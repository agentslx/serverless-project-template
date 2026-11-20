//! Python-language dispatcher — forwards the request to `local_proxy_py`
//! over HTTP. The Python sub-server reads the same `routes.json` and mounts
//! its own handlers; from the FE's perspective there is one URL.

use std::collections::HashMap;

use crate::proxy_types::{ProxyRequest, ProxyResponse};
use crate::state::AppState;

pub async fn forward(
    state: AppState,
    req: ProxyRequest,
) -> Result<ProxyResponse, anyhow::Error> {
    let url = format!("{}{}", state.python_subserver_url, req.path);
    let method = reqwest::Method::from_bytes(req.method.as_bytes())
        .unwrap_or(reqwest::Method::GET);

    let mut builder = state.http.request(method, &url);
    if !req.query_params.is_empty() {
        let qp: Vec<(&String, &String)> = req.query_params.iter().collect();
        builder = builder.query(&qp);
    }
    for (k, v) in req.headers.iter() {
        // Drop hop-by-hop headers.
        if k == "host" || k == "content-length" || k == "connection" {
            continue;
        }
        builder = builder.header(k, v);
    }
    if !req.body.is_empty() {
        builder = builder.body(req.body);
    }

    let resp = builder.send().await
        .map_err(|e| anyhow::anyhow!("python sub-server unreachable: {e}"))?;

    let status = resp.status().as_u16();
    let mut headers: HashMap<String, String> = HashMap::new();
    for (k, v) in resp.headers().iter() {
        if let Ok(vs) = v.to_str() {
            headers.insert(k.as_str().to_lowercase(), vs.to_string());
        }
    }
    let body = resp.bytes().await.map(|b| b.to_vec()).unwrap_or_default();

    Ok(ProxyResponse { status, headers, body })
}
