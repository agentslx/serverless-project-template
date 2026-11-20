use async_trait::async_trait;
use shared_entities_rs::AppError;

use crate::data::datasources::DynamoAdminDataSource;
use crate::domain::repository::{AdminRepository, ListUsersPage};

pub struct DynamoAdminRepository {
    db: DynamoAdminDataSource,
}

impl DynamoAdminRepository {
    pub fn new(db: DynamoAdminDataSource) -> Self { Self { db } }
}

#[async_trait]
impl AdminRepository for DynamoAdminRepository {
    async fn list_users(
        &self,
        limit: u32,
        next_token: Option<&str>,
    ) -> Result<ListUsersPage, AppError> {
        self.db.list_users(limit, next_token).await
    }
}
