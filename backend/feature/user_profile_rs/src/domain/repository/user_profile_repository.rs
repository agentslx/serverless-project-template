use async_trait::async_trait;
use shared_entities_rs::{AppError, UserProfile, UserProfilePatch};

/// Domain interface used by usecases. Concrete impls live in `data/repository/`.
#[async_trait]
pub trait UserProfileRepository: Send + Sync {
    async fn find_by_id(&self, user_id: &str) -> Result<Option<UserProfile>, AppError>;

    async fn update(
        &self,
        user_id: &str,
        patch: &UserProfilePatch,
    ) -> Result<UserProfile, AppError>;
}
