"""User Pydantic schemas."""

from datetime import datetime

from pydantic import EmailStr, Field, field_validator

from src.schemas.base import BaseModelSchema, BaseSchema
from src.schemas.validators import PasswordValidator, UsernameValidator


class UserBase(BaseSchema):
    """
    Base user schema with common fields.

    Used as base for UserCreate and UserUpdate schemas.
    """

    email: EmailStr = Field(..., description="User email address", max_length=255)
    username: str | None = Field(None, description="Username", min_length=3, max_length=50)
    first_name: str | None = Field(None, description="First name", max_length=100)
    last_name: str | None = Field(None, description="Last name", max_length=100)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        """Validate username format."""
        return UsernameValidator.validate_default(v)


class UserCreate(UserBase):
    """
    Schema for creating a new user.

    Includes password field for registration.
    Password will be hashed before storing in database.
    """

    password: str = Field(..., description="User password", min_length=8, max_length=100)
    is_active: bool = Field(default=True, description="Whether user is active")
    is_superuser: bool = Field(default=False, description="Whether user is superuser")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        return PasswordValidator.validate_required(v)


class UserUpdate(BaseSchema):
    """
    Schema for updating an existing user.

    All fields are optional to allow partial updates.
    """

    email: EmailStr | None = Field(None, description="User email address", max_length=255)
    username: str | None = Field(None, description="Username", min_length=3, max_length=50)
    first_name: str | None = Field(None, description="First name", max_length=100)
    last_name: str | None = Field(None, description="Last name", max_length=100)
    password: str | None = Field(None, description="New password", min_length=8, max_length=100)
    is_active: bool | None = Field(None, description="Whether user is active")
    is_superuser: bool | None = Field(None, description="Whether user is superuser")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        """Validate username format."""
        return UsernameValidator.validate_default(v)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        """Validate password strength."""
        return PasswordValidator.validate_default(v)


class UserResponse(BaseModelSchema):
    """
    Schema for user responses.

    Includes all user fields except password.
    Used in API responses.
    """

    email: str = Field(..., description="User email address")
    username: str | None = Field(None, description="Username")
    first_name: str | None = Field(None, description="First name")
    last_name: str | None = Field(None, description="Last name")
    is_active: bool = Field(..., description="Whether user is active")
    is_superuser: bool = Field(..., description="Whether user is superuser")

    @property
    def full_name(self) -> str | None:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name


class UserInDB(UserResponse):
    """
    Schema for user in database.

    Includes hashed_password field.
    Used internally, never exposed in API responses.
    """

    hashed_password: str = Field(..., description="Hashed password")
    deleted_at: datetime | None = Field(None, description="Soft delete timestamp")
