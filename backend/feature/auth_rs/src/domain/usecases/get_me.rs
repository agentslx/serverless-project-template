use crate::domain::repository::AuthRepository;
use shared_entities_rs::{AppError, UserProfile};

/// `GetMe` — fetches the current user's profile, lazily creating one if
/// missing (e.g. user signed up before the trigger Lambda existed).
pub struct GetMeUseCase<R: AuthRepository> {
    repo: R,
}

impl<R: AuthRepository> GetMeUseCase<R> {
    pub fn new(repo: R) -> Self {
        Self { repo }
    }

    pub async fn execute(&self, user_id: &str, email: &str) -> Result<UserProfile, AppError> {
        if user_id.is_empty() {
            return Err(AppError::Unauthorised);
        }
        self.repo.get_or_create_profile(user_id, email).await
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use async_trait::async_trait;

    struct Stub;

    #[async_trait]
    impl AuthRepository for Stub {
        async fn get_or_create_profile(
            &self,
            user_id: &str,
            email: &str,
        ) -> Result<UserProfile, AppError> {
            Ok(UserProfile::new(user_id, email, "User"))
        }
    }

    #[tokio::test]
    async fn returns_entity() {
        let uc = GetMeUseCase::new(Stub);
        let p = uc.execute("u-1", "a@b.c").await.unwrap();
        assert_eq!(p.user_id, "u-1");
        assert_eq!(p.email, "a@b.c");
    }

    #[tokio::test]
    async fn rejects_empty_user_id() {
        let uc = GetMeUseCase::new(Stub);
        assert!(matches!(uc.execute("", "a@b.c").await, Err(AppError::Unauthorised)));
    }
}
