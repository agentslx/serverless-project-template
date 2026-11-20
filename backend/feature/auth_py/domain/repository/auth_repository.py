"""Domain interface for the auth feature (Python)."""
from __future__ import annotations

import abc
from shared.entities_py import UserProfile


class AuthRepository(abc.ABC):
    @abc.abstractmethod
    def get_or_create_profile(self, user_id: str, email: str) -> UserProfile: ...
