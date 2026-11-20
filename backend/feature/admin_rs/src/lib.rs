//! Feature: admin.
//!
//! Owns admin-only operations against the `user_profiles` table:
//! - `list_users` (paginated scan)
//!
//! Auth model: every entry-point (Lambda binary, AppSync resolver, local-proxy
//! handler) is responsible for *first* verifying that the caller has the
//! `admin` Cognito group. The usecases here trust their input and focus on
//! correctness (pagination shape, max page size, etc.).
//!
//! Presentation lives under `presentation/lambda_handlers/list_users/`
//! (Rust binary) and `presentation/graphql_resolvers/listUsers.js`
//! (AppSync JS resolver, served by the admin AppSync API).

pub mod data;
pub mod domain;
