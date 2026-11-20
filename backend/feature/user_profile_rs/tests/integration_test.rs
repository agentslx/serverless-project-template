//! Integration tests against DynamoDB-local.
//! Skipped automatically when DYNAMODB_ENDPOINT is not set.

use feature_user_profile_rs::data::datasources::DynamoUserProfileDataSource;
use feature_user_profile_rs::data::repository::DynamoUserProfileRepository;
use feature_user_profile_rs::domain::repository::UserProfileRepository;
use shared_entities_rs::{UserProfile, UserProfilePatch};
use std::env;

#[tokio::test]
async fn read_after_write() {
    let Some(_) = env::var("DYNAMODB_ENDPOINT").ok() else {
        eprintln!("skipping: DYNAMODB_ENDPOINT not set");
        return;
    };
    env::set_var("AWS_REGION", "ap-southeast-2");
    env::set_var("AWS_ACCESS_KEY_ID", "x");
    env::set_var("AWS_SECRET_ACCESS_KEY", "x");

    let client = shared_database_rs::build_client().await;
    let table = env::var("TEST_TABLE").unwrap_or_else(|_| "test_user_profiles".into());

    // Seed: pretend feature_auth_rs created the row.
    let seed = UserProfile::new("u-int-2", "a@b.c", "Seed");
    feature_auth_seed(&client, &table, &seed).await;

    let repo = DynamoUserProfileRepository::new(DynamoUserProfileDataSource::new(client, table));
    let updated = repo
        .update("u-int-2", &UserProfilePatch {
            display_name: Some("Updated".into()),
            avatar_url: None,
        })
        .await
        .unwrap();
    assert_eq!(updated.display_name, "Updated");

    let again = repo.find_by_id("u-int-2").await.unwrap().unwrap();
    assert_eq!(again.display_name, "Updated");
}

// Tiny helper to seed without touching feature_auth_rs (which we mustn't import here).
async fn feature_auth_seed(client: &aws_sdk_dynamodb::Client, table: &str, p: &UserProfile) {
    use aws_sdk_dynamodb::types::AttributeValue;
    let mut item = std::collections::HashMap::new();
    item.insert("user_id".into(), AttributeValue::S(p.user_id.clone()));
    item.insert("email".into(), AttributeValue::S(p.email.clone()));
    item.insert("display_name".into(), AttributeValue::S(p.display_name.clone()));
    item.insert("created_at".into(), AttributeValue::S(p.created_at.clone()));
    item.insert("updated_at".into(), AttributeValue::S(p.updated_at.clone()));
    let _ = client.put_item().table_name(table).set_item(Some(item)).send().await;
}
