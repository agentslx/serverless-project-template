# scripts/

Convenience wrappers. All scripts are idempotent and emit `set -euo pipefail`.

| Script                     | Purpose                                                          |
|----------------------------|------------------------------------------------------------------|
| `dev_up.sh`                | Bring up moto + local_proxy_py + local_proxy + create the table |
| `dev_down.sh`              | Tear down everything `dev_up.sh` started                         |
| `test_all.sh`              | `cargo test` + `pytest` + `check_routes.sh`                      |
| `check_routes.sh`          | Validate `routes.json` — every handler must be registered        |
| `package_py_lambdas.sh`    | Bundle each Python Lambda into `backend/target/python_lambda/`   |

The dev stack exposes:

| Method | Path                          | Language | Auth (local)                                  |
|--------|-------------------------------|----------|-----------------------------------------------|
| GET    | `/api/health`                 | python   | none                                          |
| GET    | `/api/me`                     | rust     | `x-user-sub`, `x-user-email`                  |
| GET    | `/api/profile/:user_id`       | rust     | `x-user-sub` (must match `:user_id`)          |
| PATCH  | `/api/profile/:user_id`       | rust     | `x-user-sub` (must match `:user_id`)          |
| GET    | `/api/admin/users?limit=&next_token=` | rust | `x-user-sub` + `x-admin: true` *or* `x-cognito-groups: admin` |

Typical loop:

```bash
./emergent_env_setup.sh        # one time
scripts/dev_up.sh              # bring stack up
curl http://localhost:9000/api/health
scripts/test_all.sh            # run every test
scripts/dev_down.sh            # cleanup
```
