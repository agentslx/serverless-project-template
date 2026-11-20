import { appsyncAdminDatasource } from "@/features/admin/data/datasources/appsyncAdminDatasource";

export const appsyncAdminRepository = {
  async listUsers() {
    return appsyncAdminDatasource.listUsers();
  },
};
