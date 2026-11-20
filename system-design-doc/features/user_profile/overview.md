# Feature · user_profile

## Goal
Read and update the current user's profile.

| Operation         | Path                                | Auth                |
|-------------------|-------------------------------------|---------------------|
| `getUserProfile`  | AppSync JS resolver → DynamoDB      | Cognito user pool   |
| `updateUserProfile` | AppSync pipeline → Lambda → DDB   | Cognito user pool   |
| `adminListProfiles` | AppSync → Lambda → DDB Scan       | Cognito admin pool  |

## Lambda structure

A single consolidated Lambda (`handler_user_profile`) serves both GET and PATCH operations via HTTP method routing. The AppSync `updateUserProfile` mutation also invokes this same Lambda. This maximises warm-container reuse — a user fetching their profile warms the container for subsequent profile updates.

The handler initialises one DynamoDB client + repository at cold start, then branches by HTTP method to the appropriate use case.

## Entity

```rust
// shared/entities/src/user_profile.rs
pub struct UserProfile {
    pub user_id: String,        // == Cognito sub
    pub email: String,
    pub display_name: String,
    pub avatar_url: Option<String>,
    pub created_at: String,     // ISO-8601
    pub updated_at: String,
}
```

## Why a JS resolver for read (AppSync path)?

`getUserProfile` is hot. AppSync JS resolvers run inside AppSync — sub-millisecond, no Lambda cold start, no IAM-on-the-fly. The only logic is "GetItem by `user_id` from JWT sub". Perfect fit.

## Why a Lambda for write?

Updates need:
- field-level validation
- enforcement that `user_id` from path == JWT `sub` (cannot change someone else's row)
- `updated_at = now()` audit
- (future) emit a `ProfileUpdated` EventBridge event

Putting that in JS resolvers gets unwieldy fast.
