import React from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Toaster } from "sonner";

import { bootstrap } from "@/shared/modules/amplifyClient";
import { AuthProvider, useAuth } from "@/features/auth/presentation/state/AuthContext";
import { ProtectedRoute } from "@/shared/ui/ProtectedRoute";
import { AppShell } from "@/shared/ui/AppShell";

import LoginPage from "@/features/auth/presentation/pages/LoginPage";
import SignUpPage from "@/features/auth/presentation/pages/SignUpPage";
import VerifyPage from "@/features/auth/presentation/pages/VerifyPage";
import ForgotPasswordPage from "@/features/auth/presentation/pages/ForgotPasswordPage";

import ProfilePage from "@/features/user_profile/presentation/pages/ProfilePage";
import EditProfilePage from "@/features/user_profile/presentation/pages/EditProfilePage";
import ChatPage from "@/features/chat/presentation/pages/ChatPage";

import LandingPage from "@/LandingPage";

bootstrap();

function ShelledRoutes() {
  const { user } = useAuth();
  const location = useLocation();
  const bare = ["/login", "/signup", "/verify", "/forgot"].some((p) =>
    location.pathname.startsWith(p)
  );

  const inner = (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignUpPage />} />
      <Route path="/verify" element={<VerifyPage />} />
      <Route path="/forgot" element={<ForgotPasswordPage />} />

      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile/edit"
        element={
          <ProtectedRoute>
            <EditProfilePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );

  return bare ? inner : <AppShell currentUser={user}>{inner}</AppShell>;
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
