/**
 * AppSync JS resolver — getUserProfile (DynamoDB direct).
 *
 * Auth: identity comes from the Cognito user pool authoriser. We *force*
 * the requested user_id to match the JWT sub so a user can never read
 * someone else's profile via this resolver.
 *
 * Runtime: APPSYNC_JS 1.0.0
 */
import { util } from '@aws-appsync/utils';

export function request(ctx) {
  const sub = ctx.identity?.sub;
  if (!sub) {
    util.unauthorized();
  }

  const requested = ctx.args?.user_id;
  if (requested && requested !== sub) {
    util.unauthorized();
  }

  return {
    operation: 'GetItem',
    key: util.dynamodb.toMapValues({ user_id: sub }),
    consistentRead: false,
  };
}

export function response(ctx) {
  if (ctx.error) {
    util.error(ctx.error.message, ctx.error.type);
  }
  return ctx.result; // null is fine — frontend handles "not found"
}
