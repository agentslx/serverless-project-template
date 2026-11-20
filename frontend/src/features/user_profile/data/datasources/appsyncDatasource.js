/**
 * Datasource — talks to AppSync via Amplify GraphQL client.
 */
import { gqlClient } from "@/shared/modules/amplifyClient";
import {
  QUERY_GET_USER_PROFILE,
  MUTATION_UPDATE_USER_PROFILE,
} from "./operations";

export const appsyncDatasource = {
  async getUserProfile(userId) {
    const r = await gqlClient().graphql({
      query: QUERY_GET_USER_PROFILE,
      variables: { user_id: userId },
    });
    return r.data?.getUserProfile || null;
  },

  async updateUserProfile(input) {
    const r = await gqlClient().graphql({
      query: MUTATION_UPDATE_USER_PROFILE,
      variables: { input },
    });
    return r.data?.updateUserProfile;
  },
};
