"""DynamoDB <-> entity transformer (lives in `data/models/` per AGENTS.md)."""
from __future__ import annotations

from typing import Optional
from shared.entities_py import UserProfile


class DynamoUserProfileModel:
    @staticmethod
    def to_item(p: UserProfile) -> dict:
        item = {
            "user_id": p.user_id,
            "email": p.email,
            "display_name": p.display_name,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }
        if p.avatar_url:
            item["avatar_url"] = p.avatar_url
        return item

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
