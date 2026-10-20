"""Esquemas definidos en el contrato OpenAPI (components/schemas)."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    objectId: str
    userId: str
    verified: Literal[True] = True


ProblemCode = Literal[
    "UNAUTHENTICATED",
    "OBJECT_NOT_FOUND",
    "OBJECT_ALREADY_CLAIMED",
    "IDENTITY_NOT_VERIFIED",
    "IDEMPOTENCY_KEY_REUSED",
    "INVALID_IDEMPOTENCY_KEY",
]


class Problem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: ProblemCode
    message: str
