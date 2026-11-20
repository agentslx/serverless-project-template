use async_trait::async_trait;
use shared_entities_rs::{AppError, UserProfile};

use crate::data::datasources::DynamoUserProfileDataSource;
use crate::domain::repository::AuthRepository;

/// Implementation of `AuthRepository` backed by DynamoDB.
///
/// The repository is the only place that knows about *both* the entity and
/// the DTO. It glues datasources together — for example, a future cache
/// datasource would also be wired here without touching domain or
/// presentation code.
pub struct DynamoAuthRepository {
    db: DynamoUserProfileDataSource,
}

impl DynamoAuthRepository {
    pub fn new(db: DynamoUserProfileDataSource) -> Self {
        Self { db }
    }
}

#[async_trait]
impl AuthRepository for DynamoAuthRepository {
    async fn get_or_create_profile(
        &self,
        user_id: &str,
        email: &str,
    ) -> Result<UserProfile, AppError> {
        if let Some(p) = self.db.get(user_id).await? {
            return Ok(p);
        }
        let new = UserProfile::new(user_id, email, default_display_name(email));
        self.db.put_if_absent(&new).await?;
        // Re-read so we always return what's in the table (handles a race).
        self.db
            .get(user_id)
            .await?
            .ok_or_else(|| AppError::Internal("profile vanished after put".into()))
    }
}

fn default_display_name(email: &str) -> String {
    email.split('@').next().unwrap_or("user").to_string()
}
