from __future__ import annotations

from shared.entities_py import AppError, AppErrorKind, UserProfile, UserProfilePatch
from feature.user_profile_py.domain.repository import UserProfileRepository


class UpdateUserProfileUseCase:
    def __init__(self, repo: UserProfileRepository):
        self.repo = repo

    def execute(self, caller_user_id: str, target_user_id: str,
                patch: UserProfilePatch) -> UserProfile:
        if caller_user_id != target_user_id:
            raise AppError(AppErrorKind.FORBIDDEN)
        if patch.display_name is not None and len(patch.display_name.strip()) < 2:
            raise AppError(AppErrorKind.VALIDATION, "display_name must be ≥ 2 chars")
        return self.repo.update(target_user_id, patch)
