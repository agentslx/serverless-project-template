from __future__ import annotations

import abc
from typing import Optional

from shared.entities_py import UserProfile, UserProfilePatch


class UserProfileRepository(abc.ABC):
    @abc.abstractmethod
    def find_by_id(self, user_id: str) -> Optional[UserProfile]: ...

    @abc.abstractmethod
    def update(self, user_id: str, patch: UserProfilePatch) -> UserProfile: ...
