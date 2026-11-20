"""Unit tests for feature_user_profile_py."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.entities_py import AppError, AppErrorKind, UserProfile, UserProfilePatch  # noqa: E402
from feature.user_profile_py.domain.repository import UserProfileRepository  # noqa: E402
from feature.user_profile_py.domain.usecases import (  # noqa: E402
    GetUserProfileUseCase,
    UpdateUserProfileUseCase,
)


class Stub(UserProfileRepository):
    def __init__(self, found: Optional[UserProfile] = None):
        self.found = found

    def find_by_id(self, user_id):
        return self.found

    def update(self, user_id, patch):
        return UserProfile.new(user_id, "a@b.c", patch.display_name or "X")


def test_get_profile_happy():
    p = UserProfile.new("u1", "a@b.c", "Alice")
    assert GetUserProfileUseCase(Stub(p)).execute("u1") == p


def test_get_profile_not_found():
    with pytest.raises(AppError) as ei:
        GetUserProfileUseCase(Stub(None)).execute("u1")
    assert ei.value.kind == AppErrorKind.NOT_FOUND


def test_update_profile_forbidden():
    with pytest.raises(AppError) as ei:
        UpdateUserProfileUseCase(Stub()).execute("u1", "u2", UserProfilePatch())
    assert ei.value.kind == AppErrorKind.FORBIDDEN


def test_update_profile_validation():
    with pytest.raises(AppError) as ei:
        UpdateUserProfileUseCase(Stub()).execute(
            "u1", "u1", UserProfilePatch(display_name="a")
        )
    assert ei.value.kind == AppErrorKind.VALIDATION
