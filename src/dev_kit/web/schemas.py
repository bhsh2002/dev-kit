# src/dev_kit/web/schemas.py
"""
Provides reusable base schemas and powerful schema factories for apiflask.

This module is the core of the API data validation and serialization layer,
offering tools to auto-generate CRUD schemas from SQLAlchemy models.
"""

from apiflask import Schema
from apiflask.fields import Boolean, DateTime, Integer, List, Nested, String
from apiflask.validators import Range
from marshmallow import ValidationError, pre_dump, validates_schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from dev_kit.database.repository import PaginationResult


class BaseSchema(Schema):
    """A base schema for all other schemas to inherit from."""

    pass


class UpdateSchemaMixin(BaseSchema):
    """A mixin to validate that an update request is not empty."""

    @validates_schema
    def ensure_at_least_one_field(self, data, **kwargs):
        if not data:
            raise ValidationError(
                "At least one field must be provided for update.", "_schema"
            )


class PaginationQuerySchema(Schema):
    """Schema for pagination query parameters (page, per_page)."""

    page = Integer(
        load_default=1, validate=Range(min=1), metadata={"description": "Page number."}
    )
    per_page = Integer(
        load_default=10,
        validate=Range(min=1, max=100),
        metadata={"description": "Items per page."},
    )


class BaseListQuerySchema(PaginationQuerySchema):
    """Base schema for list queries, adding sorting and soft-delete control."""

    sort_by = String(
        required=False,
        metadata={
            "description": "Sort results. Example:"
            " 'name' for ascending, '-created_at' for descending."
        },
    )
    include_soft_deleted = Boolean(
        load_default=False,
        metadata={"description": "Include soft-deleted items in the results."},
    )


class BaseFilterQuerySchema(BaseListQuerySchema):
    """Base schema for filter queries, with common timestamp filters."""

    created_after = DateTime(
        required=False,
        metadata={"description": "Filter for items created after this date."},
    )
    created_before = DateTime(
        required=False,
        metadata={"description": "Filter for items created before this date."},
    )


class PaginationInfoSchema(BaseSchema):
    """Schema for displaying pagination metadata in the output."""

    total = Integer(metadata={"description": "Total number of items."})
    page = Integer(metadata={"description": "Current page number."})
    per_page = Integer(metadata={"description": "Number of items per page."})
    total_pages = Integer(metadata={"description": "Total number of pages."})
    has_next = Boolean(metadata={"description": "Indicates if there is a next page."})
    has_prev = Boolean(
        metadata={"description": "Indicates if there is a previous page."}
    )


def create_pagination_schema(item_schema: type[Schema]) -> type[Schema]:
    """
    A factory that dynamically creates a pagination output schema
    for a given item schema.
    """

    class GenericPaginationOutSchema(BaseSchema):
        items = List(Nested(item_schema))
        pagination = Nested(PaginationInfoSchema)

        @pre_dump
        def make_pagination_serializable(self, data, **kwargs):
            if isinstance(data, PaginationResult):
                return {
                    "items": data.items,
                    "pagination": {
                        "total": data.total,
                        "page": data.page,
                        "per_page": data.per_page,
                        "total_pages": data.total_pages,
                        "has_next": data.has_next,
                        "has_prev": data.has_prev,
                    },
                }
            return data

    GenericPaginationOutSchema.__name__ = f"{item_schema.__name__}PaginationOut"
    return GenericPaginationOutSchema


def create_crud_schemas(model_class: type, **kwargs) -> dict:
    """
    Dynamically generates a full set of CRUD schemas for a SQLAlchemy model.

    This powerful factory creates five essential schemas for a given model:
    - 'main': For serializing model instances (output).
    - 'input': For validating new data upon creation (input).
    - 'update': A partial schema for validating updates.
    - 'query': For validating query parameters for filtering and pagination.
    - 'pagination_out': A wrapper schema for paginated responses.

    Args:
        model_class: The SQLAlchemy model to generate schemas for.
        **kwargs: Optional lists of field names to exclude from different schemas.
                  - `exclude_from_main` (List[str]): Fields to exclude from all schemas.
                  - `exclude_from_input` (List[str]): Additional fields to
                    exclude from the input schema.
                  - `exclude_from_update` (List[str]): Additional fields to
                    exclude from the update schema.

    Returns:
        A dictionary containing the generated 'main', 'input', 'update', 'query',
        and 'pagination_out' schemas.
    """
    model_name = model_class.__name__
    exclude_from_main = kwargs.get("exclude_from_main", [])
    exclude_from_input = kwargs.get("exclude_from_input", [])
    exclude_from_update = kwargs.get("exclude_from_update", [])
    custom_fields = kwargs.get("custom_fields", {})

    # --- Main Schema (for output) ---
    main_schema_attrs = {
        "Meta": type(
            "Meta",
            (),
            {
                "model": model_class,
                "include_fk": True,
                "exclude": tuple(exclude_from_main),
            },
        )
    }
    main_schema_attrs.update(custom_fields)
    MainSchema = type(f"{model_name}Schema", (SQLAlchemyAutoSchema,), main_schema_attrs)

    # --- Input Schema (for creation) ---
    class InputSchema(MainSchema):
        class Meta(MainSchema.Meta):
            exclude = tuple(set(exclude_from_main + exclude_from_input))

    # --- Update Schema (for updates) ---
    class UpdateSchema(UpdateSchemaMixin, MainSchema):
        class Meta(MainSchema.Meta):
            exclude = tuple(set(exclude_from_main + exclude_from_update))
            partial = True

    # --- Query Schema (for list filtering) ---
    QuerySchema = type(f"{model_name}QuerySchema", (BaseFilterQuerySchema,), {})

    # --- Pagination Output Schema ---
    PaginationOutSchema = create_pagination_schema(MainSchema)

    # Rename for better debugging and OpenAPI docs
    InputSchema.__name__ = f"{model_name}InputSchema"
    UpdateSchema.__name__ = f"{model_name}UpdateSchema"

    return {
        "main": MainSchema,
        "input": InputSchema,
        "update": UpdateSchema,
        "query": QuerySchema,
        "pagination_out": PaginationOutSchema,
    }


class MessageSchema(Schema):
    """A generic schema for simple message responses."""

    message = String()
