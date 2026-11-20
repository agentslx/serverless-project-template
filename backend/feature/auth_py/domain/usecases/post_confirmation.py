from __future__ import annotations

from shared.entities_py import UserProfile
from feature.auth_py.domain.repository import AuthRepository


class PostConfirmationUseCase:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    def execute(self, user_id: str, email: str) -> UserProfile:
        return self.repo.get_or_create_profile(user_id, email)
