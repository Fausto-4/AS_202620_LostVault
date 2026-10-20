"""Verificación de identidad.

Regla actual: la identidad es válida si el correo del token pertenece a un
dominio institucional configurado (VERIFIED_EMAIL_DOMAINS, por defecto
utb.edu.co). Es el punto de extensión para una verificación real.
"""

from app.auth import AuthenticatedUser
from app.config import verified_email_domains


def is_identity_verified(user: AuthenticatedUser) -> bool:
    if not user.email or "@" not in user.email:
        return False
    domain = user.email.rsplit("@", 1)[1].lower()
    return domain in verified_email_domains()
