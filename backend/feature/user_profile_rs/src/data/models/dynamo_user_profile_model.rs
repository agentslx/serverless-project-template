use aws_sdk_dynamodb::types::AttributeValue;
use shared_entities_rs::UserProfile;
use std::collections::HashMap;

/// DynamoDB <-> entity transformer. Mirrors the one in feature_auth_rs — that
/// duplication is intentional. Per AGENTS.md §3.8 features must not import
/// each other; if a third feature needs the same transformer, lift to
/// `shared/modules/`.
pub struct DynamoUserProfileModel;

impl DynamoUserProfileModel {
    pub fn from_item(item: &HashMap<String, AttributeValue>) -> Option<UserProfile> {
        Some(UserProfile {
            user_id: item.get("user_id")?.as_s().ok()?.clone(),
            email: item.get("email")?.as_s().ok()?.clone(),
            display_name: item.get("display_name")?.as_s().ok()?.clone(),
            avatar_url: item.get("avatar_url").and_then(|v| v.as_s().ok()).cloned(),
            created_at: item.get("created_at")?.as_s().ok()?.clone(),
            updated_at: item.get("updated_at")?.as_s().ok()?.clone(),
        })
    }
}
