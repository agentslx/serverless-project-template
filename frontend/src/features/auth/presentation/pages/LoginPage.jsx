import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { MdButton } from "@/shared/ui/MdButton";
import { MdTextField } from "@/shared/ui/MdTextField";
import { AuthCard } from "@/features/auth/presentation/components/AuthCard";
import { loginUseCase } from "@/features/auth/domain/usecases/login";
import { cognitoAuthRepository } from "@/features/auth/data/repository/cognitoAuthRepository";
import { useAuth } from "@/features/auth/presentation/state/AuthContext";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const { setUser } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const u = await loginUseCase(cognitoAuthRepository)(email, password);
      setUser(u);
      navigate("/profile");
    } catch (err) {
      toast.error(err.message || "Sign-in failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard
      testid="login-page"
      title="Welcome back"
      subtitle="Sign in to continue."
      footer={
        <div className="flex justify-between">
          <Link to="/forgot" data-testid="link-forgot" className="text-primary hover:underline">
            Forgot password?
          </Link>
          <Link to="/signup" data-testid="link-signup" className="text-primary hover:underline">
            Create account
          </Link>
        </div>
      }
    >
      <form onSubmit={onSubmit} className="flex flex-col gap-5">
        <MdTextField
          label="Email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          testid="login-email-input"
        />
        <MdTextField
          label="Password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          testid="login-password-input"
        />
        <MdButton type="submit" disabled={loading} data-testid="login-submit-btn">
          {loading ? "Signing in…" : "Sign in"}
        </MdButton>
      </form>
    </AuthCard>
  );
}
