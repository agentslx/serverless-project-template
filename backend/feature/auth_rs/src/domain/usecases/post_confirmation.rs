use crate::domain::repository::AuthRepository;
use shared_entities_rs::{AppError, UserProfile};

/// Triggered by Cognito's `PostConfirmation_ConfirmSignUp` event.
/// Idempotently seeds the `user_profiles` row.
pub struct PostConfirmationUseCase<R: AuthRepository> {
    repo: R,
}

impl<R: AuthRepository> PostConfirmationUseCase<R> {
    pub fn new(repo: R) -> Self {
        Self { repo }
    }

    pub async fn execute(&self, user_id: &str, email: &str) -> Result<UserProfile, AppError> {
        // Same `get_or_create` semantics — idempotent.
        self.repo.get_or_create_profile(user_id, email).await
    }
}
