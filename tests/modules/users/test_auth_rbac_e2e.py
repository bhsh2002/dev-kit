import pytest
from apiflask import APIFlask
from flask_jwt_extended import JWTManager, create_access_token

from dev_kit.database.extensions import db
from dev_kit.modules.users.models import Base, User, Role, Permission
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
        Base.metadata.create_all(db.engine)
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def create_jwt(app, claims=None):
    with app.app_context():
        return create_access_token(identity="fake-uuid", additional_claims=claims or {})


def test_whoami_requires_auth(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_login_sets_tokens_and_whoami(client):
    with client.application.app_context():
        u = User(username="carol")
        u.set_password("pw")
        db.session.add(u)
        db.session.commit()

    login = client.post("/auth/login", json={"username": "carol", "password": "pw"})
    assert login.status_code == 200
    data = login.get_json()
    assert data.get("access_token") and data.get("refresh_token")

    # Use access token header
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # add elevated permissions to bypass permission_required in tests
    with client.application.app_context():
        from flask_jwt_extended import create_access_token
        # get user uuid via whoami first
        me = client.get("/auth/me", headers=headers)
        assert me.status_code == 200
        user_uuid = me.get_json()["uuid"]
        token = create_access_token(identity=user_uuid, additional_claims={
        "user_id": 1,
        "permissions": [
            "assign_role:user",
            "read_roles:user",
            "assign_permission:role",
            "read_permissions:role",
            "revoke_permission:role",
            "revoke_role:user",
        ],
        "is_super_admin": True,
        })
        headers = {"Authorization": f"Bearer {token}"}
        me = client.get("/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.get_json()["username"] == "carol"


def test_change_password_and_relogin(client):
    with client.application.app_context():
        u = User(username="dave")
        u.set_password("old")
        db.session.add(u)
        db.session.commit()

    # login
    login = client.post("/auth/login", json={"username": "dave", "password": "old"})
    token = login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # change password
    resp = client.post(
        "/users/change-password",
        json={"current_password": "old", "new_password": "new12345"},
        headers=headers,
    )
    assert resp.status_code == 200

    # re-login with new password
    relogin = client.post("/auth/login", json={"username": "dave", "password": "new12345"})
    assert relogin.status_code == 200


def test_role_permission_assignment_flow(client):
    with client.application.app_context():
        user = User(username="eve")
        user.set_password("pw")
        db.session.add(user)
        role = Role(name="manager", display_name="Manager")
        perm = Permission(name="create:user")
        db.session.add_all([role, perm])
        db.session.commit()
        user_uuid = str(user.uuid)
        role_id = role.id
        perm_id = perm.id

    # login to get JWT
    login = client.post("/auth/login", json={"username": "eve", "password": "pw"})
    # craft headers with elevated claims for this user
    with client.application.app_context():
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=user_uuid, additional_claims={
            "user_id": 1,
            "permissions": [
                "assign_role:user",
                "read_roles:user",
                "assign_permission:role",
                "read_permissions:role",
                "revoke_permission:role",
                "revoke_role:user",
            ],
            "is_super_admin": True,
        })
        headers = {"Authorization": f"Bearer {token}"}

    # assign role to user
    ar = client.post(f"/roles/users/{user_uuid}", json={"role_id": role_id}, headers=headers)
    assert ar.status_code == 200

    # assign permission to role
    pr = client.post(f"/roles/{role_id}/permissions", json={"permission_id": perm_id}, headers=headers)
    assert pr.status_code == 200

    # list role permissions
    lp = client.get(f"/roles/{role_id}/permissions", headers=headers)
    assert lp.status_code == 200
    assert any(p.get("name") == "create:user" for p in lp.get_json())

    # revoke permission
    rr = client.delete(f"/roles/{role_id}/permissions", json={"permission_id": perm_id}, headers=headers)
    assert rr.status_code == 200

    # revoke role from user
    rv = client.delete(f"/roles/users/{user_uuid}", json={"role_id": role_id}, headers=headers)
    assert rv.status_code == 200
