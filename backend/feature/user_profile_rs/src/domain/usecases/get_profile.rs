use crate::domain::repository::UserProfileRepository;
use shared_entities_rs::{AppError, UserProfile};

pub struct GetUserProfileUseCase<R: UserProfileRepository> {
    repo: R,
}

impl<R: UserProfileRepository> GetUserProfileUseCase<R> {
    pub fn new(repo: R) -> Self { Self { repo } }

    pub async fn execute(&self, user_id: &str) -> Result<UserProfile, AppError> {
        if user_id.is_empty() {
            return Err(AppError::Unauthorised);
        }
        self.repo
            .find_by_id(user_id)
            .await?
            .ok_or(AppError::NotFound)
    }
}
