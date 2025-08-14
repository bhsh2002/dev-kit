import pytest
from apiflask import APIFlask
from flask_jwt_extended import JWTManager, create_access_token

from dev_kit.database.extensions import db
from dev_kit.modules.users.models import Base, User, Role
from dev_kit.modules.users.routes import users_bp, roles_bp


@pytest.fixture
def app():
    app = APIFlask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret"

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)

    with app.app_context():
        Base.metadata.create_all(db.engine)
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def auth_header(identity: str, perms: list[str] | None = None):
    token = create_access_token(identity=identity, additional_claims={"permissions": perms or []})
    return {"Authorization": f"Bearer {token}"}


def test_assign_role_forbidden_without_permission(client):
    with client.application.app_context():
        user = User(username="nope")
        user.set_password("pw")
        db.session.add(user)
        role = Role(name="viewer", display_name="Viewer")
        db.session.add(role)
        db.session.commit()
        user_uuid = str(user.uuid)
        role_id = role.id

    # Token without required permission
    headers = auth_header(identity=user_uuid, perms=["read:user"])  # missing assign_role:user
    resp = client.post(f"/roles/users/{user_uuid}", json={"role_id": role_id}, headers=headers)
    assert resp.status_code == 403


def test_list_user_roles_forbidden_without_permission(client):
    with client.application.app_context():
        user = User(username="nope2")
        user.set_password("pw")
        db.session.add(user)
        db.session.commit()
        user_uuid = str(user.uuid)

    headers = auth_header(identity=user_uuid, perms=[])  # no perms
    resp = client.get(f"/roles/users/{user_uuid}", headers=headers)
    assert resp.status_code == 403
