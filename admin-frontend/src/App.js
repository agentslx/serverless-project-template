import React from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Toaster } from "sonner";

import { bootstrap } from "@/shared/modules/amplifyClient";
import { AuthProvider, useAuth } from "@/features/auth/presentation/state/AuthContext";
import { ProtectedRoute } from "@/shared/ui/ProtectedRoute";
import { AdminShell } from "@/shared/ui/AdminShell";

import LoginPage from "@/features/auth/presentation/pages/LoginPage";
import ForgotPasswordPage from "@/features/auth/presentation/pages/ForgotPasswordPage";

import AdminDashboardPage from "@/features/admin/presentation/pages/AdminDashboardPage";
import UsersListPage from "@/features/admin/presentation/pages/UsersListPage";

bootstrap();

function ShelledRoutes() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const bare = ["/login", "/forgot"].some((p) => location.pathname.startsWith(p));

  const inner = (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot" element={<ForgotPasswordPage />} />

      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AdminDashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <ProtectedRoute>
            <UsersListPage />
          </ProtectedRoute>
        }
      />

      <Route path="/" element={<Navigate to="/admin" replace />} />
      <Route path="*" element={<Navigate to="/admin" replace />} />
    </Routes>
  );

  return bare ? inner : <AdminShell currentUser={user} onLogout={logout}>{inner}</AdminShell>;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ShelledRoutes />
        <Toaster position="bottom-right" richColors />
      </AuthProvider>
    </BrowserRouter>
  );
}
