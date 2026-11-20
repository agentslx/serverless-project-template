//! Thin shared bootstrap for an AWS DynamoDB client.
//!
//! Datasources receive the client through their constructor — they do **not**
//! call `build_client()` themselves. This keeps datasources testable.
//!
//! Reads `AWS_REGION` (default `ap-southeast-2`) and the optional override
//! `DYNAMODB_ENDPOINT` (used for `amazon/dynamodb-local`).

use aws_sdk_dynamodb::Client;
use std::env;

pub async fn build_client() -> Client {
    let region = env::var("AWS_REGION").unwrap_or_else(|_| "ap-southeast-2".to_string());

    let mut loader = aws_config::defaults(aws_config::BehaviorVersion::latest())
        .region(aws_config::Region::new(region));

    if let Ok(endpoint) = env::var("DYNAMODB_ENDPOINT") {
        tracing::info!(%endpoint, "using DynamoDB local endpoint");
        loader = loader.endpoint_url(endpoint);
    }

    let cfg = loader.load().await;
    Client::new(&cfg)
}
