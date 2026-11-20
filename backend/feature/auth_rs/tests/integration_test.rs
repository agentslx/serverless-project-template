//! Integration tests for feature_auth_rs.
//!
//! These tests require a DynamoDB-local instance:
//!     docker run -p 8000:8000 amazon/dynamodb-local
//! and `DYNAMODB_ENDPOINT=http://localhost:8000` in the env.
//!
//! They are skipped automatically when the env var is missing so `cargo test`
//! still works in CI without spinning up Docker.

use feature_auth_rs::data::datasources::DynamoUserProfileDataSource;
use feature_auth_rs::data::repository::DynamoAuthRepository;
use feature_auth_rs::domain::repository::AuthRepository;
use std::env;

fn dynamodb_endpoint() -> Option<String> {
    env::var("DYNAMODB_ENDPOINT").ok()
}

#[tokio::test]
async fn get_or_create_creates_then_reads() {
    let Some(endpoint) = dynamodb_endpoint() else {
        eprintln!("skipping: DYNAMODB_ENDPOINT not set");
        return;
    };
    env::set_var("AWS_REGION", "ap-southeast-2");
    env::set_var("DYNAMODB_ENDPOINT", endpoint);
    env::set_var("AWS_ACCESS_KEY_ID", "x");
    env::set_var("AWS_SECRET_ACCESS_KEY", "x");

    let client = shared_database_rs::build_client().await;

    // Caller is responsible for creating the table beforehand:
    //   aws dynamodb create-table --endpoint-url http://localhost:8000 \
    //     --table-name test_user_profiles \
    //     --attribute-definitions AttributeName=user_id,AttributeType=S \
    //     --key-schema AttributeName=user_id,KeyType=HASH \
    //     --billing-mode PAY_PER_REQUEST
    let table = env::var("TEST_TABLE").unwrap_or_else(|_| "test_user_profiles".into());
    let ds = DynamoUserProfileDataSource::new(client, table);
    let repo = DynamoAuthRepository::new(ds);

    let p1 = repo.get_or_create_profile("u-int-1", "a@b.c").await.unwrap();
    let p2 = repo.get_or_create_profile("u-int-1", "a@b.c").await.unwrap();
    assert_eq!(p1, p2); // idempotent
}
