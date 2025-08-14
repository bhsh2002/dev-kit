import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apiflask.fields import String

# Import the shared Base and models from our helper file
from dev_kit.modules.users.models import Base
from dev_kit.database.repository import BaseRepository
from dev_kit.services import BaseService
from dev_kit.web.schemas import create_crud_schemas
from dev_kit.modules.users.models import User


# --- بداية الكود الموجود حالياً ---
@pytest.fixture(scope="session")
def engine():
    """Creates a single in-memory SQLite engine for the whole test session."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="session")
def tables(engine):
    """Creates all tables in the engine once per session."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    """Provides a clean session for each test but DOES NOT manage transactions."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# --- نهاية الكود الموجود حالياً ---


# --- Fixtures لوحدة المنتجات (موجودة حالياً) ---
# @pytest.fixture
# def product_repo(db_session):
#     return BaseRepository(model=ProductModel, db_session=db_session)


# @pytest.fixture(scope="session")
# def product_schemas():
#     return create_crud_schemas(ProductModel)


# --- Fixtures جديدة مقترحة لوحدة المستخدمين ---
@pytest.fixture(scope="session")
def user_schemas():
    """
    Fixture لإنشاء مخططات المستخدمين مرة واحدة لكل جلسة اختبار.
    نستبعد حقل كلمة المرور من المخرجات لزيادة الأمان.
    """
    return create_crud_schemas(
        User,
        exclude_from_input=["password_hash"],
        custom_fields={"password": String(required=True, load_only=True)},
    )


@pytest.fixture
def user_service(db_session):
    """
    Fixture لإنشاء خدمة المستخدمين مع كل اختبار.
    """
    # في المستقبل، إذا احتجت منطقاً مخصصاً (مثل تشفير كلمة المرور)،
    # يمكنك إنشاء فئة UserService(BaseService) وتمريرها هنا.
    return BaseService(model=User, db_session=db_session)
