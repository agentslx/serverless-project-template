/**
 * @typedef {Object} UserProfileRepository
 * @property {(userId:string) => Promise<import('@/shared/entities/userProfile').UserProfile|null>} getProfile
 * @property {(userId:string, patch:{display_name?:string, avatar_url?:string}) => Promise<import('@/shared/entities/userProfile').UserProfile>} updateProfile
 */

export const UserProfileRepository = {};
