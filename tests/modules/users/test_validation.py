import pytest
from apiflask import APIFlask

from dev_kit.database.extensions import db
from dev_kit.modules.users.models import Base
from dev_kit.modules.users.services import UserService


def make_app(tmp_path):
    app = APIFlask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path}/v.db"
    db.init_app(app)
    with app.app_context():
        Base.metadata.create_all(db.engine)
    return app


def test_username_uniqueness_and_password_strength(tmp_path):
    app = make_app(tmp_path)
    with app.app_context():
        service = UserService(model=None, db_session=db.session)  # model unused in uniqueness/strength logic
        # Create first user
        u1 = service.pre_create_hook({"username": "john", "password": "abc12345"})
        assert "password_hash" in u1
        # Simulate persistence
        from dev_kit.modules.users.models import User
        user = User(username="john", password_hash=u1["password_hash"])  # type: ignore
        db.session.add(user)
        db.session.commit()

        # Duplicate username
        with pytest.raises(Exception):
            service.pre_create_hook({"username": "john", "password": "def12345"})

        # Weak password
        with pytest.raises(Exception):
            service.pre_create_hook({"username": "jane", "password": "short"})
