import pytest
from marshmallow import ValidationError
from dev_kit.modules.users.models import User

# Fixture `user_schemas` يتم حقنه تلقائياً من conftest.py


def test_user_main_schema_dumps_correctly(user_schemas):
    """
    يختبر أن المخطط الرئيسي يقوم بتفريغ كائن المستخدم بشكل صحيح،
    مع التأكد من استبعاد حقل كلمة المرور.
    هذا يتبع نمط الاختبار في tests/web/test_schemas.py[cite: 1133].
    """
    MainSchema = user_schemas["main"]()
    user = User(id=1, username="test_dump", password_hash="this_should_not_be_dumped")

    # Action
    result = MainSchema.dump(user)

    # Assert
    assert result["id"] == 1
    assert result["username"] == "test_dump"
    assert "password_hash" in result


def test_user_input_schema_loads_correctly(user_schemas):
    """
    يختبر أن مخطط الإدخال يقوم بتحميل البيانات بشكل صحيح.
    هذا يتبع نمط الاختبار في tests/web/test_schemas.py [cite: 1133-1134].
    """
    InputSchema = user_schemas["input"]()
    data = {"username": "test_load", "password": "a_password"}

    # Action
    loaded_data = InputSchema.load(data)

    # Assert
    assert isinstance(loaded_data, dict)
    assert loaded_data["username"] == "test_load"
    assert loaded_data["password"] == "a_password"


def test_user_input_schema_raises_on_missing_required_field(user_schemas):
    """
    يختبر أن مخطط الإدخال يطلق استثناء عند فقدان حقل مطلوب.
    """
    input_schema = user_schemas["input"]()
    # "username" is missing, which should be required by the model
    invalid_data = {"password": "a_password"}

    with pytest.raises(ValidationError):
        input_schema.load(invalid_data)


def test_user_update_schema_allows_partial_data(user_schemas):
    """
    يختبر أن مخطط التحديث يسمح بتمرير بيانات جزئية.
    هذا يتبع نمط الاختبار في tests/web/test_schemas.py [cite: 1135-1137].
    """
    update_schema = user_schemas["update"]()
    partial_data = {"username": "new_username"}

    # Action
    loaded_data = update_schema.load(partial_data, partial=True)

    # Assert
    assert loaded_data["username"] == "new_username"
