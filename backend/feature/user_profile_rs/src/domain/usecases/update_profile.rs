use crate::domain::repository::UserProfileRepository;
use shared_entities_rs::{AppError, UserProfile, UserProfilePatch};

pub struct UpdateUserProfileUseCase<R: UserProfileRepository> {
    repo: R,
}

impl<R: UserProfileRepository> UpdateUserProfileUseCase<R> {
    pub fn new(repo: R) -> Self { Self { repo } }

    pub async fn execute(
        &self,
        caller_user_id: &str,
        target_user_id: &str,
        patch: UserProfilePatch,
    ) -> Result<UserProfile, AppError> {
        if caller_user_id != target_user_id {
            return Err(AppError::Forbidden);
        }
        if let Some(name) = &patch.display_name {
            if name.trim().len() < 2 {
                return Err(AppError::Validation("display_name must be ≥ 2 chars".into()));
            }
        }
        self.repo.update(target_user_id, &patch).await
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use async_trait::async_trait;

    struct Fake;

    #[async_trait]
    impl UserProfileRepository for Fake {
        async fn find_by_id(&self, _u: &str) -> Result<Option<UserProfile>, AppError> {
            Ok(None)
        }
        async fn update(&self, u: &str, p: &UserProfilePatch) -> Result<UserProfile, AppError> {
            Ok(UserProfile::new(u, "x@y.z", p.display_name.clone().unwrap_or_default()))
        }
    }

    #[tokio::test]
    async fn rejects_mismatched_caller() {
        let uc = UpdateUserProfileUseCase::new(Fake);
        let r = uc.execute("u1", "u2", UserProfilePatch::default()).await;
        assert!(matches!(r, Err(AppError::Forbidden)));
    }

    #[tokio::test]
    async fn rejects_short_display_name() {
        let uc = UpdateUserProfileUseCase::new(Fake);
        let r = uc.execute("u1", "u1", UserProfilePatch { display_name: Some("a".into()), avatar_url: None }).await;
        assert!(matches!(r, Err(AppError::Validation(_))));
    }
}
