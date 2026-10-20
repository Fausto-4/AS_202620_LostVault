"""Configuración leída de variables de entorno."""

import os


def jwt_secret() -> str:
    secret = os.environ.get("JWT_SECRET", "")
    if not secret:
        raise RuntimeError(
            "JWT_SECRET no está configurado. Define una cadena larga y aleatoria."
        )
    return secret


def jwt_algorithm() -> str:
    return os.environ.get("JWT_ALGORITHM", "HS256")


def verified_email_domains() -> set[str]:
    """Dominios de correo cuya identidad se considera verificada."""
    raw = os.environ.get("VERIFIED_EMAIL_DOMAINS", "utb.edu.co")
    return {d.strip().lower() for d in raw.split(",") if d.strip()}


def cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "")
    return [o.strip() for o in raw.split(",") if o.strip()]
