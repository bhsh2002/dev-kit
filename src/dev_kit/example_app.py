from apiflask import APIFlask
from flask_jwt_extended import JWTManager

from dev_kit.database.extensions import db
from dev_kit.web.jwt import configure_jwt
from dev_kit.web.decorators import setup_rate_limiting
from dev_kit.modules.users.routes import auth_bp, users_bp, roles_bp, permissions_bp


def create_app() -> APIFlask:
    app = APIFlask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite:///devkit_example.db",
        JWT_SECRET_KEY="change-me",
        JWT_TOKEN_LOCATION=["headers", "cookies"],
        JWT_COOKIE_SECURE=False,
        JWT_COOKIE_CSRF_PROTECT=True,
        JWT_COOKIE_SAMESITE="Lax",
        # Dev-only: in-memory rate limit storage to avoid warnings
        RATELIMIT_STORAGE_URI="memory://",
    )

    db.init_app(app)

    # JWT & rate limiting
    jwt = JWTManager(app)
    configure_jwt(jwt)
    setup_rate_limiting(app, default_rate="200/minute")

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(roles_bp)
    app.register_blueprint(permissions_bp)

    with app.app_context():
        # For demo only: create tables
        from dev_kit.modules.users.models import Base

        Base.metadata.create_all(db.engine)

    return app


app = create_app()

if __name__ == "__main__":  # pragma: no cover
    app.run(host="127.0.0.1", port=5000, debug=True)
