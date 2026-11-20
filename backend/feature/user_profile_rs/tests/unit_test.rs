//! Unit tests for feature_user_profile_rs.

use async_trait::async_trait;
use feature_user_profile_rs::domain::repository::UserProfileRepository;
use feature_user_profile_rs::domain::usecases::{GetUserProfileUseCase, UpdateUserProfileUseCase};
use shared_entities_rs::{AppError, UserProfile, UserProfilePatch};

struct Stub {
    found: Option<UserProfile>,
}

#[async_trait]
impl UserProfileRepository for Stub {
    async fn find_by_id(&self, _u: &str) -> Result<Option<UserProfile>, AppError> {
        Ok(self.found.clone())
    }
    async fn update(&self, u: &str, p: &UserProfilePatch) -> Result<UserProfile, AppError> {
        Ok(UserProfile::new(u, "a@b.c", p.display_name.clone().unwrap_or_else(|| "X".into())))
    }
}

#[tokio::test]
async fn get_profile_happy() {
    let p = UserProfile::new("u1", "a@b.c", "Alice");
    let uc = GetUserProfileUseCase::new(Stub { found: Some(p.clone()) });
    let r = uc.execute("u1").await.unwrap();
    assert_eq!(r, p);
}

#[tokio::test]
async fn get_profile_not_found() {
    let uc = GetUserProfileUseCase::new(Stub { found: None });
    let r = uc.execute("u1").await;
    assert!(matches!(r, Err(AppError::NotFound)));
}

#[tokio::test]
async fn update_profile_happy() {
    let uc = UpdateUserProfileUseCase::new(Stub { found: None });
    let r = uc
        .execute(
            "u1",
            "u1",
            UserProfilePatch { display_name: Some("Alice".into()), avatar_url: None },
        )
        .await
        .unwrap();
    assert_eq!(r.display_name, "Alice");
}

#[tokio::test]
async fn update_profile_forbidden() {
    let uc = UpdateUserProfileUseCase::new(Stub { found: None });
    let r = uc.execute("u1", "u2", UserProfilePatch::default()).await;
    assert!(matches!(r, Err(AppError::Forbidden)));
}
