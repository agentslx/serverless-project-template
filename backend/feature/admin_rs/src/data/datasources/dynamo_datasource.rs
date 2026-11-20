use aws_sdk_dynamodb::types::AttributeValue;
use aws_sdk_dynamodb::Client;
use base64::{engine::general_purpose::URL_SAFE_NO_PAD as B64, Engine as _};
use shared_entities_rs::AppError;
use std::collections::HashMap;
use tracing::error;

use crate::data::models::DynamoUserProfileModel;
use crate::domain::repository::ListUsersPage;

/// DynamoDB-backed datasource for admin queries.
///
/// `list_users` performs a paginated `Scan`. Scan is fine for the template's
/// scope (≤ a few thousand users); when the table grows, switch to a GSI on
/// `pk = "USER"` and `Query` instead.
#[derive(Clone)]
pub struct DynamoAdminDataSource {
    client: Client,
    table: String,
}

impl DynamoAdminDataSource {
    pub fn new(client: Client, table: impl Into<String>) -> Self {
        Self { client, table: table.into() }
    }

    pub async fn list_users(
        &self,
        limit: u32,
        next_token: Option<&str>,
    ) -> Result<ListUsersPage, AppError> {
        let exclusive_start_key = match next_token {
            None => None,
            Some(t) => Some(decode_token(t)?),
        };

        let mut req = self
            .client
            .scan()
            .table_name(&self.table)
            .limit(limit as i32);

        if let Some(esk) = exclusive_start_key {
            req = req.set_exclusive_start_key(Some(esk));
        }

        let resp = req.send().await.map_err(|e| {
            error!(?e, "ddb scan failed");
            AppError::Internal("dynamodb scan".into())
        })?;

        let users = resp
            .items()
            .iter()
            .filter_map(DynamoUserProfileModel::from_item)
            .collect();

        let next_token = resp.last_evaluated_key().map(encode_token);

        Ok(ListUsersPage { users, next_token })
    }
}

fn encode_token(key: &HashMap<String, AttributeValue>) -> String {
    // We only paginate on the `user_id` PK — encode just that field.
    // (Encoding the full key map would require a serde adapter for AttributeValue.)
    let user_id = key
        .get("user_id")
        .and_then(|v| v.as_s().ok())
        .cloned()
        .unwrap_or_default();
    B64.encode(user_id.as_bytes())
}

fn decode_token(token: &str) -> Result<HashMap<String, AttributeValue>, AppError> {
    let raw = B64
        .decode(token.as_bytes())
        .map_err(|_| AppError::Validation("invalid next_token".into()))?;
    let user_id = String::from_utf8(raw)
        .map_err(|_| AppError::Validation("invalid next_token".into()))?;
    let mut map = HashMap::new();
    map.insert("user_id".to_string(), AttributeValue::S(user_id));
    Ok(map)
}
