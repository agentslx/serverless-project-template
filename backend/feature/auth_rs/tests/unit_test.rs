//! Unit tests for feature_auth_rs.

use async_trait::async_trait;
use feature_auth_rs::domain::repository::AuthRepository;
use feature_auth_rs::domain::usecases::{GetMeUseCase, PostConfirmationUseCase};
use shared_entities_rs::{AppError, UserProfile};
use std::sync::{Arc, Mutex};

struct FakeRepo {
    calls: Arc<Mutex<Vec<(String, String)>>>,
    fail: bool,
}

#[async_trait]
impl AuthRepository for FakeRepo {
    async fn get_or_create_profile(
        &self,
        user_id: &str,
        email: &str,
    ) -> Result<UserProfile, AppError> {
        self.calls
            .lock()
            .unwrap()
            .push((user_id.into(), email.into()));
        if self.fail {
            Err(AppError::Internal("boom".into()))
        } else {
            Ok(UserProfile::new(user_id, email, "User"))
        }
    }
}

#[tokio::test]
async fn get_me_returns_entity() {
    let calls = Arc::new(Mutex::new(vec![]));
    let uc = GetMeUseCase::new(FakeRepo { calls: calls.clone(), fail: false });
    let p = uc.execute("u1", "a@b.c").await.unwrap();
    assert_eq!(p.user_id, "u1");
    assert_eq!(calls.lock().unwrap().len(), 1);
}

#[tokio::test]
async fn get_me_rejects_empty_sub() {
    let calls = Arc::new(Mutex::new(vec![]));
    let uc = GetMeUseCase::new(FakeRepo { calls, fail: false });
    let r = uc.execute("", "a@b.c").await;
    assert!(matches!(r, Err(AppError::Unauthorised)));
}

#[tokio::test]
async fn post_confirmation_is_idempotent() {
    let calls = Arc::new(Mutex::new(vec![]));
    let uc = PostConfirmationUseCase::new(FakeRepo { calls: calls.clone(), fail: false });
    uc.execute("u1", "a@b.c").await.unwrap();
    uc.execute("u1", "a@b.c").await.unwrap();
    assert_eq!(calls.lock().unwrap().len(), 2); // both calls hit repo
}
