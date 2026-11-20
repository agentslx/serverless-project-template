# Data flow

## 1. Sign-up

```
Browser ──signUp(email,pw)──▶ Cognito (user pool)
        ◀──ConfirmationCodeSentToEmail──
Browser ──confirmSignUp(code)──▶ Cognito
                                   │
                                   ▼
                          PostConfirmation Lambda trigger (Rust)
                                   │
                                   ▼
                          DynamoDB: PUT user_profiles { user_id, email, created_at }
```

## 2. Login + read profile

```
Browser ──signIn──▶ Cognito  ◀── returns JWT (id + access)
Browser ──GraphQL Query getUserProfile(user_id)──▶ AppSync
                                                   │
                                                   ▼  (JS resolver, no Lambda)
                                          DynamoDB: GetItem
                                                   │
                                                   ▼
Browser ◀── UserProfile { user_id, email, display_name, avatar_url }
```

## 3. Update profile

```
Browser ──GraphQL Mutation updateUserProfile(input)──▶ AppSync
                                                       │
                                                       ▼ (pipeline resolver)
                                               Lambda updateProfile (Rust)
                                                       │
                                                       ├─ validate
                                                       ├─ DynamoDB: UpdateItem
                                                       └─ (optional) emit EventBridge
                                                       │
                                                       ▼
Browser ◀── UserProfile (updated)
```

## 4. Admin user listing

```
Admin Browser ──signIn (admin pool)──▶ Cognito Admin Pool
Admin Browser ──GraphQL listUsers──▶ AppSync (auth: admin pool)
                                       │
                                       ▼
                              Lambda adminListUsers (Rust)
                                       │
                                       ▼
                              DynamoDB Scan/Query user_profiles
```
