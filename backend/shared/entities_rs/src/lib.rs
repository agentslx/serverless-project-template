//! Plain entity types shared across features.
//!
//! ⚠️  No infrastructure imports allowed here. Specifically: no `aws-sdk-*`,
//!     no DynamoDB attribute types, no HTTP types. Just plain data shapes.

pub mod app_error;
pub mod user_profile;

pub use app_error::AppError;
pub use user_profile::{UserProfile, UserProfilePatch};
