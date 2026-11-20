//! Lambda — GET /admin/users?limit=&next_token=
//!
//! Auth: API Gateway (or AppSync) is configured to validate the *admin*
//! Cognito user pool JWT before this Lambda is invoked. We additionally
//! check that the caller's `cognito:groups` claim contains `"admin"`
//! belt-and-braces.

use lambda_http::{run, service_fn, Body, Error, Request, RequestExt, Response};
use std::env;

use feature_admin_rs::data::datasources::DynamoAdminDataSource;
use feature_admin_rs::data::repository::DynamoAdminRepository;
use feature_admin_rs::domain::usecases::ListUsersUseCase;
use shared_common_rs::{claim_sub, error_response, init_tracing, json_response};
use shared_entities_rs::AppError;

#[tokio::main]
async fn main() -> Result<(), Error> {
    init_tracing();

    let table = env::var("USER_PROFILES_TABLE").expect("USER_PROFILES_TABLE must be set");
    let ddb = shared_database_rs::build_client().await;
    let repo = DynamoAdminRepository::new(DynamoAdminDataSource::new(ddb, table));
    let uc = ListUsersUseCase::new(repo);

    run(service_fn(|req: Request| handle(req, &uc))).await
}

async fn handle<R>(
    req: Request,
    uc: &ListUsersUseCase<R>,
) -> Result<Response<Body>, Error>
where
    R: feature_admin_rs::domain::repository::AdminRepository,
{
    // Authorisation: must be an admin caller.
    if let Err(e) = claim_sub(&req) {
        return Ok(error_response(e));
    }
    if !is_admin(&req) {
        return Ok(error_response(AppError::Forbidden));
    }

    let qs = req.query_string_parameters_ref();
    let limit: Option<u32> = qs
        .and_then(|q| q.first("limit"))
        .and_then(|s| s.parse().ok());
    let next_token: Option<String> = qs
        .and_then(|q| q.first("next_token"))
        .map(str::to_string);

    match uc.execute(limit, next_token.as_deref()).await {
        Ok(page) => Ok(json_response(200, &page)),
        Err(e)   => Ok(error_response(e)),
    }
}

/// API-Gateway-with-Cognito sets `cognito:groups` either as a comma-separated
/// string in the `x-cognito-groups` header (for HTTP API authorisers) or via
/// the request-context JWT claims (REST API authoriser). Locally the proxy
/// simply forwards `x-admin: true` for tests.
fn is_admin(req: &Request) -> bool {
    if let Some(v) = req.headers().get("x-admin") {
        if v.to_str().map(|s| s.eq_ignore_ascii_case("true")).unwrap_or(false) {
            return true;
        }
    }
    if let Some(v) = req.headers().get("x-cognito-groups") {
        if let Ok(s) = v.to_str() {
            return s.split(',').any(|g| g.trim().eq_ignore_ascii_case("admin"));
        }
    }
    false
}
