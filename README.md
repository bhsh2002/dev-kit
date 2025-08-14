# Dev-Kit: إطار عمل لتسريع تطوير تطبيقات Flask

**Dev-Kit** هو إطار عمل صغير ومجموعة أدوات قوية مصممة لتسريع عملية بناء تطبيقات الويب القائمة على Flask، مع التركيز على إنشاء واجهات برمجة تطبيقات RESTful (RESTful APIs) بسرعة وكفاءة. تم بناء هذا المشروع للتخلص من الحاجة إلى كتابة الشيفرة المتكررة (boilerplate code) من خلال توفير مكونات قابلة لإعادة الاستخدام ومبنية على أفضل الممارسات في هندسة البرمجيات.

## الميزات الأساسية

*   **هيكلة منظمة**: يفرض المشروع هيكلة واضحة تفصل بين طبقة الوصول للبيانات (Repository)، منطق الأعمال (Service)، وواجهة برمجة التطبيقات (Web).
*   **مولد CRUD التلقائي**: يوفر دوال قوية لتوليد مخططات marshmallow ونقاط نهاية (endpoints) API كاملة لعمليات CRUD (الإنشاء، القراءة، التحديث، الحذف) من خلال استدعاء دالة واحدة.
*   **طبقة وصول بيانات عامة (Generic Repository)**: يتضمن `BaseRepository` الذي يغلف عمليات قاعدة البيانات الشائعة مع دعم للفلترة المتقدمة، الترتيب، وتقسيم الصفحات (pagination).
*   **طبقة خدمة مركزية (Service Layer)**: يقدم `BaseService` لإدارة منطق الأعمال وتنسيق المعاملات (transactions) بشكل آمن باستخدام Savepoints لضمان تكامل البيانات.
*   **مكونات قاعدة بيانات قابلة لإعادة الاستخدام**: يتضمن Mixins جاهزة للاستخدام مع SQLAlchemy لإضافة حقول شائعة مثل `id`, `uuid`, `created_at`, `updated_at`, و `deleted_at` (للحذف الناعم).
*   **نظام استثناءات (Exceptions) موحد**: يوفر مجموعة من الاستثناءات المخصصة التي تترجم تلقائيًا إلى استجابات خطأ JSON متسقة.
*   **أمان مدمج**: يتضمن Decorators جاهزة للتحقق من المصادقة (JWT) والصلاحيات (permissions) على مستوى كل Route.

## المتطلبات

*   Python 3.11+
*   Flask
*   SQLAlchemy & Flask-SQLAlchemy
*   APIFlask & Marshmallow-SQLAlchemy
*   Flask-JWT-Extended (JWT, CSRF, cookies)

## التثبيت

1.  تأكد من أن لديك `Poetry` مثبت.
2.  قم بتثبيت الاعتماديات من خلال جذر المشروع:
    ```bash
    poetry install
    ```

## كيفية الاستخدام

تم تصميم Dev-Kit ليكون بمثابة أساس لمشاريع Flask الجديدة. إليك دليل سريع لكيفية استخدام مكوناته الأساسية.

### 1. تعريف النماذج (Models)

استخدم الـ Mixins المتوفرة في `dev_kit.database.mixins` لتسريع عملية بناء نماذج SQLAlchemy.

**مثال: `models.py`**
```python
from dev_kit.database.extensions import db
from dev_kit.database.mixins import IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin

class Product(db.Model, IDMixin, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "products"
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
```

### 2. إنشاء الخدمة (Service)

لكل نموذج، يمكنك إنشاء خدمة ترث من `BaseService` لإدارة منطق الأعمال. في معظم الحالات، لن تحتاج إلى كتابة أي شيفرة إضافية في الخدمة للعمليات الأساسية.

**مثال: `services.py`**
```python
from dev_kit.services import BaseService
from dev_kit.database.extensions import db
from .models import Product

product_service = BaseService(model=Product, db_session=db.session)
```

### 3. إنشاء واجهة برمجة التطبيقات (API)

هذه هي الخطوة السحرية. يمكنك إنشاء API كاملة لنموذج `Product` ببضعة أسطر من الكود.

**مثال: `routes.py`**
```python
from apiflask import APIBlueprint
from dev_kit.web.schemas import create_crud_schemas
from dev_kit.web.routing import register_crud_routes
from .services import product_service
from .models import Product

# إنشاء Blueprint
product_bp = APIBlueprint('product', __name__, url_prefix='/products')

# 1. توليد جميع المخططات اللازمة تلقائيًا
schemas = create_crud_schemas(Product)

# 2. تسجيل جميع مسارات CRUD (GET, POST, PATCH, DELETE) تلقائيًا
register_crud_routes(
    bp=product_bp,
    service=product_service,
    schemas=schemas,
    entity_name='product',
    id_field='uuid' # يمكن أن تكون 'id' أو 'uuid'
)

# يمكنك الآن تسجيل الـ Blueprint في تطبيق Flask الرئيسي
# from app import app
# app.register_blueprint(product_bp)
```

بهذه الخطوات البسيطة، تم إنشاء النقاط التالية:

*   `GET /products/`: لجلب قائمة بالمنتجات مع دعم للفلترة والترتيب وتقسيم الصفحات.
*   `POST /products/`: لإنشاء منتج جديد.
*   `GET /products/{uuid}`: لجلب منتج واحد.
*   `PATCH /products/{uuid}`: لتحديث منتج موجود.
*   `DELETE /products/{uuid}`: لحذف منتج (حذف ناعم بشكل افتراضي).

### 4. استخدام الفلترة المتقدمة والترتيب المتعدد

تدعم طبقة الـ Repository الفلترة باستخدام صيغة `__`. يمكنك تمرير الفلاتر مباشرة من خلال `request.args` إلى الخدمة.

**مثال على استدعاء من خلال العميل:**
> `GET /api/products?name__ilike=book&price__in=book,pen&price__gte=15.50&sort_by=-created_at,name`

*   `name__ilike=book`: يبحث عن المنتجات التي يحتوي اسمها على "book" (غير حساس لحالة الأحرف).
*   `price__gte=15.50`: يجلب المنتجات التي سعرها أكبر من أو يساوي 15.50.
*   `price__in=book,pen`: دعم `in` كسلسلة مفصولة بفواصل.
*   `sort_by=-created_at,name`: يدعم ترتيبًا متعدد الحقول.

### 5. تخصيص الصلاحيات

يمكنك التحكم في الصلاحيات المطلوبة لكل مسار (route) عبر المعلمة `routes_config` في دالة `register_crud_routes`.

**في ملف `routes.py`:**
```python
register_crud_routes(
    # ... other params
    routes_config={
        # القيمة الافتراضية: جميع المسارات تتطلب مصادقة
        # وعمليات الإنشاء/التحديث/الحذف تتطلب صلاحيات action:entity
        # يمكنك تجاوز السلوك الافتراضي كما يلي:
        'create': {'permission': 'create:product'},
        'update': {'permission': 'update:product'},
        'delete': {'permission': 'delete:product'},
        'list': {'auth_required': True}, # يتطلب مصادقة فقط
        'get': {'auth_required': True},
    }
)
```

## تشغيل الاختبارات

المشروع يأتي مع مجموعة شاملة من الاختبارات لضمان الموثوقية. لتشغيلها:
```bash
poetry run pytest
```

## مثال تطبيق متكامل

يوجد مثال مبسط في `dev_kit/example_app.py` يوضح كيفية:

- تهيئة قاعدة البيانات وJWT وRate Limiting
- تسجيل Blueprints الخاصة بوحدة المستخدمين

تشغيله محلياً:

```bash
poetry run python -m dev_kit.example_app
```

ثم اذهب إلى `/auth/login`, `/users/`... إلخ.

### أدوات التطوير (اختياري)

إعداد pre-commit للتنسيق والفحص:

```bash
poetry run pre-commit install
```

### إعداد JWT (CSRF والـ Blocklist)

يوفر الملف `dev_kit.web.jwt` دوال مساعدة لإعداد JWT القياسي:

```python
from flask_jwt_extended import JWTManager
from dev_kit.web.jwt import configure_jwt

app.config.update(
    JWT_TOKEN_LOCATION=["headers", "cookies"],
    JWT_COOKIE_SECURE=False,  # True في الإنتاج مع HTTPS
    JWT_COOKIE_CSRF_PROTECT=True,
    JWT_ACCESS_COOKIE_NAME="access_token",
    JWT_REFRESH_COOKIE_NAME="refresh_token",
    JWT_COOKIE_SAMESITE="Lax",
)

jwt = JWTManager(app)
configure_jwt(jwt)  # تسجيل blocklist و callbacks الأساسية
```

### الحد من المعدل (Rate Limiting)

لتفعيل الحد من المعدل على التطبيق بأكمله:

```python
from dev_kit.web.decorators import setup_rate_limiting

limiter = setup_rate_limiting(app, default_rate="200/minute")
# يمكن تخصيص حدود لمسارات معينة عبر Decorators من Flask-Limiter
```

## وحدة المستخدمين (Users Module)

توفر الوحدة حزمة كاملة لإدارة المستخدمين والأدوار والصلاحيات:

- مصادقة:
  - POST `/auth/login`: تسجيل الدخول (يرجع Access/Refresh Token ويضعهما كـ Cookies).
  - GET `/auth/me`: معلومات المستخدم الحالي.
  - POST `/auth/refresh`: تحديث الـ Access Token.
  - POST `/auth/logout`: تسجيل الخروج ومسح الـ Cookies.
- إدارة المستخدم:
  - CRUD قياسي على `/users` عبر `register_crud_routes` باستخدام `uuid`.
  - POST `/users/change-password`: تغيير كلمة المرور للمستخدم الحالي.
- الأدوار والصلاحيات:
  - CRUD قياسي على `/roles` و`/permissions`.
  - POST `/roles/users/{user_uuid}`: إسناد دور لمستخدم.
  - DELETE `/roles/users/{user_uuid}`: سحب دور من مستخدم.
  - GET `/roles/users/{user_uuid}`: عرض أدوار المستخدم.
  - GET `/roles/{role_id}/permissions`: عرض صلاحيات الدور.
  - POST `/roles/{role_id}/permissions`: إسناد صلاحية لدور.
  - DELETE `/roles/{role_id}/permissions`: سحب صلاحية من دور.

الصلاحيات الافتراضية المستخدمة في الديكورات:
`assign_role:user`, `revoke_role:user`, `read_roles:user`, `assign_permission:role`, `revoke_permission:role`, `read_permissions:role`.

### التحقق من صحة كلمات المرور والأسماء الفريدة

تطبق خدمة المستخدمين قواعد قوية لكلمات المرور وتتحقق من تفرد اسم المستخدم قبل الإنشاء:

- الحد الأدنى للطول: 8 أحرف.
- يجب أن تحتوي كلمة المرور على أحرف وأرقام.
- يمنع تكرار اسم المستخدم برسالة واضحة.

### Seed القيم الافتراضية

يمكنك تهيئة بيانات بدائية (صلاحيات أساسية، دور Admin بكل الصلاحيات، ومستخدم Admin) باستخدام:

```python
from dev_kit.database.extensions import db
from dev_kit.modules.users.bootstrap import seed_default_auth

with app.app_context():
    seed_default_auth(db.session, admin_username="admin", admin_password="change-me")
```

### الترحيلات (Alembic Migrations)

تم تضمين إعداد Alembic مع ملف `alembic.ini` ومجلد `migrations/`.

- تحديد قاعدة البيانات عبر المتغير `SQLALCHEMY_DATABASE_URI`.
- توليد ترحيل جديد تلقائياً:
  ```bash
  SQLALCHEMY_DATABASE_URI=sqlite:///devkit.db alembic revision --autogenerate -m "change"
  ```
- تطبيق الترحيلات:
  ```bash
  SQLALCHEMY_DATABASE_URI=sqlite:///devkit.db alembic upgrade head
  ```
