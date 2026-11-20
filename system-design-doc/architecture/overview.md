# Architecture overview

## High-level diagram

```
                    ┌──────────────────────────────────────┐
                    │  CloudFront ×2 (user CDN + admin CDN)│
                    └──────┬─────────────────┬─────────────┘
                           │                 │
                ┌──────────▼──┐         ┌────▼─────────┐
                │ S3 (user FE)│         │ S3 (admin FE)│
                └─────────────┘         └──────────────┘
                           │                 │
   ┌──────────────────────────────────────────────────────────┐
   │              Browser ─ user app  /  admin app            │
   │  Amplify Auth ──▶ Cognito (user pool / admin pool)       │
   │  Amplify API  ──▶ AppSync GraphQL (Cognito auth)         │
   └───────────┬────────────────────────────────┬─────────────┘
               │                                │
        ┌──────▼────────┐                ┌──────▼─────────┐
        │ Cognito Pools │                │   AppSync API  │
        │ • user        │                │  (JS resolvers)│
        │ • admin       │                └──────┬─────────┘
        └───────────────┘                       │
                                          ┌─────▼──────┐
                                          │  DynamoDB  │
                                          └─────▲──────┘
                                                │
                            (cmd / write paths) │
                       ┌────────────────────────┘
                       │
                ┌──────▼───────┐     ┌──────────────┐
                │   Lambdas    │◀────│  API Gateway │
                │   (Rust)     │     │   (HTTP API) │
                └──────────────┘     └──────────────┘
```

## Why this shape

| Concern                        | Decision                                        |
|--------------------------------|-------------------------------------------------|
| Cold-start critical reads      | AppSync JS resolver hits DynamoDB directly      |
| Anything with logic / external | Lambda (Rust) for predictable perf              |
| Multi-tenant / role separation | Two Cognito pools (`user`, `admin`)             |
| Two environments               | Pulumi stacks `dev` / `prod`, separate AWS acc. |
| Region                         | `ap-southeast-2` (closest to AU users)          |

## Read vs. write paths

- **Read** `getUserProfile` — AppSync resolver → DynamoDB (no Lambda).
- **Write** `updateUserProfile` — AppSync **pipeline** resolver → Lambda (Rust) → DynamoDB.
  Lambda enforces invariants (e.g. validation, downstream events) that resolvers can't.

## Authentication

- **User App** (`frontend/`): Cognito user pool with self-sign-up + email verification.
- **Admin Panel** (`admin-frontend/`): a separate Cognito user pool with **admin-create-only** users; no public sign-up. Admin Panel is its own React bundle, S3 bucket, and CloudFront distribution — there is no shared runtime with the user app.
- Both apps use Amplify v6 (`@aws-amplify/auth`).
- AppSync uses Cognito as primary auth mode; admin operations are gated by group membership / pool.

## Environments

| Env  | AWS account / profile  | Pulumi stack | User domain                | Admin domain                  |
|------|------------------------|--------------|----------------------------|-------------------------------|
| dev  | `dev`               | `dev`        | `dev.example.com`          | `admin.dev.example.com`       |
| prod | `prod`              | `prod`       | `app.example.com`          | `admin.example.com`           |

Per-env config lives in:
- `backend/configs/{dev,prod}.toml`     — values consumed by Pulumi → Lambda env vars.
- `frontend/.env.{development,production}`        — user app, wired by deploy job.
- `admin-frontend/.env.{development,production}`  — admin app, wired by deploy job.
- `iac/Pulumi.{dev,prod}.yaml`          — region, table names, pool naming.
