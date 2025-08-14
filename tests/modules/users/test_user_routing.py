# import pytest
# from apiflask import APIFlask, APIBlueprint
# from flask_jwt_extended import create_access_token, JWTManager

# from dev_kit.web.routing import register_crud_routes
# from dev_kit.services import BaseService
# from tests.helpers import UserModel  # استيراد النموذج الخاص بالاختبار

# # Fixtures `app`, `client`, `db_session`, `user_schemas`, `user_service`
# # يتم توفيرها من ملفات conftest.py و ملف الإعداد أدناه.


# @pytest.fixture
# def app_with_users_module(db_session, user_schemas, user_service):
#     """
#     يقوم بإنشاء تطبيق Flask مع تسجيل وحدة المستخدمين فقط للاختبار المعزول.
#     هذا يتبع نمط الإعداد في tests/web/test_routing.py [cite: 1146-1148].
#     """
#     app = APIFlask("test_users_app")
#     app.config["TESTING"] = True
#     app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
#     app.config["JWT_SECRET_KEY"] = "jwt-secret-for-users"
#     JWTManager(app)

#     # إنشاء وتسجيل Blueprint
#     users_bp = APIBlueprint("users", __name__, url_prefix="/users")
#     register_crud_routes(
#         bp=users_bp,
#         service=user_service,
#         schemas=user_schemas,
#         entity_name="user",
#         id_field="id",
#     )
#     app.register_blueprint(users_bp)

#     with app.app_context():
#         yield app


# @pytest.fixture
# def client(app_with_users_module):
#     """يوفر Test Client للتطبيق."""
#     return app_with_users_module.test_client()


# @pytest.fixture
# def auth_headers(app_with_users_module):
#     """ينشئ Headers للمصادقة مع صلاحيات كاملة."""
#     with app_with_users_module.app_context():
#         # في تطبيق حقيقي، الصلاحيات ستكون أكثر تحديداً
#         claims = {"permissions": ["create:user", "update:user", "delete:user"]}
#         access_token = create_access_token(identity=1, additional_claims=claims)
#     return {"Authorization": f"Bearer {access_token}"}


# def test_create_and_get_user(client, auth_headers):
#     """
#     يختبر إنشاء مستخدم جديد عبر POST ثم جلبه عبر GET.
#     """
#     # Action: Create User
#     create_response = client.post(
#         "/users/",
#         json={"username": "e2e_user", "password": "a_secure_password"},
#         headers=auth_headers,
#     )

#     # Assert: Creation
#     assert create_response.status_code == 201
#     assert create_response.json["username"] == "e2e_user"
#     assert "id" in create_response.json
#     assert (
#         "password" not in create_response.json
#     )  # تحقق من أن كلمة المرور لا تعود في الاستجابة
#     user_id = create_response.json["id"]

#     # Action: Get User
#     get_response = client.get(f"/users/{user_id}", headers=auth_headers)

#     # Assert: Retrieval
#     assert get_response.status_code == 200
#     assert get_response.json["id"] == user_id
#     assert get_response.json["username"] == "e2e_user"


# def test_list_users(client, auth_headers, user_service):
#     """
#     يختبر جلب قائمة المستخدمين.
#     """
#     # Arrange: Create some users first
#     user_service.create({"username": "user1", "password": "p1"})
#     user_service.create({"username": "user2", "password": "p2"})

#     # Action
#     response = client.get("/users/", headers=auth_headers)

#     # Assert
#     assert response.status_code == 200
#     assert response.json["pagination"]["total"] == 2
#     assert len(response.json["items"]) == 2


# def test_unauthorized_access(client):
#     """
#     يختبر أن الوصول للمسارات المحمية بدون Token يرجع خطأ 401.
#     """
#     response = client.get("/users/")
#     assert response.status_code == 401  # Unauthorized

#     response = client.post("/users/")
#     assert response.status_code == 401  # Unauthorized
