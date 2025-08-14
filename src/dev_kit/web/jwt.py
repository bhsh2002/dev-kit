from __future__ import annotations

from typing import Optional

from flask import jsonify
from flask_jwt_extended import JWTManager


class SimpleTokenBlocklist:
    """A simple in-memory token blocklist for demo/dev.

    For production, replace with a persistent store (e.g., Redis) and TTLs.
    """

    def __init__(self):
        self._revoked_jtis: set[str] = set()

    def add(self, jti: str) -> None:
        if jti:
            self._revoked_jtis.add(jti)

    def is_revoked(self, jti: Optional[str]) -> bool:
        return bool(jti) and jti in self._revoked_jtis


# A default singleton blocklist usable by apps that don't inject one
default_blocklist = SimpleTokenBlocklist()


def configure_jwt(jwt: JWTManager, blocklist: SimpleTokenBlocklist | None = None) -> None:
    """Register standard JWT callbacks including blocklist and error handlers.

    Call this after creating JWTManager(app). Ensure app config for cookies/CSRF is set separately.
    """
    blocklist = blocklist or default_blocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(_jwt_header, jwt_payload):  # type: ignore[override]
        jti = jwt_payload.get("jti")
        return blocklist.is_revoked(jti)

    @jwt.revoked_token_loader
    def revoked_token_callback(_jwt_header, _jwt_payload):  # type: ignore[override]
        return jsonify({"message": "Token has been revoked", "error_code": "TOKEN_REVOKED"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):  # type: ignore[override]
        return jsonify({"message": "Token has expired", "error_code": "TOKEN_EXPIRED"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):  # type: ignore[override]
        return jsonify({"message": f"Invalid token: {reason}", "error_code": "INVALID_TOKEN"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(reason):  # type: ignore[override]
        return jsonify({"message": f"Missing authorization: {reason}", "error_code": "AUTH_REQUIRED"}), 401
