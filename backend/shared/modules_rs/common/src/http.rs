use lambda_http::{Body, Request, Response};
use shared_entities_rs::AppError;

pub fn json_response<T: serde::Serialize>(status: u16, body: &T) -> Response<Body> {
    let json = serde_json::to_string(body).unwrap_or_else(|_| "{}".into());
    Response::builder()
        .status(status)
        .header("content-type", "application/json")
        .header("access-control-allow-origin", "*")
        .body(Body::Text(json))
        .expect("infallible")
}

pub fn error_response(err: AppError) -> Response<Body> {
    json_response(
        err.http_status(),
        &serde_json::json!({ "error": err.to_string() }),
    )
}

/// Extract the Cognito `sub` claim from the incoming request.
///
/// Strategy (in order):
/// 1. `x-user-sub` header — set by the local proxy in dev or by an API GW
///    request mapping in prod.
/// 2. Decode the JWT in `Authorization: Bearer ...`. We *don't* verify the
///    signature here — that is done upstream by Cognito Authoriser /
///    AppSync. This is just for claim extraction.
pub fn claim_sub(req: &Request) -> Result<String, AppError> {
    if let Some(h) = req.headers().get("x-user-sub").and_then(|v| v.to_str().ok()) {
        if !h.is_empty() {
            return Ok(h.to_string());
        }
    }

    let auth = req
        .headers()
        .get("authorization")
        .and_then(|v| v.to_str().ok())
        .ok_or(AppError::Unauthorised)?;
    let token = auth.strip_prefix("Bearer ").ok_or(AppError::Unauthorised)?;
    let payload = token.split('.').nth(1).ok_or(AppError::Unauthorised)?;

    use base64::engine::general_purpose::URL_SAFE_NO_PAD;
    use base64::Engine;
    let decoded = URL_SAFE_NO_PAD
        .decode(payload)
        .map_err(|_| AppError::Unauthorised)?;
    let claims: serde_json::Value =
        serde_json::from_slice(&decoded).map_err(|_| AppError::Unauthorised)?;

    claims
        .get("sub")
        .and_then(|v| v.as_str())
        .map(str::to_string)
        .ok_or(AppError::Unauthorised)
}
