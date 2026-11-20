//! Local proxy — single FE entrypoint, language-agnostic.
//!
//! Routes are declared in `routes.json` (sibling of this binary). Each entry
//! says whether the handler runs in-process as Rust (linked at compile time)
//! or is forwarded over HTTP to the Python sub-server (`local_proxy_py`).
//!
//! See AGENTS.md §10 ("routes.json convention") for the workflow when
//! adding a new route.

mod config;
mod dispatch_py;
mod dispatch_rs;
mod handlers;
mod proxy_types;
mod router;
mod state;

use std::env;
use std::net::SocketAddr;

use axum::Router;
use tower_http::cors::{Any, CorsLayer};
use tower_http::trace::TraceLayer;
use tracing::info;

use crate::config::load_routes;
use crate::router::build_dispatcher;
use crate::state::AppStateInner;

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter(env::var("LOG_LEVEL").unwrap_or_else(|_| "info".into()))
        .init();

    // 1. Load routes.json (path is alongside the binary at workspace root).
    let routes_path = env::var("ROUTES_JSON")
        .unwrap_or_else(|_| "local_proxy/routes.json".into());
    let cfg = load_routes(&routes_path).expect("failed to load routes.json");
    info!(routes = cfg.routes.len(), "routes loaded from {}", routes_path);

    // 2. Build app state (in-process handler context: usecases, http client).
    let state = AppStateInner::build(&cfg).await;

    // 3. Build the axum router with a dynamic dispatcher fallback.
    let app = Router::new()
        .fallback(build_dispatcher())
        .with_state(state)
        .layer(CorsLayer::new().allow_origin(Any).allow_methods(Any).allow_headers(Any))
        .layer(TraceLayer::new_for_http());

    let port: u16 = env::var("PORT").ok().and_then(|s| s.parse().ok()).unwrap_or(9000);
    let addr = SocketAddr::from(([0, 0, 0, 0], port));
    info!(%addr, "local_proxy listening (RS in-process + PY via subserver)");

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
