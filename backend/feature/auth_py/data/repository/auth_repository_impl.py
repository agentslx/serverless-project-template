"""Concrete `AuthRepository` impl backed by DynamoDB."""
from __future__ import annotations

from shared.entities_py import AppError, AppErrorKind, UserProfile
from feature.auth_py.domain.repository import AuthRepository
from feature.auth_py.data.datasources import DynamoUserProfileDataSource


class DynamoAuthRepository(AuthRepository):
    def __init__(self, datasource: DynamoUserProfileDataSource):
        self.db = datasource

    def get_or_create_profile(self, user_id: str, email: str) -> UserProfile:
        existing = self.db.get(user_id)
        if existing is not None:
            return existing
        new = UserProfile.new(user_id, email, _default_display_name(email))
        self.db.put_if_absent(new)
        again = self.db.get(user_id)
        if again is None:
            raise AppError(AppErrorKind.INTERNAL, "profile vanished after put")
        return again


def _default_display_name(email: str) -> str:
    return email.split("@", 1)[0] if "@" in email else "user"
