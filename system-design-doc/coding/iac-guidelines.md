# IaC coding guidelines (Pulumi · Python)

## Files

```
iac/
├── __main__.py                   ← THIN orchestrator
├── Pulumi.yaml                   ← project descriptor
├── Pulumi.dev.yaml               ← stack config (region, names…)
├── Pulumi.prod.yaml
├── requirements.txt
├── infrastructure/               ← long-lived
│   ├── __init__.py
│   ├── dynamodb.py
│   ├── cognito.py
│   ├── appsync.py
│   ├── websocket_api.py
│   ├── frontend_hosting.py
│   └── networking.py             (optional)
└── application/                  ← deployable artefacts
    ├── __init__.py
    ├── lambdas.py                (core feature Lambdas — one per feature per protocol)
    ├── chat_lambdas.py           (chat feature Lambdas — ws_lifecycle, ws_send_message, appsync)
    └── frontend.py
```

## Rules

- `__main__.py` must stay under ~30 lines. It only imports modules and wires outputs.
- Each module exposes a class (`DynamoDb`, `Cognito`, `AppSync`, `FrontendHosting`, `Lambdas`, `Frontend`) instantiated from `__main__.py`.
- Constructors take a `name` prefix and a `config: pulumi.Config`. They do not read os.environ.
- All names go through `f"{project}-{stack}-{resource}"`.
- Outputs are exported from `__main__.py` only.

## Stack config

`Pulumi.dev.yaml`:
```yaml
config:
  aws:region: ap-southeast-2
  emergent-serverless-template:projectPrefix: est
  emergent-serverless-template:logRetentionDays: 14
```

Read with `cfg.require("projectPrefix")`.

## Secrets

Use `pulumi.Config().require_secret("xyz")` for anything sensitive — they end up encrypted in the state file.
