"""Password hashing and verification using Argon2id."""

from typing import ClassVar

from passlib.context import CryptContext

from src.core.settings import settings


class PasswordHasher:
    """
    Password hashing and verification using Argon2id algorithm.

    Usage:
        ```python
        hasher = PasswordHasher()
        hashed = hasher.hash("my_password")
        is_valid = hasher.verify("my_password", hashed)

        hasher = PasswordHasher(
            time_cost=4,
            memory_cost=204800,
            parallelism=16
        )
        hashed = hasher.hash("my_password")
        ```
    """

    DEFAULT_TIME_COST: ClassVar[int] = 2
    DEFAULT_MEMORY_COST: ClassVar[int] = 102400
    DEFAULT_PARALLELISM: ClassVar[int] = 8
    DEFAULT_HASH_LENGTH: ClassVar[int] = 32
    DEFAULT_SALT_LENGTH: ClassVar[int] = 16

    def __init__(
        self,
        *,
        time_cost: int | None = None,
        memory_cost: int | None = None,
        parallelism: int | None = None,
        hash_length: int | None = None,
        salt_length: int | None = None,
    ) -> None:
        """
        Initialize password hasher with Argon2id configuration.

        Args:
            time_cost: Number of iterations (default: 2)
            memory_cost: Memory usage in KB (default: 102400 = 100 MB)
            parallelism: Number of parallel threads (default: 8)
            hash_length: Length of hash in bytes (default: 32)
            salt_length: Length of salt in bytes (default: 16)

        Note:
            Higher values increase security but also increase computation time:
            - time_cost: Linear impact on time
            - memory_cost: Linear impact on memory usage
            - parallelism: More threads = faster, but diminishing returns
        """
        self.time_cost: int = time_cost or self.DEFAULT_TIME_COST
        self.memory_cost: int = memory_cost or self.DEFAULT_MEMORY_COST
        self.parallelism: int = parallelism or self.DEFAULT_PARALLELISM
        self.hash_length: int = hash_length or self.DEFAULT_HASH_LENGTH
        self.salt_length: int = salt_length or self.DEFAULT_SALT_LENGTH

        self._context: CryptContext = CryptContext(
            schemes=["argon2"],
            deprecated="auto",
            argon2__type="id",
            argon2__time_cost=self.time_cost,
            argon2__memory_cost=self.memory_cost,
            argon2__parallelism=self.parallelism,
            argon2__hash_len=self.hash_length,
            argon2__salt_size=self.salt_length,
        )

    def hash(self, password: str) -> str:
        """
        Hash a password using Argon2id.

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string in PHC format

        Raises:
            ValueError: If password is empty

        Example:
            ```python
            hasher = PasswordHasher()
            hashed = hasher.hash("my_secure_password")
            # Returns: $argon2id$v=19$m=102400,t=2,p=8$...$...
            ```
        """
        if not password:
            raise ValueError("Password cannot be empty")

        return self._context.hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        """
        Verify a password against a hash.

        Args:
            password: Plain text password to verify
            hashed: Hashed password to verify against

        Returns:
            True if password matches hash, False otherwise

        Example:
            ```python
            hasher = PasswordHasher()
            is_valid = hasher.verify("my_password", hashed_password)
            ```
        """
        if not password or not hashed:
            return False

        try:
            return self._context.verify(password, hashed)
        except Exception:
            return False

    def needs_update(self, hashed: str) -> bool:
        """
        Check if a hash needs to be updated.

        This happens when:
        - The hash uses outdated parameters (e.g., lower time/memory cost)
        - The hash format is outdated
        - Configuration has changed to stronger settings

        Args:
            hashed: Hashed password to check

        Returns:
            True if hash should be regenerated, False otherwise

        Example:
            ```python
            if hasher.needs_update(user.hashed_password):
                user.hashed_password = hasher.hash(password)
            ```
        """
        try:
            return self._context.needs_update(hashed)
        except Exception:
            return True

    def verify_and_update(self, password: str, hashed: str) -> tuple[bool, str | None]:
        """
        Verify password and return new hash if update needed.

        Convenience method that combines verify() and needs_update().
        If the password is correct but the hash is outdated, returns
        a new hash that should be stored.

        Args:
            password: Plain text password to verify
            hashed: Hashed password to verify against

        Returns:
            Tuple of (is_valid, new_hash)
            - is_valid: True if password matches
            - new_hash: New hash if update needed, None otherwise

        Example:
            ```python
            hasher = PasswordHasher()
            is_valid, new_hash = hasher.verify_and_update(password, user.hashed_password)

            if is_valid:
                if new_hash:
                    user.hashed_password = new_hash
                    await session.commit()
            ```
        """
        try:
            is_valid, new_hash = self._context.verify_and_update(password, hashed)
            return is_valid, new_hash
        except Exception:
            return False, None


def create_hasher_from_settings() -> PasswordHasher:
    """
    Create a PasswordHasher instance from application settings.

    Returns:
        Configured PasswordHasher instance

    Example:
        ```python
        from src.core.security.password import create_hasher_from_settings

        hasher = create_hasher_from_settings()
        hashed = hasher.hash("password")
        ```
    """
    return PasswordHasher(
        time_cost=settings.password_argon2_time_cost,
        memory_cost=settings.password_argon2_memory_cost,
        parallelism=settings.password_argon2_parallelism,
    )


default_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Hash a password using default Argon2id configuration.

    Convenience function for quick password hashing.

    Args:
        password: Plain text password

    Returns:
        Hashed password

    Example:
        ```python
        from src.core.security import hash_password

        hashed = hash_password("my_password")
        ```
    """
    return default_hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password using default Argon2id configuration.

    Convenience function for quick password verification.

    Args:
        password: Plain text password
        hashed: Hashed password

    Returns:
        True if password matches hash

    Example:
        ```python
        from src.core.security import verify_password

        if verify_password("my_password", user.hashed_password):
            pass
        ```
    """
    return default_hasher.verify(password, hashed)
