use crate::domain::repository::{AdminRepository, ListUsersPage};
use shared_entities_rs::AppError;

/// Page-size guardrails. Keeping these in the usecase (not the data layer)
/// because they're a *business* rule about what an admin can see.
const DEFAULT_LIMIT: u32 = 20;
const MAX_LIMIT: u32 = 100;

pub struct ListUsersUseCase<R: AdminRepository> {
    repo: R,
}

impl<R: AdminRepository> ListUsersUseCase<R> {
    pub fn new(repo: R) -> Self { Self { repo } }

    /// `limit` is clamped to `[1, MAX_LIMIT]` (default `DEFAULT_LIMIT` if `None`).
    pub async fn execute(
        &self,
        limit: Option<u32>,
        next_token: Option<&str>,
    ) -> Result<ListUsersPage, AppError> {
        let limit = match limit {
            None => DEFAULT_LIMIT,
            Some(0) => return Err(AppError::Validation("limit must be ≥ 1".into())),
            Some(n) => n.min(MAX_LIMIT),
        };
        self.repo.list_users(limit, next_token).await
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use async_trait::async_trait;
    use shared_entities_rs::UserProfile;

    struct Fake {
        last_limit: std::sync::Mutex<u32>,
    }

    #[async_trait]
    impl AdminRepository for Fake {
        async fn list_users(
            &self,
            limit: u32,
            _next_token: Option<&str>,
        ) -> Result<ListUsersPage, AppError> {
            *self.last_limit.lock().unwrap() = limit;
            Ok(ListUsersPage {
                users: vec![UserProfile::new("u1", "a@b.c", "Alice")],
                next_token: None,
            })
        }
    }

    fn fake() -> Fake { Fake { last_limit: std::sync::Mutex::new(0) } }

    #[tokio::test]
    async fn applies_default_limit() {
        let f = fake();
        let last = std::sync::Mutex::new(0);
        // Wrap the wrapper with a closure-style check by inspecting after.
        let uc = ListUsersUseCase::new(WrapFake(f, &last));
        let _ = uc.execute(None, None).await.unwrap();
        assert_eq!(*last.lock().unwrap(), DEFAULT_LIMIT);
    }

    #[tokio::test]
    async fn clamps_to_max_limit() {
        let f = fake();
        let last = std::sync::Mutex::new(0);
        let uc = ListUsersUseCase::new(WrapFake(f, &last));
        let _ = uc.execute(Some(99_999), None).await.unwrap();
        assert_eq!(*last.lock().unwrap(), MAX_LIMIT);
    }

    #[tokio::test]
    async fn rejects_zero_limit() {
        let uc = ListUsersUseCase::new(fake());
        let r = uc.execute(Some(0), None).await;
        assert!(matches!(r, Err(AppError::Validation(_))));
    }

    // ---- helper that lets the test inspect the limit Fake saw ----
    struct WrapFake<'a>(Fake, &'a std::sync::Mutex<u32>);

    #[async_trait]
    impl<'a> AdminRepository for WrapFake<'a> {
        async fn list_users(
            &self,
            limit: u32,
            next_token: Option<&str>,
        ) -> Result<ListUsersPage, AppError> {
            *self.1.lock().unwrap() = limit;
            self.0.list_users(limit, next_token).await
        }
    }
}
