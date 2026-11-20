//! Lightweight, language-agnostic request/response types used inside the proxy.
//! These are independent from `lambda_http` so the same handlers can be
//! invoked locally without a Lambda runtime.

use std::collections::HashMap;

#[derive(Debug)]
pub struct ProxyRequest {
    pub method: String,
    pub path: String,
    pub headers: HashMap<String, String>,
    pub path_params: HashMap<String, String>,
    pub query_params: HashMap<String, String>,
    pub body: Vec<u8>,
}

#[derive(Debug)]
pub struct ProxyResponse {
    pub status: u16,
    pub headers: HashMap<String, String>,
    pub body: Vec<u8>,
}

impl ProxyResponse {
    pub fn json<T: serde::Serialize>(status: u16, body: &T) -> Self {
        let bytes = serde_json::to_vec(body).unwrap_or_else(|_| b"{}".to_vec());
        let mut h = HashMap::new();
        h.insert("content-type".into(), "application/json".into());
        Self { status, headers: h, body: bytes }
    }

    pub fn error(status: u16, message: &str) -> Self {
        Self::json(status, &serde_json::json!({ "error": message }))
    }
}
