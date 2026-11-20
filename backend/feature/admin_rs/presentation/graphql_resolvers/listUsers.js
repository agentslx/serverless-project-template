/**
 * AppSync JS resolver — listUsers (Lambda data source).
 *
 * This admin-only resolver delegates to the `handler_list_users` Rust Lambda,
 * which performs a paginated DynamoDB scan and returns a `ListUsersPage`.
 *
 * The AppSync API itself is gated by the **admin** Cognito user pool — every
 * call is JWT-validated before this resolver runs. We additionally enforce
 * the `admin` group at the schema level (`@aws_cognito_user_pools`).
 *
 * Runtime: APPSYNC_JS 1.0.0
 */
import { util } from '@aws-appsync/utils';

export function request(ctx) {
  const sub = ctx.identity?.sub;
  if (!sub) {
    util.unauthorized();
  }
  // `cognito:groups` is exposed at `ctx.identity.groups` for user-pool auth.
  const groups = ctx.identity?.groups ?? [];
  if (!groups.includes('admin')) {
    util.unauthorized();
  }

  return {
    operation: 'Invoke',
    payload: {
      action: 'listUsers',
      limit: ctx.args?.limit ?? null,
      next_token: ctx.args?.next_token ?? null,
      caller_groups: groups,
    },
  };
}

export function response(ctx) {
  if (ctx.error) {
    util.error(ctx.error.message, ctx.error.type);
  }
  // Lambda returns the `ListUsersPage` directly: { users, next_token }.
  return ctx.result;
}
