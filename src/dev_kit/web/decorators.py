# src/dev_kit/web/decorators.py
"""
A collection of decorators for Flask routes.

These decorators provide reusable functionality such as activity logging
and permission checking for API endpoints.
"""

from functools import wraps
from flask import current_app, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from dev_kit.exceptions import PermissionDeniedError


def log_activity(f):
    """Logs the entry, exit, and errors of a function call."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_app.logger.info(
            f"Activity: Calling function {f.__name__} with args:\
              {args}, kwargs: {kwargs}"
        )
        try:
            result = f(*args, **kwargs)
            current_app.logger.info(
                f"Activity: Function {f.__name__} finished successfully."
            )
            return result
        except Exception as e:
            current_app.logger.error(
                f"Activity: Error in function {f.__name__}: {str(e)}", exc_info=True
            )
            raise

    return decorated_function


def permission_required(permission: str):
    """
    Decorator factory to ensure a user has a specific permission in their JWT.

    It checks for the presence of a valid JWT, then looks for the required
    permission within the 'permissions' claim. It also allows users with the
    'is_super_admin' claim to bypass the check.

    Args:
        permission: The name of the permission string required to access the route.

    Raises:
        PermissionDeniedError: If the user does not have the required permission.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_permissions = claims.get("permissions", [])
            is_super_admin = claims.get("is_super_admin", False)

            if not is_super_admin and permission not in user_permissions:
                raise PermissionDeniedError(
                    f"Required permission '{permission}' is missing."
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def setup_rate_limiting(app, default_rate: str = "100/minute"):
    """Attach Flask-Limiter to the app with a sane default rate.

    You can override per-route using @app.limit on blueprints or endpoints.
    """
    limiter = Limiter(get_remote_address, app=app, default_limits=[default_rate])
    return limiter
