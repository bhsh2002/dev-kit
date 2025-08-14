# tests/web/test_routing.py
import pytest
from apiflask import APIFlask, APIBlueprint
from flask_jwt_extended import JWTManager, create_access_token

# Import library components
from dev_kit.database.extensions import db
from dev_kit.services import BaseService
from dev_kit.web.routing import register_crud_routes
from dev_kit.web.schemas import create_crud_schemas

# Import test helpers
# from tests.helpers import ProductModel


@pytest.fixture
def app(db_session):
    """
    Creates a full Flask app instance for each test, ensuring isolation.
    Relies on the db_session fixture from conftest.py for database management.
    """
    app = APIFlask(__name__)
    app.config["TESTING"] = True
    # The db_session fixture manages the connection, so we don't need a DB URI here.
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///:memory:"  # Still needed for SQLAlchemy setup
    )
    app.config["JWT_SECRET_KEY"] = "end-to-end-secret-key"

    db.init_app(app)
    JWTManager(app)

    product_bp = APIBlueprint("products", __name__, url_prefix="/products")

    # The service must use the specific session created for this test
    test_service = BaseService(model=ProductModel, db_session=db_session)
    test_schemas = create_crud_schemas(ProductModel)

    # register_crud_routes(
    #     bp=product_bp,
    #     service=test_service,
    #     schemas=test_schemas,
    #     entity_name="product",
    #     id_field="uuid",
    # )
    # app.register_blueprint(product_bp)

    # The 'tables' fixture from conftest has already created the tables.
    # We just need the app context.
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Creates JWT auth headers with full permissions."""
    with app.app_context():
        claims = {"permissions": ["create:product", "update:product", "delete:product"]}
        access_token = create_access_token(
            identity="test-user", additional_claims=claims
        )
    return {"Authorization": f"Bearer {access_token}"}


# --- End-to-End Tests ---
# def test_create_and_get_product(client, auth_headers):
#     """Tests POST to create a product and then GET to retrieve it."""
#     response = client.post(
#         "/products/",
#         json={"name": "E2E Test Product", "price": 199.99},
#         headers=auth_headers,
#     )
#     assert response.status_code == 201
#     assert response.json["name"] == "E2E Test Product"
#     product_uuid = response.json["uuid"]

#     response = client.get(f"/products/{product_uuid}", headers=auth_headers)
#     assert response.status_code == 200
#     assert response.json["name"] == "E2E Test Product"


# def test_list_products(app, client, auth_headers, db_session):
#     """Tests GET to list all products."""
#     # Create some data first within the test's own session
#     service = BaseService(model=ProductModel, db_session=db_session)
#     service.create({"name": "Product A", "price": 10})
#     service.create({"name": "Product B", "price": 20})

#     response = client.get("/products/", headers=auth_headers)
#     assert response.status_code == 200
#     assert response.json["pagination"]["total"] == 2


# def test_permission_denied_for_create(app, client):
#     """Tests that a user without permissions gets a 403 error."""
#     with app.app_context():
#         access_token = create_access_token(identity="no-perms-user")
#     headers = {"Authorization": f"Bearer {access_token}"}

#     response = client.post(
#         "/products/",
#         json={"name": "Illegal Product", "price": 99},
#         headers=headers,
#     )
#     assert response.status_code == 403
