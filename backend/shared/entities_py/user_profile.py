"""Domain entity — UserProfile."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class UserProfile:
    user_id: str
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    @classmethod
    def new(cls, user_id: str, email: str, display_name: str) -> "UserProfile":
        return cls(user_id=user_id, email=email, display_name=display_name)

    def apply_patch(self, patch: "UserProfilePatch") -> "UserProfile":
        if patch.display_name is not None:
            self.display_name = patch.display_name
        if patch.avatar_url is not None:
            self.avatar_url = patch.avatar_url
        self.updated_at = _now_iso()
        return self

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class UserProfilePatch:
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
