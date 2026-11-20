# Clean architecture cheat-sheet

Apply these rules to **every feature**, both backend and frontend. They're enforced by code review and by the lint configs.

## Layers

```
        ┌──────────────────────────────────────┐
        │           presentation               │   ← Lambda handler / React page
        │       (depends on domain only)       │
        └────────────────────┬─────────────────┘
                             │
        ┌────────────────────▼─────────────────┐
        │               domain                 │   ← pure business logic
        │ usecases  ──uses──▶  repository (trait)│
        └────────────────────▲─────────────────┘
                             │ (impls)
        ┌────────────────────┴─────────────────┐
        │                 data                 │   ← infrastructure
        │  repository_impl ──▶ datasources ──▶ │     SDKs / HTTP / cache
        │              models (DTOs)           │
        └──────────────────────────────────────┘

shared/entities  ←  used by all layers (plain types only)
```

## Mental model

1. **Entity** — a plain shape, e.g. `UserProfile { user_id, email, display_name }`. Lives in `shared/entities/`. No DynamoDB, no JSON-API knowledge.
2. **Model** — an infrastructure-shaped DTO, e.g. `DynamoUserProfileModel` with `from_item(...)` and `to_item()`. Lives in `data/models/`.
3. **Datasource** — talks to one external system (`DynamoUserProfileDataSource`, `CacheDataSource`). Lives in `data/datasources/`.
4. **Repository (trait)** — what the domain wants. Lives in `domain/repository/`.
5. **Repository (impl)** — assembles datasources, converts models ↔ entities. Lives in `data/repository/`.
6. **Usecase** — orchestrates calls to one or more repositories. Pure logic. Lives in `domain/usecases/`.
7. **Presentation** — handler / page that injects concrete impls into usecases.

## Example data flow (read)

```
LambdaHandler::get_profile
        │
        ├── builds DynamoUserProfileRepository (impl)
        │   └── injects DynamoUserProfileDataSource + CachedUserProfileDataSource
        │
        └── calls GetUserProfileUseCase::execute(user_id)
                    │
                    └── repository.find_by_id(user_id) -> UserProfile (entity)
                                │
                                ├── tries cache_ds.get(user_id)
                                └── on miss: db_ds.get_item(user_id)
                                            └── Model::from_item -> entity
```

## Allowed imports — quick table

| File path                                | May import                                                    |
|------------------------------------------|---------------------------------------------------------------|
| `shared/entities/`                       | std + serde                                                   |
| `domain/usecases/`                       | `shared/entities`, sibling `domain/repository`                |
| `domain/repository/`                     | `shared/entities`                                             |
| `data/models/`                           | `shared/entities`, serde, aws-sdk types                       |
| `data/datasources/`                      | `data/models`, infra SDKs                                     |
| `data/repository/`                       | `domain/repository`, `data/datasources`, `data/models`, `shared/entities` |
| `presentation/lambda_handlers/<x>/`      | `domain/usecases`, `data/repository` (only to wire impls)     |

If a file needs an import not in this table, the layering is wrong.
