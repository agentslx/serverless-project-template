use serde::{Deserialize, Serialize};

/// Domain entity representing a user's profile.
///
/// Used by every layer (presentation, domain, data). Knows nothing about
/// DynamoDB / JSON-API / GraphQL — those concerns live in `data/models/`.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct UserProfile {
    pub user_id: String,
    pub email: String,
    pub display_name: String,
    pub avatar_url: Option<String>,
    /// ISO-8601 UTC string.
    pub created_at: String,
    pub updated_at: String,
}

/// A patch object — every field optional. Used for `update_profile`.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct UserProfilePatch {
    pub display_name: Option<String>,
    pub avatar_url: Option<String>,
}

impl UserProfile {
    pub fn new(user_id: impl Into<String>, email: impl Into<String>, display_name: impl Into<String>) -> Self {
        let now = chrono::Utc::now().to_rfc3339();
        Self {
            user_id: user_id.into(),
            email: email.into(),
            display_name: display_name.into(),
            avatar_url: None,
            created_at: now.clone(),
            updated_at: now,
        }
    }

    pub fn apply_patch(mut self, patch: UserProfilePatch) -> Self {
        if let Some(d) = patch.display_name {
            self.display_name = d;
        }
        if let Some(a) = patch.avatar_url {
            self.avatar_url = Some(a);
        }
        self.updated_at = chrono::Utc::now().to_rfc3339();
        self
    }

    pub fn to_json(&self) -> serde_json::Value {
        serde_json::to_value(self).unwrap_or(serde_json::Value::Null)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn apply_patch_sets_only_provided_fields() {
        let p = UserProfile::new("u1", "a@b.c", "Old");
        let patched = p.clone().apply_patch(UserProfilePatch {
            display_name: Some("New".into()),
            avatar_url: None,
        });
        assert_eq!(patched.display_name, "New");
        assert_eq!(patched.avatar_url, None);
        assert_eq!(patched.user_id, p.user_id);
    }
}
