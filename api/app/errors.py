"""Errores de la API con el formato Problem {code, message} del contrato."""

from fastapi import Request
from fastapi.responses import JSONResponse

from app.models import ProblemCode


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        code: ProblemCode,
        message: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.headers = headers


async def api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
        headers=exc.headers,
    )
