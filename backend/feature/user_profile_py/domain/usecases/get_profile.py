from __future__ import annotations

from shared.entities_py import AppError, AppErrorKind, UserProfile
from feature.user_profile_py.domain.repository import UserProfileRepository


class GetUserProfileUseCase:
    def __init__(self, repo: UserProfileRepository):
        self.repo = repo

    def execute(self, user_id: str) -> UserProfile:
        if not user_id:
            raise AppError(AppErrorKind.UNAUTHORISED)
        p = self.repo.find_by_id(user_id)
        if p is None:
            raise AppError(AppErrorKind.NOT_FOUND)
        return p
