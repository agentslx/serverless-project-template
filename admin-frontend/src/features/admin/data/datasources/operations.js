export const QUERY_LIST_USERS = /* GraphQL */ `
  query ListUsers($limit: Int, $next: String) {
    listUsers(limit: $limit, next: $next) {
      items {
        user_id
        email
        display_name
        avatar_url
        created_at
        updated_at
      }
      next
    }
  }
`;
