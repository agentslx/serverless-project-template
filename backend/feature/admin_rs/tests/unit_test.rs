//! Unit tests for feature_admin_rs.

use async_trait::async_trait;
use feature_admin_rs::domain::repository::{AdminRepository, ListUsersPage};
use feature_admin_rs::domain::usecases::ListUsersUseCase;
use shared_entities_rs::{AppError, UserProfile};

struct Stub {
    page: ListUsersPage,
}

#[async_trait]
impl AdminRepository for Stub {
    async fn list_users(
        &self,
        _limit: u32,
        _next_token: Option<&str>,
    ) -> Result<ListUsersPage, AppError> {
        Ok(self.page.clone())
    }
}

#[tokio::test]
async fn list_users_returns_page() {
    let p = ListUsersPage {
        users: vec![
            UserProfile::new("u1", "a@b.c", "Alice"),
            UserProfile::new("u2", "b@b.c", "Bob"),
        ],
        next_token: Some("tok".into()),
    };
    let uc = ListUsersUseCase::new(Stub { page: p.clone() });
    let r = uc.execute(Some(50), None).await.unwrap();
    assert_eq!(r.users.len(), 2);
    assert_eq!(r.next_token, Some("tok".into()));
}

#[tokio::test]
async fn list_users_zero_limit_rejected() {
    let uc = ListUsersUseCase::new(Stub {
        page: ListUsersPage { users: vec![], next_token: None },
    });
    let r = uc.execute(Some(0), None).await;
    assert!(matches!(r, Err(AppError::Validation(_))));
}
