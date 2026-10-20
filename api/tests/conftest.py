import os
import time

import jwt
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("JWT_SECRET", "secreto-de-pruebas-suficientemente-largo")

from app.main import create_app  # noqa: E402
from app.store import ClaimStore, LostObject  # noqa: E402


class FakeClock:
    def __init__(self) -> None:
        self.now = time.time()

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def client(clock: FakeClock) -> TestClient:
    store = ClaimStore(
        objects=[LostObject("1", "Termo negro"), LostObject("2", "Carné")],
        clock=clock,
    )
    with TestClient(create_app(store)) as c:
        yield c


def make_token(sub: str = "student-42", email: str | None = "estudiante@utb.edu.co") -> str:
    payload: dict[str, object] = {"sub": sub, "exp": int(time.time()) + 3600}
    if email is not None:
        payload["email"] = email
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")


def auth(token: str | None = None) -> dict[str, str]:
    return {"Authorization": f"Bearer {token or make_token()}"}
