//! Feature: auth.
//!
//! - domain      — pure logic + repository traits
//! - data        — DynamoDB-backed repository for the user_profile row
//!                 created on Cognito post-confirmation
//! - presentation— see ./presentation/lambda_handlers/*

pub mod data;
pub mod domain;
