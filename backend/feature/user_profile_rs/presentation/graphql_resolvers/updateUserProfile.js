/**
 * AppSync JS resolver — updateUserProfile.
 *
 * This is the *first* function of an AppSync **pipeline** resolver. It
 * delegates to the `handler_update_profile` Lambda, then formats the
 * response. Doing it as a pipeline keeps validation/audit/event-emission
 * close to the Lambda while still letting AppSync own auth & throttling.
 *
 * Runtime: APPSYNC_JS 1.0.0
 */
import { util } from '@aws-appsync/utils';

export function request(ctx) {
  const sub = ctx.identity?.sub;
  if (!sub) {
    util.unauthorized();
  }
  return {
    operation: 'Invoke',
    payload: {
      action: 'updateUserProfile',
      user_id: sub,
      input: ctx.args.input,
    },
  };
}

export function response(ctx) {
  if (ctx.error) {
    util.error(ctx.error.message, ctx.error.type);
  }
  // Lambda returns the entity directly.
  return ctx.result;
}
