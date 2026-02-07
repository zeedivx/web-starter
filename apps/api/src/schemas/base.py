"""Base Pydantic schemas."""

from datetime import datetime
from typing import ClassVar, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T", bound=BaseModel)


class BaseSchema(BaseModel):
    """
    Base schema with common configuration.

    Attributes:
        model_config: Configuration for the schema
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


class IDSchema(BaseSchema):
    """
    Schema with UUID id field.

    Attributes:
        id: UUID v7 identifier
    """

    id: UUID = Field(..., description="UUID identifier")


class TimestampSchema(BaseSchema):
    """
    Schema with timestamp fields.

    Attributes:
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class BaseModelSchema(IDSchema, TimestampSchema):
    """
    Combines ID and timestamp schemas.

    Use this as base for most model response schemas.

    Attributes:
        id: UUID identifier
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """


class ResponseSchema[T](BaseSchema):
    """
    Generic response wrapper.

    Usage:
        ```python
        @app.get("/users/{id}", response_model=ResponseSchema[UserSchema])
        async def get_user(id: UUID) -> ResponseSchema[UserSchema]:
            user = await get_user_by_id(id)
            return ResponseSchema(
                success=True,
                message="User retrieved successfully",
                data=user
            )
        ```
    """

    success: bool = Field(default=True, description="Whether request was successful")
    message: str = Field(default="Success", description="Response message")
    data: T | None = Field(default=None, description="Response data")


class PaginationParams(BaseSchema):
    """
    Pagination query parameters.

    Attributes:
        page: Page number (1-indexed)
        page_size: Number of items per page
        skip: Number of items to skip (computed)
    """

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def skip(self) -> int:
        """Calculate number of items to skip."""
        return (self.page - 1) * self.page_size


class PaginatedResponse[T](BaseSchema):
    """
    Paginated response wrapper.

    Usage:
        ```python
        @app.get("/users", response_model=PaginatedResponse[UserSchema])
        async def list_users(
            pagination: PaginationParams = Depends()
        ) -> PaginatedResponse[UserSchema]:
            users, total = await get_users_paginated(pagination)
            return PaginatedResponse(
                items=users,
                total=total,
                page=pagination.page,
                page_size=pagination.page_size
            )
        ```
    """

    items: list[T] = Field(default_factory=list, description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Items per page")

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1
