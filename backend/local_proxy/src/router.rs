//! Path-pattern → RouteEntry router, plus the axum fallback handler.

use std::collections::HashMap;

use axum::body::{to_bytes, Body};
use axum::extract::{Request, State};
use axum::http::{HeaderMap, Method, StatusCode};
use axum::response::Response;
use matchit::Router as Matcher;
use tracing::warn;

use crate::config::{Language, RouteEntry, RoutesConfig};
use crate::proxy_types::{ProxyRequest, ProxyResponse};
use crate::state::AppState;
use crate::{dispatch_py, dispatch_rs};

/// One `matchit` trie per HTTP method.
#[derive(Default)]
pub struct RouteTable {
    pub get: Matcher<RouteEntry>,
    pub post: Matcher<RouteEntry>,
    pub put: Matcher<RouteEntry>,
    pub patch: Matcher<RouteEntry>,
    pub delete: Matcher<RouteEntry>,
}

impl RouteTable {
    pub fn from_config(cfg: &RoutesConfig) -> Result<Self, String> {
        let mut t = RouteTable::default();
        for r in &cfg.routes {
            let trie = match r.method.to_uppercase().as_str() {
                "GET" => &mut t.get,
                "POST" => &mut t.post,
                "PUT" => &mut t.put,
                "PATCH" => &mut t.patch,
                "DELETE" => &mut t.delete,
                other => return Err(format!("unsupported method {other}")),
            };
            trie.insert(r.path.clone(), r.clone())
                .map_err(|e| format!("route {} {}: {e}", r.method, r.path))?;
        }
        Ok(t)
    }

    pub fn lookup<'a>(
        &'a self,
        method: &Method,
        path: &'a str,
    ) -> Option<(&'a RouteEntry, HashMap<String, String>)> {
        let trie = match *method {
            Method::GET => &self.get,
            Method::POST => &self.post,
            Method::PUT => &self.put,
            Method::PATCH => &self.patch,
            Method::DELETE => &self.delete,
            _ => return None,
        };
        let m = trie.at(path).ok()?;
        let params = m.params.iter()
            .map(|(k, v)| (k.to_string(), v.to_string()))
            .collect::<HashMap<_, _>>();
        Some((m.value, params))
    }
}

/// axum fallback handler — dispatches every request through routes.json.
pub fn build_dispatcher() -> impl Fn(State<AppState>, Request) -> std::pin::Pin<Box<dyn std::future::Future<Output = Response> + Send>> + Clone + Send + 'static
{
    move |State(state), req: Request| {
        Box::pin(async move {
            let (parts, body) = req.into_parts();
            let path = parts.uri.path().to_string();
            let query_params = parse_query(parts.uri.query().unwrap_or(""));
            let method = parts.method.clone();

            let Some((entry, path_params)) = state.routes.lookup(&method, &path) else {
                return into_response(ProxyResponse::error(404, "route not found"));
            };

            let body_bytes = to_bytes(body, 8 * 1024 * 1024)
                .await
                .map(|b| b.to_vec())
                .unwrap_or_default();

            let proxy_req = ProxyRequest {
                method: method.to_string(),
                path: path.clone(),
                headers: header_map_to_hashmap(&parts.headers),
                path_params,
                query_params,
                body: body_bytes,
            };

            let result = match entry.language {
                Language::Rust => dispatch_rs::dispatch(&entry.handler, state.clone(), proxy_req).await,
                Language::Python => dispatch_py::forward(state.clone(), proxy_req).await,
            };

            match result {
                Ok(r) => into_response(r),
                Err(e) => {
                    warn!(handler = %entry.handler, ?e, "handler failed");
                    into_response(ProxyResponse::error(500, &e.to_string()))
                }
            }
        })
    }
}

fn header_map_to_hashmap(h: &HeaderMap) -> HashMap<String, String> {
    h.iter()
        .filter_map(|(k, v)| v.to_str().ok().map(|v| (k.as_str().to_lowercase(), v.to_string())))
        .collect()
}

/// Minimal `?a=1&b=2` parser. Last-write-wins on duplicate keys (matches the
/// behaviour of `req.query_string_parameters_ref().first(...)` in lambda_http).
fn parse_query(q: &str) -> HashMap<String, String> {
    let mut out = HashMap::new();
    if q.is_empty() {
        return out;
    }
    for pair in q.split('&') {
        if pair.is_empty() {
            continue;
        }
        let (k, v) = match pair.split_once('=') {
            Some((k, v)) => (k, v),
            None => (pair, ""),
        };
        out.insert(url_decode(k), url_decode(v));
    }
    out
}

fn url_decode(s: &str) -> String {
    let mut out = Vec::with_capacity(s.len());
    let bytes = s.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        match bytes[i] {
            b'+' => { out.push(b' '); i += 1; }
            b'%' if i + 2 < bytes.len() => {
                let hi = (bytes[i + 1] as char).to_digit(16);
                let lo = (bytes[i + 2] as char).to_digit(16);
                if let (Some(h), Some(l)) = (hi, lo) {
                    out.push((h * 16 + l) as u8);
                    i += 3;
                } else {
                    out.push(bytes[i]); i += 1;
                }
            }
            b => { out.push(b); i += 1; }
        }
    }
    String::from_utf8(out).unwrap_or_default()
}

fn into_response(r: ProxyResponse) -> Response {
    let mut builder = Response::builder().status(StatusCode::from_u16(r.status).unwrap_or(StatusCode::INTERNAL_SERVER_ERROR));
    for (k, v) in r.headers.iter() {
        builder = builder.header(k, v);
    }
    builder.body(Body::from(r.body)).expect("infallible")
}
