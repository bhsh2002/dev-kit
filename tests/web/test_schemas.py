# # tests/web/test_schemas.py
# import pytest
# from marshmallow import ValidationError
# import datetime
# from tests.helpers import ProductModel
# from dev_kit.database.repository import PaginationResult


# def test_main_schema_dumps_correctly(product_schemas):
#     MainSchema = product_schemas["main"]
#     now = datetime.datetime.now(datetime.timezone.utc)
#     product = ProductModel(
#         id=1, name="Laptop", price=1200, created_at=now, updated_at=now
#     )
#     result = MainSchema().dump(product)
#     assert result["id"] == 1
#     assert "uuid" in result


# def test_input_schema_loads_correctly(db_session, product_schemas):
#     InputSchema = product_schemas["input"]
#     data = {"name": "Keyboard", "price": 75.0}
#     loaded_data = InputSchema().load(data)
#     assert isinstance(loaded_data, dict)
#     assert loaded_data["name"] == "Keyboard"


# def test_input_schema_raises_validation_error(db_session, product_schemas):
#     InputSchema = product_schemas["input"]
#     data = {"price": 75.0}
#     with pytest.raises(ValidationError):
#         InputSchema().load(data, session=db_session)


# def test_update_schema_allows_partial_data(db_session, product_schemas):
#     UpdateSchema = product_schemas["update"]
#     data = {"price": 80.0}

#     # Explicitly tell load that we are sending partial data.
#     # This returns a dictionary of the changes, not a model instance.
#     loaded_data = UpdateSchema().load(data, session=db_session, partial=True)

#     # Assert the returned dictionary.
#     assert loaded_data["price"] == 80.0


# def test_update_schema_fails_on_empty_data(db_session, product_schemas):
#     UpdateSchema = product_schemas["update"]
#     with pytest.raises(ValidationError):
#         UpdateSchema().load({}, session=db_session)


# def test_pagination_out_schema_works(product_schemas):
#     PaginationOutSchema = product_schemas["pagination_out"]
#     product1 = ProductModel(id=1, name="Laptop", price=1200)
#     paginated_result = PaginationResult(
#         items=[product1],
#         total=1,
#         page=1,
#         per_page=10,
#         total_pages=1,
#         has_next=False,
#         has_prev=False,
#     )
#     result = PaginationOutSchema().dump(paginated_result)
#     assert len(result["items"]) == 1
#     assert result["pagination"]["total"] == 1
