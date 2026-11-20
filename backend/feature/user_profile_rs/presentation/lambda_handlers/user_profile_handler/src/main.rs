use lambda_http::{http::Method, run, service_fn, Body, Error, Request, RequestExt, Response};
use serde::Deserialize;
use std::env;

use feature_user_profile_rs::data::datasources::DynamoUserProfileDataSource;
use feature_user_profile_rs::data::repository::DynamoUserProfileRepository;
use feature_user_profile_rs::domain::repository::UserProfileRepository;
use feature_user_profile_rs::domain::usecases::{GetUserProfileUseCase, UpdateUserProfileUseCase};
use shared_common_rs::{claim_sub, error_response, init_tracing, json_response};
use shared_entities_rs::{AppError, UserProfilePatch};

#[derive(Deserialize)]
struct UpdateBody {
    display_name: Option<String>,
    avatar_url: Option<String>,
}

#[tokio::main]
async fn main() -> Result<(), Error> {
    init_tracing();

    let table = env::var("USER_PROFILES_TABLE").expect("USER_PROFILES_TABLE must be set");
    let ddb = shared_database_rs::build_client().await;
    let repo = DynamoUserProfileRepository::new(DynamoUserProfileDataSource::new(ddb, table));
    let get_uc = GetUserProfileUseCase::new(repo.clone());
    let update_uc = UpdateUserProfileUseCase::new(repo);

    run(service_fn(|req: Request| route(req, &get_uc, &update_uc))).await
}

async fn route<R>(
    req: Request,
    get_uc: &GetUserProfileUseCase<R>,
    update_uc: &UpdateUserProfileUseCase<R>,
) -> Result<Response<Body>, Error>
where
    R: UserProfileRepository,
{
    match *req.method() {
        Method::GET => handle_get(req, get_uc).await,
        Method::PATCH => handle_update(req, update_uc).await,
        _ => Ok(error_response(AppError::Validation("method not allowed".into()))),
    }
}

async fn handle_get<R>(
    req: Request,
    uc: &GetUserProfileUseCase<R>,
) -> Result<Response<Body>, Error>
where
    R: UserProfileRepository,
{
    let caller = match claim_sub(&req) {
        Ok(s) => s,
        Err(e) => return Ok(error_response(e)),
    };

    let target = req
        .path_parameters_ref()
        .and_then(|p| p.first("user_id"))
        .map(str::to_string)
        .unwrap_or_else(|| caller.clone());

    if target != caller {
        return Ok(error_response(AppError::Forbidden));
    }

    match uc.execute(&target).await {
        Ok(p) => Ok(json_response(200, &p)),
        Err(e) => Ok(error_response(e)),
    }
}

async fn handle_update<R>(
    req: Request,
    uc: &UpdateUserProfileUseCase<R>,
) -> Result<Response<Body>, Error>
where
    R: UserProfileRepository,
{
    let caller = match claim_sub(&req) {
        Ok(s) => s,
        Err(e) => return Ok(error_response(e)),
    };

    let target = req
        .path_parameters_ref()
        .and_then(|p| p.first("user_id"))
        .map(str::to_string)
        .unwrap_or_else(|| caller.clone());

    let body_bytes = req.body();
    let body: UpdateBody = match serde_json::from_slice(body_bytes.as_ref()) {
        Ok(b) => b,
        Err(_) => return Ok(error_response(AppError::Validation("bad json".into()))),
    };
    let patch = UserProfilePatch {
        display_name: body.display_name,
        avatar_url: body.avatar_url,
    };

    match uc.execute(&caller, &target, patch).await {
        Ok(p) => Ok(json_response(200, &p)),
        Err(e) => Ok(error_response(e)),
    }
}
