use aws_sdk_dynamodb::types::{AttributeValue, ReturnValue};
use aws_sdk_dynamodb::Client;
use shared_entities_rs::{AppError, UserProfile, UserProfilePatch};
use tracing::error;

use crate::data::models::DynamoUserProfileModel;

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
            .key("user_id", AttributeValue::S(user_id.into()))
            .send()
            .await
            .map_err(|e| {
                error!(?e, "ddb get_item failed");
                AppError::Internal("dynamodb get_item".into())
            })?;
        Ok(resp.item.as_ref().and_then(DynamoUserProfileModel::from_item))
    }

    pub async fn update(
        &self,
        user_id: &str,
        patch: &UserProfilePatch,
    ) -> Result<UserProfile, AppError> {
        let now = chrono::Utc::now().to_rfc3339();
        let mut expr = String::from("SET updated_at = :u");
        let mut values = std::collections::HashMap::new();
        values.insert(":u".to_string(), AttributeValue::S(now));

        if let Some(name) = &patch.display_name {
            expr.push_str(", display_name = :d");
            values.insert(":d".into(), AttributeValue::S(name.clone()));
        }
        if let Some(url) = &patch.avatar_url {
            expr.push_str(", avatar_url = :a");
            values.insert(":a".into(), AttributeValue::S(url.clone()));
        }

        let resp = self
            .client
            .update_item()
            .table_name(&self.table)
            .key("user_id", AttributeValue::S(user_id.into()))
            .update_expression(expr)
            .set_expression_attribute_values(Some(values))
            .condition_expression("attribute_exists(user_id)")
            .return_values(ReturnValue::AllNew)
            .send()
            .await
            .map_err(|e| {
                error!(?e, "ddb update_item failed");
                AppError::Internal("dynamodb update_item".into())
            })?;

        let item = resp.attributes.unwrap_or_default();
        DynamoUserProfileModel::from_item(&item).ok_or(AppError::NotFound)
    }
}
