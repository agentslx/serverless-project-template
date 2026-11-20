from __future__ import annotations

from typing import Optional
from shared.entities_py import UserProfile


class DynamoUserProfileModel:
    @staticmethod
    def from_item(item: dict) -> Optional[UserProfile]:
        if not item:
            return None
        try:
            return UserProfile(
                user_id=item["user_id"],
                email=item["email"],
                display_name=item["display_name"],
                avatar_url=item.get("avatar_url"),
                created_at=item["created_at"],
                updated_at=item["updated_at"],
            )
        except KeyError:
            return None
