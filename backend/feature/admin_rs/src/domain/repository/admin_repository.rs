use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use shared_entities_rs::{AppError, UserProfile};

/// One page of `list_users` results.
///
/// `next_token` is opaque from the caller's perspective — the FE just
/// echoes it back to fetch the next page. Internally it is the
/// base64-encoded DynamoDB `LastEvaluatedKey`.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct ListUsersPage {
    pub users: Vec<UserProfile>,
    pub next_token: Option<String>,
}

/// Domain interface for admin-only persistence operations.
/// Concrete impls live in `data/repository/`.
#[async_trait]
pub trait AdminRepository: Send + Sync {
    async fn list_users(
        &self,
        limit: u32,
        next_token: Option<&str>,
    ) -> Result<ListUsersPage, AppError>;
}
