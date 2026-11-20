//! Concrete Rust handler functions. Every entry registered in
//! `dispatch_rs::dispatch` lives here.

use serde::Deserialize;

use shared_entities_rs::UserProfilePatch;

use crate::proxy_types::{ProxyRequest, ProxyResponse};
use crate::state::AppState;

fn sub(req: &ProxyRequest) -> Option<String> {
    req.headers.get("x-user-sub").filter(|s| !s.is_empty()).cloned()
}

fn email(req: &ProxyRequest) -> String {
    req.headers.get("x-user-email").cloned().unwrap_or_default()
}

pub async fn get_me(
    state: AppState,
    req: ProxyRequest,
) -> Result<ProxyResponse, anyhow::Error> {
    let Some(sub) = sub(&req) else {
        return Ok(ProxyResponse::error(401, "missing x-user-sub"));
    };
    let entity = state.get_me.execute(&sub, &email(&req)).await?;
    Ok(ProxyResponse::json(200, &entity))
}

pub async fn get_profile(
    state: AppState,
    req: ProxyRequest,
) -> Result<ProxyResponse, anyhow::Error> {
    let Some(sub) = sub(&req) else {
        return Ok(ProxyResponse::error(401, "missing x-user-sub"));
    };
    let target = req.path_params.get("user_id").cloned().unwrap_or_else(|| sub.clone());
    if target != sub {
        return Ok(ProxyResponse::error(403, "forbidden"));
    }
    let entity = state.get_profile.execute(&target).await?;
    Ok(ProxyResponse::json(200, &entity))
}

#[derive(Deserialize)]
struct UpdateBody {
    display_name: Option<String>,
    avatar_url: Option<String>,
}

pub async fn update_profile(
    state: AppState,
    req: ProxyRequest,
) -> Result<ProxyResponse, anyhow::Error> {
    let Some(sub) = sub(&req) else {
        return Ok(ProxyResponse::error(401, "missing x-user-sub"));
    };
    let target = req.path_params.get("user_id").cloned().unwrap_or_else(|| sub.clone());

    let body: UpdateBody = match serde_json::from_slice(&req.body) {
        Ok(b) => b,
        Err(_) => return Ok(ProxyResponse::error(400, "bad json")),
    };
    let patch = UserProfilePatch {
        display_name: body.display_name,
        avatar_url: body.avatar_url,
    };

    let entity = state.update_profile.execute(&sub, &target, patch).await?;
    Ok(ProxyResponse::json(200, &entity))
}

/// Admin-only — caller must present `x-admin: true` (locally) or come through
/// API Gateway with `cognito:groups` containing `"admin"` (forwarded as
/// `x-cognito-groups`).
pub async fn list_users(
    state: AppState,
    req: ProxyRequest,
) -> Result<ProxyResponse, anyhow::Error> {
    if sub(&req).is_none() {
        return Ok(ProxyResponse::error(401, "missing x-user-sub"));
    }
    if !is_admin(&req) {
        return Ok(ProxyResponse::error(403, "admin only"));
    }

    let limit: Option<u32> = req
        .query_params
        .get("limit")
        .and_then(|s| s.parse().ok());
    let next_token: Option<String> = req.query_params.get("next_token").cloned();

    let page = state.list_users.execute(limit, next_token.as_deref()).await?;
    Ok(ProxyResponse::json(200, &page))
}

fn is_admin(req: &ProxyRequest) -> bool {
    if let Some(v) = req.headers.get("x-admin") {
        if v.eq_ignore_ascii_case("true") {
            return true;
        }
    }
    if let Some(v) = req.headers.get("x-cognito-groups") {
        return v.split(',').any(|g| g.trim().eq_ignore_ascii_case("admin"));
    }
    false
}
