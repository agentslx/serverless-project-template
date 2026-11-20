//! Lambda — Cognito PostConfirmation_ConfirmSignUp trigger.
//!
//! Cognito invokes this synchronously after a user confirms their email.
//! We must return the original event unmodified or sign-up will fail.

use lambda_runtime::{run, service_fn, Error, LambdaEvent};
use serde_json::Value;
use std::env;
use tracing::{info, warn};

use feature_auth_rs::data::datasources::DynamoUserProfileDataSource;
use feature_auth_rs::data::repository::DynamoAuthRepository;
use feature_auth_rs::domain::usecases::PostConfirmationUseCase;
use shared_common_rs::init_tracing;

#[tokio::main]
async fn main() -> Result<(), Error> {
    init_tracing();

    let table = env::var("USER_PROFILES_TABLE").expect("USER_PROFILES_TABLE must be set");
    let ddb = shared_database_rs::build_client().await;
    let repo = DynamoAuthRepository::new(DynamoUserProfileDataSource::new(ddb, table));
    let usecase = PostConfirmationUseCase::new(repo);

    run(service_fn(|e| handle(e, &usecase))).await
}

async fn handle<R>(
    event: LambdaEvent<Value>,
    usecase: &PostConfirmationUseCase<R>,
) -> Result<Value, Error>
where
    R: feature_auth_rs::domain::repository::AuthRepository,
{
    let payload = event.payload.clone();

    let sub = payload
        .pointer("/request/userAttributes/sub")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    let email = payload
        .pointer("/request/userAttributes/email")
        .and_then(|v| v.as_str())
        .unwrap_or("");

    info!(%sub, %email, "post-confirmation trigger");

    if !sub.is_empty() {
        if let Err(e) = usecase.execute(sub, email).await {
            // Don't fail Cognito flow if our seed errors — log + continue.
            warn!(?e, "failed to seed user_profile; continuing");
        }
    }
    // Cognito requires the original event back.
    Ok(payload)
}
