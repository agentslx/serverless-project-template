import { appsyncDatasource } from "@/features/user_profile/data/datasources/appsyncDatasource";

export const appsyncProfileRepository = {
  async getProfile(userId) {
    return appsyncDatasource.getUserProfile(userId);
  },
  async updateProfile(_userId, patch) {
    return appsyncDatasource.updateUserProfile(patch);
  },
};
