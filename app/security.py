import os
from datetime import datetime, timedelta, timezone
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

bearer_scheme = HTTPBearer()


if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET est manquant. Vérifie le fichier .env."
    )


def creer_token(sujet: str) -> str:
    maintenant = datetime.now(timezone.utc)

    contenu = {
        "sub": sujet,
        "iat": maintenant,
        "exp": maintenant + timedelta(
            minutes=JWT_EXPIRE_MINUTES
        ),
    }

    return jwt.encode(
        contenu,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def verifier_token(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    )
) -> dict:
    try:
        return jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton expiré"
        )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton invalide"
        )