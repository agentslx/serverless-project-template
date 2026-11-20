//! routes.json loader.

use serde::Deserialize;
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Language {
    Rust,
    Python,
}

#[derive(Debug, Clone, Deserialize)]
pub struct RouteEntry {
    pub method: String,
    pub path: String,
    pub handler: String,
    pub language: Language,
}

#[derive(Debug, Clone, Deserialize)]
pub struct RoutesConfig {
    #[serde(default = "default_python_url")]
    pub python_subserver_url: String,
    pub routes: Vec<RouteEntry>,
}

fn default_python_url() -> String {
    "http://localhost:9001".to_string()
}

pub fn load_routes(path: impl AsRef<Path>) -> Result<RoutesConfig, String> {
    let bytes = fs::read(path.as_ref())
        .map_err(|e| format!("read {}: {}", path.as_ref().display(), e))?;
    serde_json::from_slice::<RoutesConfig>(&bytes).map_err(|e| format!("parse routes.json: {e}"))
}
