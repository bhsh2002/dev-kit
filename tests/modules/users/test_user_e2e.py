import pytest
from apiflask import APIFlask
from flask_jwt_extended import JWTManager

from dev_kit.database.extensions import db
from dev_kit.modules.users.models import Base, User, Role
from dev_kit.modules.users.routes import auth_bp, users_bp, roles_bp


@pytest.fixture
def app():
    app = APIFlask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret"

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)

    with app.app_context():
        # Create tables for users/roles/permissions
        Base.metadata.create_all(db.engine)
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def test_login_flow(client):
    # Arrange: create a user directly in the database
    with client.application.app_context():
        session = db.session
        user = User(username="alice")
        user.set_password("password123")
        session.add(user)
        session.commit()

    # Act: login
    resp = client.post("/auth/login", json={"username": "alice", "password": "password123"})

    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data
    assert data["user"]["username"] == "alice"


def test_assign_and_list_roles(client):
    with client.application.app_context():
        session = db.session
        # Create user and role
        user = User(username="bob")
        user.set_password("pw")
        session.add(user)
        role = Role(name="admin", display_name="Admin", description="Administrator", is_system_role=True)
        session.add(role)
        session.commit()
        user_uuid = str(user.uuid)
        role_id = role.id

    # Need auth header
    login = client.post("/auth/login", json={"username": "bob", "password": "pw"})
    token = login.get_json()["access_token"]
    # elevate permissions for role ops
    from flask_jwt_extended import create_access_token
    token = create_access_token(identity=user_uuid, additional_claims={
        "user_id": 1,
        "permissions": [
            "assign_role:user",
            "read_roles:user",
            "revoke_role:user",
        ],
        "is_super_admin": True,
    })
    headers = {"Authorization": f"Bearer {token}"}

    # Assign role
    assign_resp = client.post(f"/roles/users/{user_uuid}", json={"role_id": role_id}, headers=headers)
    assert assign_resp.status_code == 200
    assert assign_resp.get_json()["message"] == "Role assigned successfully"

    # List roles for user
    list_resp = client.get(f"/roles/users/{user_uuid}", headers=headers)
    assert list_resp.status_code == 200
    roles = list_resp.get_json()
    assert isinstance(roles, list)
    assert any(r.get("name") == "admin" for r in roles)
