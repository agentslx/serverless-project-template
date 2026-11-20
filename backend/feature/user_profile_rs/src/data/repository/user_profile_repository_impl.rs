use async_trait::async_trait;
use shared_entities_rs::{AppError, UserProfile, UserProfilePatch};

use crate::data::datasources::DynamoUserProfileDataSource;
use crate::domain::repository::UserProfileRepository;

#[derive(Clone)]
pub struct DynamoUserProfileRepository {
    db: DynamoUserProfileDataSource,
}

impl DynamoUserProfileRepository {
    pub fn new(db: DynamoUserProfileDataSource) -> Self { Self { db } }
}

#[async_trait]
impl UserProfileRepository for DynamoUserProfileRepository {
    async fn find_by_id(&self, user_id: &str) -> Result<Option<UserProfile>, AppError> {
        self.db.get(user_id).await
    }

    async fn update(
        &self,
        user_id: &str,
        patch: &UserProfilePatch,
    ) -> Result<UserProfile, AppError> {
        self.db.update(user_id, patch).await
    }
}
