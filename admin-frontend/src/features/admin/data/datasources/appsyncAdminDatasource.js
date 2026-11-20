/**
 * AppSync datasource — admin scope.
 * NOTE: the AppSync schema currently exposes `listUsers` only when called by
 * the admin Cognito group. Wire it via the IaC `application/lambdas.py`
 * (admin_list_users handler — left as a P1 task in PRD).
 */
import { gqlClient } from "@/shared/modules/amplifyClient";
import { QUERY_LIST_USERS } from "./operations";

export const appsyncAdminDatasource = {
  async listUsers() {
    const r = await gqlClient().graphql({
      query: QUERY_LIST_USERS,
      variables: { limit: 100 },
    });
    return r.data?.listUsers?.items || [];
  },
};
