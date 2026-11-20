import React, { useEffect, useState } from "react";
import { listUsersUseCase } from "@/features/admin/domain/usecases/listUsers";
import { appsyncAdminRepository } from "@/features/admin/data/repository/appsyncAdminRepository";

export default function UsersListPage() {
  const [users, setUsers] = useState([]);
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const list = await listUsersUseCase(appsyncAdminRepository)();
        setUsers(list);
      } catch (e) {
        setErr(e.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div data-testid="admin-users-page" className="flex flex-col gap-6">
      <header>
        <h1 className="text-3xl font-medium tracking-tight text-on-surface">Users</h1>
        <p className="text-sm text-on-surface-variant mt-1">
          Backed by AppSync · authenticated against the admin Cognito pool.
        </p>
      </header>

      {err && (
        <div
          data-testid="users-error"
          className="bg-tertiary-container text-on-tertiary-container rounded-2xl px-4 py-3 text-sm"
        >
          AppSync unreachable ({err}). Showing empty list — wire the
          <code className="mx-1 font-mono">listUsers</code> resolver to populate.
        </div>
      )}

      <section className="bg-surface rounded-3xl shadow-md3-1 border border-outline-variant overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-surface-variant text-on-surface-variant">
            <tr className="text-left">
              <th className="py-3 px-5 font-medium">Display name</th>
              <th className="py-3 px-5 font-medium">Email</th>
              <th className="py-3 px-5 font-medium">User ID</th>
              <th className="py-3 px-5 font-medium">Created</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={4} className="py-8 px-5 text-on-surface-variant">
                  Loading…
                </td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td
                  colSpan={4}
                  data-testid="users-empty"
                  className="py-8 px-5 text-on-surface-variant"
                >
                  No users found.
                </td>
              </tr>
            ) : (
              users.map((u) => (
                <tr
                  key={u.user_id}
                  data-testid={`user-row-${u.user_id}`}
                  className="border-t border-outline-variant"
                >
                  <td className="py-3 px-5 text-on-surface">{u.display_name}</td>
                  <td className="py-3 px-5 text-on-surface">{u.email}</td>
                  <td className="py-3 px-5 font-mono text-xs text-on-surface-variant">
                    {u.user_id}
                  </td>
                  <td className="py-3 px-5 text-on-surface-variant">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
