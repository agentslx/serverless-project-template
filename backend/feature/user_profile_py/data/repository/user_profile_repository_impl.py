from __future__ import annotations

from typing import Optional

from shared.entities_py import UserProfile, UserProfilePatch
from feature.user_profile_py.domain.repository import UserProfileRepository
from feature.user_profile_py.data.datasources import DynamoUserProfileDataSource


class DynamoUserProfileRepository(UserProfileRepository):
    def __init__(self, datasource: DynamoUserProfileDataSource):
        self.db = datasource

    def find_by_id(self, user_id: str) -> Optional[UserProfile]:
        return self.db.get(user_id)

    def update(self, user_id: str, patch: UserProfilePatch) -> UserProfile:
        return self.db.update(user_id, patch)
