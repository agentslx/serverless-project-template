use aws_sdk_dynamodb::Client;
use shared_entities_rs::{AppError, UserProfile};
use tracing::error;

use crate::data::models::DynamoUserProfileModel;

/// Talks to the `user_profiles` DynamoDB table.
///
/// This datasource is **scoped to the auth feature**. The user_profile feature
/// has its *own* datasource that talks to the same table. They cannot import
/// each other (per AGENTS.md §3.8).
#[derive(Clone)]
pub struct DynamoUserProfileDataSource {
    client: Client,
    table: String,
}

impl DynamoUserProfileDataSource {
    pub fn new(client: Client, table: impl Into<String>) -> Self {
        Self { client, table: table.into() }
    }

    pub async fn get(&self, user_id: &str) -> Result<Option<UserProfile>, AppError> {
        let resp = self
            .client
            .get_item()
            .table_name(&self.table)
            .key("user_id", aws_sdk_dynamodb::types::AttributeValue::S(user_id.into()))
            .send()
            .await
            .map_err(|e| {
                error!(?e, "dynamodb get_item failed");
                AppError::Internal("dynamodb get_item".into())
            })?;

        Ok(resp.item.as_ref().and_then(DynamoUserProfileModel::from_item))
    }

    pub async fn put_if_absent(&self, p: &UserProfile) -> Result<(), AppError> {
        let item = DynamoUserProfileModel::to_item(p);
        let r = self
            .client
            .put_item()
            .table_name(&self.table)
            .set_item(Some(item))
            .condition_expression("attribute_not_exists(user_id)")
            .send()
            .await;

        match r {
            Ok(_) => Ok(()),
            Err(e) => {
                use aws_sdk_dynamodb::error::SdkError;
                if let SdkError::ServiceError(svc) = &e {
                    if svc.err().is_conditional_check_failed_exception() {
                        return Ok(()); // already exists — idempotent
                    }
                }
                error!(?e, "dynamodb put_item failed");
                Err(AppError::Internal("dynamodb put_item".into()))
            }
        }
    }
}
