import os
from apiflask import APIFlask
from click.testing import CliRunner

from dev_kit.database.extensions import db
from dev_kit.modules.users.bootstrap import seed_default_auth
from dev_kit.modules.users.cli import main as cli_main
from dev_kit.modules.users.models import Base, User, Role, Permission


def test_seed_default_auth_idempotent(tmp_path):
    app = APIFlask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path}/seed.db"
    db.init_app(app)
    with app.app_context():
        Base.metadata.create_all(db.engine)
        # First seed
        res1 = seed_default_auth(db.session, admin_username="admin", admin_password="pw")
        # Second seed
        res2 = seed_default_auth(db.session, admin_username="admin", admin_password="pw")

        assert res1["admin_role_id"] == res2["admin_role_id"]
        # Permissions should exist
        assert db.session.query(Permission).count() >= 10
        # Admin role exists
        assert db.session.query(Role).filter_by(name="admin").first() is not None
        # Admin user exists
        assert db.session.query(User).filter_by(username="admin").first() is not None

    # Smoke test CLI
    runner = CliRunner()
    result = runner.invoke(cli_main, ["--admin-username", "admin", "--admin-password", "pw"])
    assert result.exit_code == 0
