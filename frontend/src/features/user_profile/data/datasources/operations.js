/** AppSync GraphQL operation strings — kept inside the data layer. */
export const QUERY_GET_USER_PROFILE = /* GraphQL */ `
  query GetUserProfile($user_id: ID!) {
    getUserProfile(user_id: $user_id) {
      user_id
      email
      display_name
      avatar_url
      created_at
      updated_at
    }
  }
`;

export const MUTATION_UPDATE_USER_PROFILE = /* GraphQL */ `
  mutation UpdateUserProfile($input: UpdateUserProfileInput!) {
    updateUserProfile(input: $input) {
      user_id
      email
      display_name
      avatar_url
      created_at
      updated_at
    }
  }
`;
