# AGENTS.md

AI agent guidance for the Serverless System Template project.

## Project Structure

```
serverless-system-template/
├── backend/
│   ├── src/
│   │   ├── core_python/          # Shared entities, config, utilities
│   │   └── functions/            # Each subdirectory = one Lambda (vertical slice)
│   │       └── <function_name>/
│   │           ├── presentation/  # handler.py — Lambda entry, DI, routing
│   │           ├── domain/        # Use cases (pure logic) + repository ABC
│   │           └── data/          # Repository impl + cloud datasources
│   ├── tests/
│   ├── aws/                      # SAM template + build config
│   ├── Makefile
│   └── pyproject.toml
├── frontend/
│   ├── react_app/                # Vite + React + TypeScript SPA
│   └── nextjs_app/               # Next.js App Router + OpenNext
├── infrastructure/
│   ├── __main__.py               # Pulumi orchestrator
│   ├── services/                 # One module per AWS resource type
│   └── Pulumi.{dev,staging,prod}.yaml
├── scripts/                      # Operational shell scripts
├── docs/                         # Setup and usage guides
├── pyproject.toml                # Root uv workspace
└── .github/workflows/            # CI/CD pipelines
```

## Conventions

### Python (Backend + Infrastructure)

- Package manager: `uv`. Run commands with `uv run`.
- Python 3.11+.
- Use f-strings for logging: `logger.info(f"Processing {item_id}")`.
- Use `ruff` for linting and formatting.
- Tests: `pytest` + `pytest-asyncio` + `hypothesis` for property tests.

### Clean Architecture Rules

Each vertical slice under `backend/src/functions/` follows strict layering:

1. **Domain layer** (`domain/`): Pure business logic. Use cases + repository ABCs.
   - MUST NOT import `boto3`, `botocore`, `kink`, `aws_lambda_powertools`, or any cloud SDK.
   - Depends only on `core_python` and standard library.
2. **Data layer** (`data/`): Concrete repository implementations + cloud datasources.
   - Implements domain ABCs. May import `boto3` and cloud SDKs.
3. **Presentation layer** (`presentation/`): Lambda handler, DI wiring, request routing.
   - Parses events via `core_python.utils.lambda_request.parse_event`.
   - Formats responses via `core_python.utils.lambda_response.format_response`.
   - DI initialization at module level (runs once per cold start) using `kink`.

### Vertical Slice Isolation

- Each function imports only from `core_python` and its own submodules.
- No cross-slice imports between functions.
- Each function has its own `requirements.txt` for function-specific dependencies.

### Infrastructure (Pulumi)

- Service-per-file pattern under `infrastructure/services/`.
- Cognito and DynamoDB are config-based (pre-created outside Pulumi).
- All resources must have tags: `Application`, `Environment`, `ManagedBy`.

### Frontends

- React app: Vite + TypeScript. Auth via AWS Amplify. Tokens in memory only.
- Next.js app: App Router. Auth via AWS SDK. Tokens in httpOnly cookies.
- Both use `npm` as package manager.

## Adding a New Lambda Function

1. Create `backend/src/functions/<name>/` with `presentation/`, `domain/`, `data/` dirs.
2. Define repository ABC in `domain/repository.py`.
3. Implement use cases in `domain/` — pure logic, no cloud imports.
4. Implement repository + datasource in `data/`.
5. Wire DI and routing in `presentation/handler.py`.
6. Add `requirements.txt` for function-specific deps.
7. Add corresponding test files under `backend/tests/functions/<name>/`.
8. Register the Lambda in `infrastructure/services/lambda_functions.py`.
9. Add API routes in `infrastructure/services/api_gateway.py`.
