import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { MdButton } from "@/shared/ui/MdButton";
import { MdTextField } from "@/shared/ui/MdTextField";
import { AuthCard } from "@/features/auth/presentation/components/AuthCard";
import { signUpUseCase } from "@/features/auth/domain/usecases/signUp";
import { cognitoAuthRepository } from "@/features/auth/data/repository/cognitoAuthRepository";

export default function SignUpPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await signUpUseCase(cognitoAuthRepository)(email, password);
      toast.success("Code sent — check your inbox.");
      navigate(`/verify?email=${encodeURIComponent(email)}`);
    } catch (err) {
      toast.error(err.message || "Sign-up failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard
      testid="signup-page"
      title="Create your account"
      subtitle="We'll send a verification code to your email."
      footer={
        <Link to="/login" data-testid="link-login" className="text-primary hover:underline">
          Already have an account? Sign in
        </Link>
      }
    >
      <form onSubmit={onSubmit} className="flex flex-col gap-5">
        <MdTextField
          label="Email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          testid="signup-email-input"
        />
        <MdTextField
          label="Password (min 8 chars)"
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          testid="signup-password-input"
          helperText="At least 8 characters with one number and one uppercase letter."
        />
        <MdButton type="submit" disabled={loading} data-testid="signup-submit-btn">
          {loading ? "Creating…" : "Create account"}
        </MdButton>
      </form>
    </AuthCard>
  );
}
