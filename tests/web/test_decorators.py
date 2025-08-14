# tests/web/test_decorators.py

import pytest
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from unittest.mock import patch

from dev_kit.web.decorators import permission_required, log_activity
from dev_kit.exceptions import PermissionDeniedError


# --- Test Setup ---
@pytest.fixture
def app():
    """Creates a minimal Flask app for testing decorators."""
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "super-secret-key-for-testing"
    JWTManager(app)

    # A simple error handler to return JSON for our custom exception
    @app.errorhandler(PermissionDeniedError)
    def handle_permission_denied(error):
        return jsonify(error.to_dict()), error.status_code

    # Create a protected route for testing
    @app.route("/protected")
    @permission_required("read:data")
    def protected_route():
        return jsonify(message="success"), 200

    # Create another route for testing the logger
    @app.route("/logged")
    @log_activity
    def logged_route():
        return jsonify(message="logged"), 200

    return app


@pytest.fixture
def client(app):
    """Provides a test client for the Flask app."""
    return app.test_client()


# --- Tests for permission_required ---
def test_permission_denied_without_token(client):
    """Tests that accessing a protected route without a token fails."""
    response = client.get("/protected")
    assert response.status_code == 401  # Unauthorized from flask-jwt-extended


def test_permission_denied_with_wrong_permission(app, client):
    """Tests that a token with incorrect permissions is denied."""
    with app.app_context():
        # Create a token with a different permission
        access_token = create_access_token(
            identity="testuser", additional_claims={"permissions": ["write:data"]}
        )
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get("/protected", headers=headers)
    assert response.status_code == 403  # Forbidden
    assert response.json["error_code"] == "PERMISSION_DENIED"


def test_permission_granted_with_correct_permission(app, client):
    """Tests that a token with the correct permission is allowed."""
    with app.app_context():
        access_token = create_access_token(
            identity="testuser", additional_claims={"permissions": ["read:data"]}
        )
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get("/protected", headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "success"


def test_permission_granted_for_super_admin(app, client):
    """Tests that a super admin can bypass the permission check."""
    with app.app_context():
        # Token has no 'permissions' list, but has 'is_super_admin'
        access_token = create_access_token(
            identity="admin", additional_claims={"is_super_admin": True}
        )
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get("/protected", headers=headers)
    assert response.status_code == 200


# --- Test for log_activity ---
def test_log_activity_decorator(app, client):
    """Tests that the log_activity decorator calls the logger."""
    with app.app_context():
        # Mock the logger object on current_app
        with patch("dev_kit.web.decorators.current_app.logger") as mock_logger:
            client.get("/logged")
            # Assert that logger.info was called at least twice (entry and exit)
            assert mock_logger.info.call_count >= 2
