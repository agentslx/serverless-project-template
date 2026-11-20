# user_profile · flows

## Read (no Lambda)

```
React (ProfilePage)
   │  generateClient().graphql({ query: getUserProfile, variables: { user_id } })
   ▼
AppSync ──── auth: Cognito user pool ──── (jwt.sub == arg user_id ? )
   │
   ▼ (JS resolver `getUserProfile.js`)
DynamoDB.GetItem { user_id }
   │
   ▼ (response template returns Item)
React
```

## Write (Lambda)

```
React (EditProfilePage) ── updateUserProfile(input) ──▶ AppSync
                                                          │
                                                          ▼ (pipeline resolver)
                                                  Lambda update_profile (Rust)
                                                          │
                                                          ├── usecase: validate input
                                                          ├── repo.update(user_id, patch)
                                                          │       └─ DynamoDB UpdateItem
                                                          └── return entity
                                                          │
                                                          ▼
React (ProfilePage updated)
```
