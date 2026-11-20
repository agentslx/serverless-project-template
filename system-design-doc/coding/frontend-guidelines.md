# Frontend (Frontends)

src/
├── App.js
├── shared/{entities,modules,ui}
└── features/<feature>/{domain,data,presentation}
```

Both `frontend/` (user app) and `admin-frontend/` (admin app) follow the
same layout. They are independent React projects — see §5.

## Folder shape (per app)

```
frontend/src/
├── shared/
│   ├── entities/        plain types (UserProfile, AuthSession, …)
│   ├── modules/         non-UI shared code (amplify init, http client, …)
│   └── ui/              shared visual components (Button, Layout, …)
└── features/<feature>/
    ├── domain/
    │   ├── usecases/
    │   └── repository/   (just JSDoc-typed interface objects)
    ├── data/
    │   ├── datasources/
    │   ├── repository/
    │   └── models/
    └── presentation/
        ├── pages/
        ├── components/
        └── state/        (React contexts / hooks)
```

## Imports / conventions

- `@/...` alias points at `src/`.
- Pages = default exports. Other components = named exports.
- One feature must **never** import from another feature. If you need to, lift to `shared/`.
- Domain files have **no** imports from `aws-amplify`, `axios`, etc.

## Auth

- Amplify v6 modular API (`signIn`, `signUp`, `confirmSignUp`, `resetPassword`).
- Two configurations are bootstrapped: `userPool` (default) and `adminPool`. We swap with `Amplify.configure(...)` when entering `/admin/*`.
- Auth state is exposed by `features/auth/presentation/state/AuthContext.jsx`.

## GraphQL (AppSync)

- A single Amplify GraphQL client is built in `shared/modules/amplifyClient.js`.
- Each feature owns its `.graphql` operation strings under `data/datasources/<f>_appsync_datasource.js`.

## Tailwind / Material design tokens

CSS variables in `index.css` follow the Material 3 token set (`--md-sys-color-primary`, etc.). We expose Tailwind colour names like `primary`, `surface`, `on-surface`. Avoid:

- ❌ Inter, Roboto-default, Helvetica
- ❌ Purple-on-white gradient
- ❌ Centered "AI app" hero

Use:

- ✅ `Roboto Flex` (variable) for body, `Material Symbols Rounded` for icons.
- ✅ Subtle elevation shadows (`shadow-md3-1` … `shadow-md3-5`).
- ✅ Rounded-2xl / pill buttons.

## data-testid

Every interactive element + critical info element gets a kebab-case `data-testid` describing function:

```jsx
<button data-testid="login-submit-btn">Sign in</button>
<input data-testid="login-email-input" />
<div  data-testid="profile-display-name">{name}</div>
```
