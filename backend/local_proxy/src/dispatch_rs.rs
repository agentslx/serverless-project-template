//! Rust-language dispatcher.
//!
//! Each Rust handler from `routes.json` is bound here in a single `match`.
//! Adding a handler is a one-line change — see AGENTS.md §10.

use crate::handlers;
use crate::proxy_types::{ProxyRequest, ProxyResponse};
use crate::state::AppState;

pub async fn dispatch(
    handler_name: &str,
    state: AppState,
    req: ProxyRequest,
) -> Result<ProxyResponse, anyhow::Error> {
    match handler_name {
        "get_me"          => handlers::get_me(state, req).await,
        "get_profile"     => handlers::get_profile(state, req).await,
        "update_profile"  => handlers::update_profile(state, req).await,
        "list_users"      => handlers::list_users(state, req).await,
        other => Ok(ProxyResponse::error(
            500,
            &format!("rust handler '{other}' not registered in dispatch_rs.rs"),
        )),
    }
}
