/**
 * Plain entity. No Amplify or HTTP imports — same rule as backend `shared/entities`.
 *
 * @typedef {Object} UserProfile
 * @property {string} user_id
 * @property {string} email
 * @property {string} display_name
 * @property {string|null} avatar_url
 * @property {string} created_at
 * @property {string} updated_at
 */

export const UserProfile = {
  isValid(p) {
    return p && typeof p.user_id === "string" && typeof p.email === "string";
  },
};
