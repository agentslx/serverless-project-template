import React, { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { MdButton } from "@/shared/ui/MdButton";
import { MdTextField } from "@/shared/ui/MdTextField";
import { AuthCard } from "@/features/auth/presentation/components/AuthCard";
import {
  confirmSignUpUseCase,
  resendCodeUseCase,
} from "@/features/auth/domain/usecases/signUp";
import { cognitoAuthRepository } from "@/features/auth/data/repository/cognitoAuthRepository";

export default function VerifyPage() {
  const [params] = useSearchParams();
  const [email, setEmail] = useState(params.get("email") || "");
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await confirmSignUpUseCase(cognitoAuthRepository)(email, code);
      toast.success("Email verified — please sign in.");
      navigate("/login");
    } catch (err) {
      toast.error(err.message || "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const onResend = async () => {
    try {
      await resendCodeUseCase(cognitoAuthRepository)(email);
      toast.success("New code sent.");
    } catch (err) {
      toast.error(err.message || "Could not resend");
    }
  };

  return (
    <AuthCard
      testid="verify-page"
      title="Verify your email"
      subtitle="Enter the 6-digit code we sent you."
      footer={
        <div className="flex justify-between">
          <button
            type="button"
            data-testid="resend-code-btn"
            className="text-primary hover:underline"
            onClick={onResend}
          >
            Resend code
          </button>
          <Link to="/login" data-testid="link-login" className="text-primary hover:underline">
            Back to sign in
          </Link>
        </div>
      }
    >
      <form onSubmit={onSubmit} className="flex flex-col gap-5">
        <MdTextField
          label="Email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          testid="verify-email-input"
        />
        <MdTextField
          label="Verification code"
          inputMode="numeric"
          required
          value={code}
          onChange={(e) => setCode(e.target.value.replace(/[^0-9]/g, ""))}
          testid="verify-code-input"
        />
        <MdButton type="submit" disabled={loading} data-testid="verify-submit-btn">
          {loading ? "Verifying…" : "Verify"}
        </MdButton>
      </form>
    </AuthCard>
  );
}
