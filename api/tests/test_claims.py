"""Pruebas de la operación createClaim contra el contrato OpenAPI."""

import os
import time

import jwt

from tests.conftest import auth, make_token

PROBLEM_CODES = {
    "UNAUTHENTICATED",
    "OBJECT_NOT_FOUND",
    "OBJECT_ALREADY_CLAIMED",
    "IDENTITY_NOT_VERIFIED",
    "IDEMPOTENCY_KEY_REUSED",
    "INVALID_IDEMPOTENCY_KEY",
}


def assert_claim(body: dict, object_id: str = "1", user_id: str = "student-42") -> None:
    # additionalProperties: false; verified es const true
    assert body == {"objectId": object_id, "userId": user_id, "verified": True}


def assert_problem(response, status: int, code: str) -> None:
    assert response.status_code == status
    body = response.json()
    assert set(body) == {"code", "message"}
    assert body["code"] in PROBLEM_CODES
    assert body["code"] == code
    assert isinstance(body["message"], str) and body["message"]


# --- 201 ---------------------------------------------------------------

def test_claim_created(client):
    r = client.post("/v1/objects/1/claims", headers=auth())
    assert r.status_code == 201
    assert_claim(r.json())
    assert "idempotent-replayed" not in r.headers


# --- 401 ---------------------------------------------------------------

def test_no_token_is_401(client):
    r = client.post("/v1/objects/1/claims")
    assert_problem(r, 401, "UNAUTHENTICATED")


def test_garbage_token_is_401(client):
    r = client.post("/v1/objects/1/claims", headers={"Authorization": "Bearer nope"})
    assert_problem(r, 401, "UNAUTHENTICATED")


def test_expired_token_is_401(client):
    expired = jwt.encode(
        {"sub": "student-42", "exp": int(time.time()) - 10},
        os.environ["JWT_SECRET"],
        algorithm="HS256",
    )
    r = client.post("/v1/objects/1/claims", headers=auth(expired))
    assert_problem(r, 401, "UNAUTHENTICATED")


def test_token_signed_with_other_secret_is_401(client):
    forged = jwt.encode(
        {"sub": "student-42", "exp": int(time.time()) + 3600},
        "otro-secreto-distinto-de-32-bytes-o-mas",
        algorithm="HS256",
    )
    r = client.post("/v1/objects/1/claims", headers=auth(forged))
    assert_problem(r, 401, "UNAUTHENTICATED")


def test_unauthenticated_does_not_claim_object(client):
    client.post("/v1/objects/1/claims")
    r = client.post("/v1/objects/1/claims", headers=auth())
    assert r.status_code == 201


# --- 404 ---------------------------------------------------------------

def test_unknown_object_is_404(client):
    r = client.post("/v1/objects/999/claims", headers=auth())
    assert_problem(r, 404, "OBJECT_NOT_FOUND")


# --- 409 / 200 ---------------------------------------------------------

def test_already_claimed_by_other_user_is_409(client):
    client.post("/v1/objects/1/claims", headers=auth())
    other = make_token(sub="student-7", email="otro@utb.edu.co")
    r = client.post("/v1/objects/1/claims", headers=auth(other))
    assert_problem(r, 409, "OBJECT_ALREADY_CLAIMED")


def test_repeat_by_same_user_without_key_is_200(client):
    first = client.post("/v1/objects/1/claims", headers=auth())
    again = client.post("/v1/objects/1/claims", headers=auth())
    assert first.status_code == 201
    assert again.status_code == 200
    assert_claim(again.json())


# --- 422 identidad -----------------------------------------------------

def test_unverified_identity_is_422_and_object_stays_available(client):
    outsider = make_token(sub="intruso", email="intruso@gmail.com")
    r = client.post("/v1/objects/1/claims", headers=auth(outsider))
    assert_problem(r, 422, "IDENTITY_NOT_VERIFIED")

    ok = client.post("/v1/objects/1/claims", headers=auth())
    assert ok.status_code == 201


def test_token_without_email_is_422(client):
    r = client.post("/v1/objects/1/claims", headers=auth(make_token(email=None)))
    assert_problem(r, 422, "IDENTITY_NOT_VERIFIED")


# --- Idempotencia ------------------------------------------------------

def test_replay_with_same_key_returns_201_and_header(client):
    h = {**auth(), "Idempotency-Key": "abc-123"}
    first = client.post("/v1/objects/1/claims", headers=h)
    replay = client.post("/v1/objects/1/claims", headers=h)
    assert first.status_code == 201
    assert "idempotent-replayed" not in first.headers
    assert replay.status_code == 201
    assert replay.headers["Idempotent-Replayed"] == "true"
    assert replay.json() == first.json()


def test_key_reused_for_other_object_is_422(client):
    h = {**auth(), "Idempotency-Key": "abc-123"}
    client.post("/v1/objects/1/claims", headers=h)
    r = client.post("/v1/objects/2/claims", headers=h)
    assert_problem(r, 422, "IDEMPOTENCY_KEY_REUSED")


def test_keys_are_scoped_per_user(client):
    key = {"Idempotency-Key": "misma-clave"}
    client.post("/v1/objects/1/claims", headers={**auth(), **key})
    other = make_token(sub="student-7", email="otro@utb.edu.co")
    r = client.post("/v1/objects/2/claims", headers={**auth(other), **key})
    assert r.status_code == 201
    assert_claim(r.json(), object_id="2", user_id="student-7")


def test_key_expires_after_24h(client, clock):
    h = {**auth(), "Idempotency-Key": "abc-123"}
    client.post("/v1/objects/1/claims", headers=h)
    clock.now += 24 * 3600 + 1
    r = client.post("/v1/objects/2/claims", headers=h)
    assert r.status_code == 201  # la clave ya no está vigente


def test_empty_key_is_400(client):
    r = client.post("/v1/objects/1/claims", headers={**auth(), "Idempotency-Key": ""})
    assert_problem(r, 400, "INVALID_IDEMPOTENCY_KEY")


def test_too_long_key_is_400(client):
    r = client.post(
        "/v1/objects/1/claims",
        headers={**auth(), "Idempotency-Key": "x" * 256},
    )
    assert_problem(r, 400, "INVALID_IDEMPOTENCY_KEY")


def test_max_length_key_is_accepted(client):
    r = client.post(
        "/v1/objects/1/claims",
        headers={**auth(), "Idempotency-Key": "x" * 255},
    )
    assert r.status_code == 201


def test_invalid_key_does_not_claim_object(client):
    client.post("/v1/objects/1/claims", headers={**auth(), "Idempotency-Key": ""})
    r = client.post("/v1/objects/1/claims", headers=auth())
    assert r.status_code == 201


# --- Extra -------------------------------------------------------------

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
