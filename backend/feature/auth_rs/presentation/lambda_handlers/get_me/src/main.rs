//! Lambda handler — GET /me
//!
//! Returns the current user's profile (lazily creating one if missing).
//! Auth: API Gateway HTTP API with Cognito JWT authoriser, OR an upstream
//! that sets `x-user-sub` (used by the local proxy in dev).

use lambda_http::{run, service_fn, Body, Error, Request, Response};
use std::env;

use feature_auth_rs::data::datasources::DynamoUserProfileDataSource;
use feature_auth_rs::data::repository::DynamoAuthRepository;
use feature_auth_rs::domain::usecases::GetMeUseCase;
use shared_common_rs::{claim_sub, error_response, init_tracing, json_response};

#[tokio::main]
async fn main() -> Result<(), Error> {
    init_tracing();

    let table = env::var("USER_PROFILES_TABLE").expect("USER_PROFILES_TABLE must be set");
    let ddb = shared_database_rs::build_client().await;
    let repo = DynamoAuthRepository::new(DynamoUserProfileDataSource::new(ddb, table));
    let usecase = GetMeUseCase::new(repo);

    run(service_fn(|req: Request| handle(req, &usecase))).await
}

async fn handle<R>(
    req: Request,
    usecase: &GetMeUseCase<R>,
) -> Result<Response<Body>, Error>
where
    R: feature_auth_rs::domain::repository::AuthRepository,
{
    let sub = match claim_sub(&req) {
        Ok(s) => s,
        Err(e) => return Ok(error_response(e)),
    };
    // Email may be present as a header from the JWT mapping; not required.
    let email = req
        .headers()
        .get("x-user-email")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("")
        .to_string();

    match usecase.execute(&sub, &email).await {
        Ok(profile) => Ok(json_response(200, &profile)),
        Err(e) => Ok(error_response(e)),
    }
}
