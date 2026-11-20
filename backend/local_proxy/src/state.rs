//! Shared application state — built once at startup and cloned into every
//! request handler.

use std::env;
use std::sync::Arc;

use feature_auth_rs::data::datasources::DynamoUserProfileDataSource as AuthDS;
use feature_auth_rs::data::repository::DynamoAuthRepository;
use feature_auth_rs::domain::usecases::GetMeUseCase;

use feature_user_profile_rs::data::datasources::DynamoUserProfileDataSource as UpDS;
use feature_user_profile_rs::data::repository::DynamoUserProfileRepository;
use feature_user_profile_rs::domain::usecases::{GetUserProfileUseCase, UpdateUserProfileUseCase};

use feature_admin_rs::data::datasources::DynamoAdminDataSource;
use feature_admin_rs::data::repository::DynamoAdminRepository;
use feature_admin_rs::domain::usecases::ListUsersUseCase;

use crate::config::RoutesConfig;
use crate::router::RouteTable;

pub type AppState = Arc<AppStateInner>;

pub struct AppStateInner {
    /// Pre-built in-process Rust usecases.
    pub get_me: GetMeUseCase<DynamoAuthRepository>,
    pub get_profile: GetUserProfileUseCase<DynamoUserProfileRepository>,
    pub update_profile: UpdateUserProfileUseCase<DynamoUserProfileRepository>,
    pub list_users: ListUsersUseCase<DynamoAdminRepository>,

    /// HTTP client used to forward Python-language routes.
    pub http: reqwest::Client,
    pub python_subserver_url: String,

    /// Match-trie built from routes.json.
    pub routes: RouteTable,
}

impl AppStateInner {
    pub async fn build(cfg: &RoutesConfig) -> AppState {
        let table = env::var("USER_PROFILES_TABLE")
            .unwrap_or_else(|_| "est-dev-user-profiles".into());

        let ddb = shared_database_rs::build_client().await;

        let auth_repo = DynamoAuthRepository::new(AuthDS::new(ddb.clone(), table.clone()));
        let profile_repo_get = DynamoUserProfileRepository::new(UpDS::new(ddb.clone(), table.clone()));
        let profile_repo_upd = DynamoUserProfileRepository::new(UpDS::new(ddb.clone(), table.clone()));
        let admin_repo = DynamoAdminRepository::new(DynamoAdminDataSource::new(ddb, table));

        Arc::new(AppStateInner {
            get_me:         GetMeUseCase::new(auth_repo),
            get_profile:    GetUserProfileUseCase::new(profile_repo_get),
            update_profile: UpdateUserProfileUseCase::new(profile_repo_upd),
            list_users:     ListUsersUseCase::new(admin_repo),

            http: reqwest::Client::builder().build().expect("reqwest client"),
            python_subserver_url: cfg.python_subserver_url.clone(),

            routes: RouteTable::from_config(cfg).expect("invalid routes.json"),
        })
    }
}
