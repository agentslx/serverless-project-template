# IaC

Pulumi (Python) project. Two stacks: `dev` and `prod`.

## Layout

| Path                           | Role                                |
|--------------------------------|-------------------------------------|
| `__main__.py`                  | thin orchestrator                   |
| `infrastructure/dynamodb.py`   | `user_profiles` table               |
| `infrastructure/cognito.py`    | user pool + admin pool              |
| `infrastructure/appsync.py`    | GraphQL API + JS resolvers          |
| `infrastructure/frontend_hosting.py` | S3 + CloudFront with OAC      |
| `application/lambdas.py`       | Rust Lambda functions per binary    |
| `application/frontend.py`      | bundle upload + CDN invalidation    |

## Run

```bash
cd iac
python -m venv venv && . venv/bin/activate
pip install -r requirements.txt

pulumi stack select dev
pulumi up
```

Outputs (`pulumi stack output --json`) are consumed by the `deploy-dev.yml`
workflow to populate `frontend/.env.development` before the FE build.
