import pytest
from dev_kit.modules.users.models import User
from dev_kit.exceptions import NotFoundError

# Fixtures `db_session` و `user_service` يتم حقنها تلقائياً من conftest.py


def test_create_user_persists_data(db_session, user_service):
    """
    يختبر أن دالة الإنشاء تقوم بحفظ البيانات بشكل دائم في قاعدة البيانات.
    هذا يتبع نفس نمط الاختبار في test_services.py[cite: 1161].
    """
    # Action
    user_data = {"username": "testuser", "password_hash": "strong_password"}
    created_user = user_service.create(user_data)

    # Assert
    assert created_user.id is not None
    assert created_user.username == "testuser"

    # للتحقق من أن البيانات موجودة بالفعل في الجلسة الحالية لقاعدة البيانات
    fetched_user = db_session.query(User).filter_by(id=created_user.id).one()
    assert fetched_user is not None
    assert fetched_user.username == "testuser"


def test_get_user_by_id(user_service):
    """
    يختبر جلب مستخدم بواسطة الـ ID الخاص به.
    """
    # Arrange
    user_data = {"username": "get_user", "password_hash": "password123"}
    created_user = user_service.create(user_data)

    # Action
    fetched_user = user_service.get_by_id(created_user.id)

    # Assert
    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.username == "get_user"


def test_update_user(user_service):
    """
    يختبر تحديث بيانات مستخدم موجود.
    """
    # Arrange
    user_data = {"username": "original_name", "password_hash": "password123"}
    created_user = user_service.create(user_data)
    user_id = created_user.id

    # Action
    update_data = {"username": "updated_name"}
    updated_user = user_service.update(entity_id=user_id, data=update_data)

    # Assert
    assert updated_user is not None
    assert updated_user.id == user_id
    assert updated_user.username == "updated_name"


def test_update_nonexistent_user_raises_error(user_service):
    """
    يختبر أن محاولة تحديث مستخدم غير موجود تطلق استثناء NotFoundError.
    هذا يتبع نمط الاختبار في test_services.py[cite: 1162].
    """
    with pytest.raises(NotFoundError):
        user_service.update(entity_id=9999, data={"username": "ghost_user"})
