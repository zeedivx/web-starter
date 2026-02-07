"""Common reusable validators."""

import re
from typing import ClassVar


class PasswordValidator:
    """
    Password validation with configurable rules.

    Usage:
        ```python
        @field_validator("password")
        @classmethod
        def validate_password(cls, v: str) -> str:
            return PasswordValidator.validate(v)
        ```

    Or with custom config:
        ```python
        @field_validator("password")
        @classmethod
        def validate_password(cls, v: str) -> str:
            return PasswordValidator(
                min_length=12,
                require_special=True
            ).validate(v)
        ```
    """

    DEFAULT_MIN_LENGTH: ClassVar[int] = 8
    DEFAULT_MAX_LENGTH: ClassVar[int] = 100
    DEFAULT_REQUIRE_UPPERCASE: ClassVar[bool] = True
    DEFAULT_REQUIRE_LOWERCASE: ClassVar[bool] = True
    DEFAULT_REQUIRE_DIGIT: ClassVar[bool] = True
    DEFAULT_REQUIRE_SPECIAL: ClassVar[bool] = False

    def __init__(
        self,
        *,
        min_length: int | None = None,
        max_length: int | None = None,
        require_uppercase: bool | None = None,
        require_lowercase: bool | None = None,
        require_digit: bool | None = None,
        require_special: bool | None = None,
    ) -> None:
        """
        Initialize password validator with custom rules.

        Args:
            min_length: Minimum password length
            max_length: Maximum password length
            require_uppercase: Require at least one uppercase letter
            require_lowercase: Require at least one lowercase letter
            require_digit: Require at least one digit
            require_special: Require at least one special character
        """
        self.min_length: int = min_length or self.DEFAULT_MIN_LENGTH
        self.max_length: int = max_length or self.DEFAULT_MAX_LENGTH
        self.require_uppercase: bool = (
            require_uppercase if require_uppercase is not None else self.DEFAULT_REQUIRE_UPPERCASE
        )
        self.require_lowercase: bool = (
            require_lowercase if require_lowercase is not None else self.DEFAULT_REQUIRE_LOWERCASE
        )
        self.require_digit: bool = (
            require_digit if require_digit is not None else self.DEFAULT_REQUIRE_DIGIT
        )
        self.require_special: bool = (
            require_special if require_special is not None else self.DEFAULT_REQUIRE_SPECIAL
        )

    def validate(self, value: str | None) -> str | None:
        """
        Validate password against configured rules.

        Args:
            value: Password to validate

        Returns:
            Validated password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if value is None:
            return None

        if len(value) < self.min_length:
            raise ValueError(f"Password must be at least {self.min_length} characters long")

        if len(value) > self.max_length:
            raise ValueError(f"Password must be at most {self.max_length} characters long")

        if self.require_uppercase and not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")

        if self.require_lowercase and not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")

        if self.require_digit and not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")

        if self.require_special and not re.search(r"[!@#$%^&*(),.?\":{}|<>+\-=\\/\[\]]", value):
            raise ValueError("Password must contain at least one special character")

        return value

    @classmethod
    def validate_default(cls, value: str | None) -> str | None:
        """
        Validate password with default rules.

        Args:
            value: Password to validate

        Returns:
            Validated password
        """
        return cls().validate(value)

    @classmethod
    def validate_required(cls, value: str) -> str:
        """
        Validate required password field with default rules.

        Args:
            value: Password to validate (must not be None)

        Returns:
            Validated password
        """
        result = cls().validate(value)
        assert result is not None
        return result


class UsernameValidator:
    """
    Username validation with configurable rules.

    Usage:
        ```python
        @field_validator("username")
        @classmethod
        def validate_username(cls, v: str | None) -> str | None:
            return UsernameValidator.validate(v)
        ```

    Or with custom config:
        ```python
        @field_validator("username")
        @classmethod
        def validate_username(cls, v: str | None) -> str | None:
            return UsernameValidator(
                min_length=5,
                allow_uppercase=False
            ).validate(v)
        ```
    """

    DEFAULT_MIN_LENGTH: ClassVar[int] = 3
    DEFAULT_MAX_LENGTH: ClassVar[int] = 50
    DEFAULT_ALLOW_UPPERCASE: ClassVar[bool] = True
    DEFAULT_ALLOW_UNDERSCORE: ClassVar[bool] = True
    DEFAULT_ALLOW_HYPHEN: ClassVar[bool] = True
    DEFAULT_PATTERN: ClassVar[str] = r"^[a-zA-Z0-9_-]+$"

    def __init__(
        self,
        *,
        min_length: int | None = None,
        max_length: int | None = None,
        allow_uppercase: bool | None = None,
        allow_underscore: bool | None = None,
        allow_hyphen: bool | None = None,
        custom_pattern: str | None = None,
    ) -> None:
        """
        Initialize username validator with custom rules.

        Args:
            min_length: Minimum username length
            max_length: Maximum username length
            allow_uppercase: Allow uppercase letters
            allow_underscore: Allow underscore character
            allow_hyphen: Allow hyphen character
            custom_pattern: Custom regex pattern for validation
        """
        self.min_length: int = min_length or self.DEFAULT_MIN_LENGTH
        self.max_length: int = max_length or self.DEFAULT_MAX_LENGTH
        self.allow_uppercase: bool = (
            allow_uppercase if allow_uppercase is not None else self.DEFAULT_ALLOW_UPPERCASE
        )
        self.allow_underscore: bool = (
            allow_underscore if allow_underscore is not None else self.DEFAULT_ALLOW_UNDERSCORE
        )
        self.allow_hyphen: bool = (
            allow_hyphen if allow_hyphen is not None else self.DEFAULT_ALLOW_HYPHEN
        )

        if custom_pattern:
            self.pattern: str = custom_pattern
        else:
            chars = "a-z0-9"
            if self.allow_uppercase:
                chars += "A-Z"
            if self.allow_underscore:
                chars += "_"
            if self.allow_hyphen:
                chars += "-"
            self.pattern = f"^[{chars}]+$"

    def validate(self, value: str | None) -> str | None:
        """
        Validate username against configured rules.

        Args:
            value: Username to validate

        Returns:
            Validated username

        Raises:
            ValueError: If username doesn't meet requirements
        """
        if value is None:
            return None

        value = value.strip()

        if len(value) < self.min_length:
            raise ValueError(f"Username must be at least {self.min_length} characters long")

        if len(value) > self.max_length:
            raise ValueError(f"Username must be at most {self.max_length} characters long")

        if not re.match(self.pattern, value):
            allowed_chars = "letters and numbers"
            if self.allow_underscore:
                allowed_chars += ", underscores"
            if self.allow_hyphen:
                allowed_chars += ", and hyphens"
            raise ValueError(f"Username must contain only {allowed_chars}")

        if self.allow_underscore or self.allow_hyphen:
            special_chars: list[str] = []
            if self.allow_underscore:
                special_chars.append("_")
            if self.allow_hyphen:
                special_chars.append("-")

            if value[0] in special_chars or value[-1] in special_chars:
                raise ValueError("Username cannot start or end with special characters")

        return value

    @classmethod
    def validate_default(cls, value: str | None) -> str | None:
        """
        Validate username with default rules.

        Args:
            value: Username to validate

        Returns:
            Validated username
        """
        return cls().validate(value)

    @classmethod
    def validate_required(cls, value: str) -> str:
        """
        Validate required username field with default rules.

        Args:
            value: Username to validate (must not be None)

        Returns:
            Validated username
        """
        result = cls().validate(value)
        assert result is not None
        return result
