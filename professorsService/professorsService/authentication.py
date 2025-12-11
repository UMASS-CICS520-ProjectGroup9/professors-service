from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError


@dataclass
class ExternalJWTUser:
    """
    Lightweight user representation that mirrors the data encoded
    by the auth service without requiring a local User record.
    """

    id: int
    email: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None

    @property
    def is_authenticated(self) -> bool:  # pragma: no cover - simple property
        return True

    def is_anonymous(self) -> bool:  # pragma: no cover - simple property
        return False

    def __str__(self) -> str:  # pragma: no cover
        return f"ExternalJWTUser(id={self.id}, email={self.email}, username={self.username}, role={self.role})"


class ExternalJWTAuthentication(BaseAuthentication):
    """
    Authenticate requests using the JWTs issued by the user-auth service.
    The token is decoded locally with the shared signing key, so no
    additional network round-trip is required.
    """

    keyword = "bearer"

    def __init__(self) -> None:
        signing_key = settings.SIMPLE_JWT.get("SIGNING_KEY", settings.SECRET_KEY)
        algorithm = settings.SIMPLE_JWT.get("ALGORITHM", "HS256")
        self.token_backend = TokenBackend(algorithm=algorithm, signing_key=signing_key)

    def authenticate(self, request: Request) -> Optional[Tuple[ExternalJWTUser, dict]]:
        auth_header = request.headers.get("Authorization")
        print("53-auth_header: ", auth_header)
        if not auth_header:
            return None

        try:
            scheme, token = auth_header.split()
        except ValueError as exc:
            raise AuthenticationFailed("Invalid Authorization header") from exc

        if scheme.lower() != self.keyword:
            return None

        payload = self._decode_token(token)
        print("payload: ",payload)
        raw_user_id = payload.get("user_id")
        if raw_user_id is None:
            raise AuthenticationFailed("Token payload missing user_id")

        try:
            user_id = int(raw_user_id)
        except (TypeError, ValueError) as exc:
            raise AuthenticationFailed("Invalid user_id in token") from exc

        user = ExternalJWTUser(
            id=user_id,
            email=payload.get("email"),
            username=payload.get("username"),
            role=payload.get("role")
        )
        print("user: ", user)
        return (user, payload)

    def _decode_token(self, token: str) -> dict:
        try:
            return self.token_backend.decode(token, verify=True)
        except TokenBackendError as exc:
            raise AuthenticationFailed("Invalid or expired token") from exc
