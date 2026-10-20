"""Aplicación FastAPI de LostVault Claims API."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app import service
from app.auth import AuthenticatedUser, current_user
from app.config import cors_origins, jwt_secret
from app.errors import ApiError, api_error_handler
from app.models import Claim, Problem
from app.store import ClaimStore


@asynccontextmanager
async def lifespan(_app: FastAPI):
    jwt_secret()  # falla al arrancar si falta JWT_SECRET
    yield


def create_app(store: ClaimStore | None = None) -> FastAPI:
    app = FastAPI(
        title="LostVault Claims API",
        version="1.0.0",
        description=(
            "Frontera HTTP para reclamar un objeto perdido. "
            "Implementa el contrato docs/contracts/lostvault-api.yaml."
        ),
        lifespan=lifespan,
    )
    app.state.store = store if store is not None else ClaimStore()
    app.add_exception_handler(ApiError, api_error_handler)

    origins = cors_origins()
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_methods=["POST", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
            expose_headers=["Idempotent-Replayed"],
        )

    @app.get("/health", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/v1/objects/{objectId}/claims",
        operation_id="createClaim",
        summary="Solicita la reclamación de un objeto disponible.",
        status_code=201,
        response_model=Claim,
        responses={
            200: {
                "model": Claim,
                "description": "El objeto ya estaba reclamado por este mismo usuario.",
            },
            400: {"model": Problem, "description": "Idempotency-Key inválida."},
            401: {"model": Problem, "description": "No existe una sesión autenticada."},
            404: {"model": Problem, "description": "El objeto solicitado no existe."},
            409: {"model": Problem, "description": "El objeto ya fue reclamado."},
            422: {
                "model": Problem,
                "description": "Identidad no verificada o Idempotency-Key reutilizada.",
            },
        },
    )
    def create_claim(
        objectId: str,
        request: Request,
        response: Response,
        user: AuthenticatedUser = Depends(current_user),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> Claim:
        outcome = service.create_claim(
            request.app.state.store, user, objectId, idempotency_key
        )
        response.status_code = outcome.status_code
        if outcome.replayed:
            response.headers["Idempotent-Replayed"] = "true"
        return outcome.claim

    return app


app = create_app()
