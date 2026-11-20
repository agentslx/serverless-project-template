use thiserror::Error;

/// Domain-level errors. Each feature has its own local `Error` enum but
/// converts into this at the boundary (handler) so HTTP responses are uniform.
#[derive(Debug, Error)]
pub enum AppError {
    #[error("not found")]
    NotFound,

    #[error("unauthorised")]
    Unauthorised,

    #[error("forbidden")]
    Forbidden,

    #[error("validation: {0}")]
    Validation(String),

    #[error("conflict: {0}")]
    Conflict(String),

    #[error("internal: {0}")]
    Internal(String),
}

impl AppError {
    pub fn http_status(&self) -> u16 {
        match self {
            Self::NotFound => 404,
            Self::Unauthorised => 401,
            Self::Forbidden => 403,
            Self::Validation(_) => 400,
            Self::Conflict(_) => 409,
            Self::Internal(_) => 500,
        }
    }
}
