"""Genera un JWT de prueba. Uso:

    JWT_SECRET=... python scripts/make_token.py --sub student-42 --email estudiante@utb.edu.co
"""

import argparse
import os
import sys
import time

import jwt


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera un JWT para LostVault API")
    parser.add_argument("--sub", required=True, help="ID del usuario (claim sub)")
    parser.add_argument("--email", default=None, help="Correo del usuario")
    parser.add_argument("--hours", type=float, default=1.0, help="Horas de vigencia")
    args = parser.parse_args()

    secret = os.environ.get("JWT_SECRET")
    if not secret:
        print("Define JWT_SECRET en el entorno.", file=sys.stderr)
        return 1

    payload: dict[str, object] = {
        "sub": args.sub,
        "exp": int(time.time() + args.hours * 3600),
    }
    if args.email:
        payload["email"] = args.email

    print(jwt.encode(payload, secret, algorithm=os.environ.get("JWT_ALGORITHM", "HS256")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
