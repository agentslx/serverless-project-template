"""Domain-level errors. Mirror of `shared/entities_rs/app_error.rs`."""
from __future__ import annotations

import enum


class AppErrorKind(str, enum.Enum):
    NOT_FOUND = "not_found"
    UNAUTHORISED = "unauthorised"
    FORBIDDEN = "forbidden"
    VALIDATION = "validation"
    CONFLICT = "conflict"
    INTERNAL = "internal"


class AppError(Exception):
    def __init__(self, kind: AppErrorKind, message: str = ""):
        super().__init__(message or kind.value)
        self.kind = kind
        self.message = message or kind.value

    @property
    def http_status(self) -> int:
        return {
            AppErrorKind.NOT_FOUND: 404,
            AppErrorKind.UNAUTHORISED: 401,
            AppErrorKind.FORBIDDEN: 403,
            AppErrorKind.VALIDATION: 400,
            AppErrorKind.CONFLICT: 409,
            AppErrorKind.INTERNAL: 500,
        }[self.kind]
