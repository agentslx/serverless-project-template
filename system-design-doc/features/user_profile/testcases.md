# user_profile · test cases

## Backend

### `feature_user_profile` unit tests
| ID  | Test                                                   | Expected                           |
|-----|--------------------------------------------------------|------------------------------------|
| U1  | `GetUserProfileUseCase` returns entity                 | matches stub repo                  |
| U2  | `UpdateUserProfileUseCase` rejects empty display_name  | `Err(ValidationError)`             |
| U3  | `UpdateUserProfileUseCase` updates `updated_at`        | `updated_at` is more recent       |
| U4  | `DynamoUserProfileModel::from_item` roundtrip          | `to_item ∘ from_item == identity`  |

### Integration tests (DynamoDB-local)
| ID  | Test                                                   | Expected                           |
|-----|--------------------------------------------------------|------------------------------------|
| I1  | `handler_get_profile` GET happy path                   | 200 + correct JSON                 |
| I2  | `handler_get_profile` not found                        | 404                                |
| I3  | `handler_update_profile` rejects mismatched user_id     | 403                                |
| I4  | `handler_update_profile` happy path                    | 200 + DynamoDB updated             |

## Frontend

| ID  | Scenario                                                | Expected                          |
|-----|---------------------------------------------------------|-----------------------------------|
| F1  | ProfilePage shows skeleton then data                    | data-testid `profile-display-name` |
| F2  | EditProfilePage submits patch                           | `updateUserProfile` mutation called|
| F3  | EditProfilePage validation: display_name >= 2 chars     | inline error                      |

## AppSync resolver (unit)

| ID  | Test                                                     | Expected                          |
|-----|----------------------------------------------------------|-----------------------------------|
| R1  | `getUserProfile.request` builds GetItem with sub          | `key: { user_id: { S: <sub> } }`  |
| R2  | `getUserProfile.response` returns null on missing item    | `null`                            |
