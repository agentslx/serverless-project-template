use async_trait::async_trait;
use shared_entities_rs::{AppError, UserProfile};

/// What the auth feature needs from its data layer.
///
/// Implementations live in `data/repository/`.
#[async_trait]
pub trait AuthRepository: Send + Sync {
    async fn get_or_create_profile(
        &self,
        user_id: &str,
        email: &str,
    ) -> Result<UserProfile, AppError>;
}
