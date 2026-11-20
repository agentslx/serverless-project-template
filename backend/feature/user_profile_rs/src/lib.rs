//! Feature: user_profile.
//!
//! Owns:
//! - read & update for the current user's profile (Lambda)
//! - JS resolvers under presentation/graphql_resolvers/ (live alongside, but
//!   are not Rust — they're TypeScript-flavoured JS executed by AppSync).

pub mod data;
pub mod domain;
