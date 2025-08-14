import os
import click

from dev_kit.database.extensions import db
from dev_kit.modules.users.bootstrap import seed_default_auth
from apiflask import APIFlask


def build_app() -> APIFlask:
    app = APIFlask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///devkit.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    # Ensure users tables exist for seeding in simple environments
    from dev_kit.modules.users.models import Base as UsersBase
    with app.app_context():
        UsersBase.metadata.create_all(db.engine)
    return app


@click.command(name="dev-kit-seed-auth")
@click.option("--admin-username", default=lambda: os.getenv("DEVKIT_ADMIN_USERNAME", "admin"), help="Admin username")
@click.option("--admin-password", default=lambda: os.getenv("DEVKIT_ADMIN_PASSWORD", "change-me"), help="Admin password")
def main(admin_username: str, admin_password: str):
    """Seed default auth data (roles, permissions, admin user)."""
    app = build_app()
    with app.app_context():
        res = seed_default_auth(db.session, admin_username=admin_username, admin_password=admin_password)
        click.echo(f"Seed completed: {res}")


if __name__ == "__main__":
    main()
