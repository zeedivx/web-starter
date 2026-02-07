"""Base model class with auto tablename generation."""

import re
from typing import override

from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    Base class for all models.
    """

    __abstract__: bool = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Generate table name from class name.

        Converts CamelCase to snake_case and pluralizes:
        - User -> users
        - UserProfile -> user_profiles
        - Category -> categories
        - APIKey -> api_keys
        """
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)
        name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

        if name.endswith("y") and len(name) > 1 and name[-2] not in "aeiou":
            return f"{name[:-1]}ies"
        if name.endswith(("s", "x", "z", "ch", "sh")):
            return f"{name}es"
        return f"{name}s"

    def to_dict(self) -> dict[str, object]:
        """Convert model to dictionary."""
        return {
            str(c.name): getattr(self, str(c.name))  # pyright: ignore[reportAny]
            for c in self.__table__.columns
        }

    @override
    def __repr__(self) -> str:
        """String representation of model."""
        columns = ", ".join(
            f"{col.name}={getattr(self, str(col.name))!r}"  # pyright: ignore[reportAny]
            for col in self.__table__.columns
        )
        return f"{self.__class__.__name__}({columns})"
