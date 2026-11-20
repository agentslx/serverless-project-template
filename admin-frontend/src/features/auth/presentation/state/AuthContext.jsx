import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { cognitoAuthRepository } from "@/features/auth/data/repository/cognitoAuthRepository";
import { currentSessionUseCase, logoutUseCase } from "@/features/auth/domain/usecases/session";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const refreshSession = useCallback(async () => {
    try {
      const u = await currentSessionUseCase(cognitoAuthRepository)();
      setUser(u);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshSession();
  }, [refreshSession]);

  const value = useMemo(
    () => ({
      user,
      loading,
      setUser,
      refreshSession,
      logout: async () => {
        await logoutUseCase(cognitoAuthRepository)();
        setUser(null);
        navigate("/login");
      },
    }),
    [user, loading, refreshSession, navigate]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
