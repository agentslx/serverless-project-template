use aws_sdk_dynamodb::types::AttributeValue;
use shared_entities_rs::UserProfile;
use std::collections::HashMap;

/// Transforms between DynamoDB attribute maps and the `UserProfile` entity.
///
/// Lives in `data/models/` because it depends on infrastructure types
/// (`AttributeValue`). Repositories use this internally — never expose it
/// past the data layer boundary.
pub struct DynamoUserProfileModel;

impl DynamoUserProfileModel {
    pub fn to_item(p: &UserProfile) -> HashMap<String, AttributeValue> {
        let mut item = HashMap::new();
        item.insert("user_id".into(), AttributeValue::S(p.user_id.clone()));
        item.insert("email".into(), AttributeValue::S(p.email.clone()));
        item.insert("display_name".into(), AttributeValue::S(p.display_name.clone()));
        if let Some(a) = &p.avatar_url {
            item.insert("avatar_url".into(), AttributeValue::S(a.clone()));
        }
        item.insert("created_at".into(), AttributeValue::S(p.created_at.clone()));
        item.insert("updated_at".into(), AttributeValue::S(p.updated_at.clone()));
        item
    }

    pub fn from_item(item: &HashMap<String, AttributeValue>) -> Option<UserProfile> {
        Some(UserProfile {
            user_id: item.get("user_id")?.as_s().ok()?.clone(),
            email: item.get("email")?.as_s().ok()?.clone(),
            display_name: item.get("display_name")?.as_s().ok()?.clone(),
            avatar_url: item
                .get("avatar_url")
                .and_then(|v| v.as_s().ok())
                .cloned(),
            created_at: item.get("created_at")?.as_s().ok()?.clone(),
            updated_at: item.get("updated_at")?.as_s().ok()?.clone(),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn roundtrip() {
        let original = UserProfile::new("u1", "a@b.c", "Alice");
        let item = DynamoUserProfileModel::to_item(&original);
        let back = DynamoUserProfileModel::from_item(&item).unwrap();
        assert_eq!(original, back);
    }
}
