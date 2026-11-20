"""Unit tests for feature_auth_py."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make `backend/` importable when running `pytest` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from shared.entities_py import AppError, AppErrorKind, UserProfile  # noqa: E402
from feature.auth_py.domain.repository import AuthRepository  # noqa: E402
from feature.auth_py.domain.usecases import GetMeUseCase, PostConfirmationUseCase  # noqa: E402


class FakeRepo(AuthRepository):
    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def get_or_create_profile(self, user_id, email):
        self.calls.append((user_id, email))
        return UserProfile.new(user_id, email, "User")


def test_get_me_returns_entity():
    repo = FakeRepo()
    p = GetMeUseCase(repo).execute("u1", "a@b.c")
    assert p.user_id == "u1"
    assert len(repo.calls) == 1


def test_get_me_rejects_empty_sub():
    repo = FakeRepo()
    with pytest.raises(AppError) as ei:
        GetMeUseCase(repo).execute("", "a@b.c")
    assert ei.value.kind == AppErrorKind.UNAUTHORISED


def test_post_confirmation_is_idempotent():
    repo = FakeRepo()
    uc = PostConfirmationUseCase(repo)
    uc.execute("u1", "a@b.c")
    uc.execute("u1", "a@b.c")
    assert len(repo.calls) == 2
