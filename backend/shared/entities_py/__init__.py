"""Plain entity types — Python mirror of `shared/entities_rs`.

Same constraint as the Rust side: NO infrastructure imports here. No boto3,
no DynamoDB types, no requests, etc. Just pure data.
"""

from .user_profile import UserProfile, UserProfilePatch
from .app_error import AppError, AppErrorKind

__all__ = ["UserProfile", "UserProfilePatch", "AppError", "AppErrorKind"]
