# auth · test cases

## Frontend (jest + RTL)

| ID     | Scenario                                                  | Expected                                  |
|--------|-----------------------------------------------------------|-------------------------------------------|
| FE-A1  | LoginPage renders all fields                              | email + password + submit + signup link   |
| FE-A2  | SignUp triggers `signUp()` once                           | repository called with `{email, password}`|
| FE-A3  | Verify with wrong code → error toast                      | toast "Invalid code"                      |
| FE-A4  | Forgot password emits two-step flow                       | request + confirm called in order         |
| FE-A5  | Admin login uses admin Amplify config                     | mocked configure() called with adminPool  |

## Backend (cargo test)

| ID     | Crate                          | Scenario                                  | Expected                          |
|--------|--------------------------------|-------------------------------------------|-----------------------------------|
| BE-A1  | feature_auth (unit)            | `GetMeUseCase` returns entity from repo   | entity matches stub               |
| BE-A2  | handler_get_me (integration)   | GET /me with valid JWT claims             | 200, JSON with `user_id, email`   |
| BE-A3  | handler_get_me (integration)   | GET /me without claims                    | 401                               |
| BE-A4  | handler_post_confirmation      | Cognito event → DynamoDB Put              | item exists in DynamoDB local     |
