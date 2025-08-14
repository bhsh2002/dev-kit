# tests/test_exceptions.py

import pytest
from dev_kit.exceptions import (
    AppBaseException,
    NotFoundError,
    PermissionDeniedError,
)


def test_not_found_error_properties():
    """Tests that NotFoundError sets its properties correctly."""
    # Action
    error = NotFoundError(entity_name="Product", entity_id=123)

    # Assert
    assert error.status_code == 404
    assert error.error_code == "NOT_FOUND"
    assert "Product with ID/identifier '123' not found" in error.message
    assert error.payload["entity"] == "Product"
    assert error.payload["id"] == "123"


def test_to_dict_method():
    """Tests the to_dict method for proper serialization."""
    # Action
    error = AppBaseException(
        message="A custom error",
        status_code=418,
        error_code="IM_A_TEAPOT",
        payload={"extra": "info"},
    )
    error_dict = error.to_dict()

    # Assert
    expected_dict = {
        "message": "A custom error",
        "error_code": "IM_A_TEAPOT",
        "details": {"extra": "info"},
    }
    assert error_dict == expected_dict


def test_raise_permission_denied():
    """Tests that a function correctly raises PermissionDeniedError."""

    # Arrange
    def protected_function():
        # This function simulates a failure in permission checks
        raise PermissionDeniedError()

    # Action & Assert
    with pytest.raises(PermissionDeniedError) as excinfo:
        protected_function()

    # You can optionally inspect the raised exception
    assert excinfo.value.status_code == 403
    assert "You do not have permission" in excinfo.value.message
