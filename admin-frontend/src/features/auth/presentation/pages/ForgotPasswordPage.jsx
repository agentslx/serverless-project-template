import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { MdButton } from "@/shared/ui/MdButton";
import { MdTextField } from "@/shared/ui/MdTextField";
import { AuthCard } from "@/features/auth/presentation/components/AuthCard";
import {
  forgotPasswordUseCase,
  confirmForgotPasswordUseCase,
} from "@/features/auth/domain/usecases/forgotPassword";
import { cognitoAuthRepository } from "@/features/auth/data/repository/cognitoAuthRepository";

export default function ForgotPasswordPage() {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onRequest = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await forgotPasswordUseCase(cognitoAuthRepository)(email);
      toast.success("Reset code sent.");
      setStep(2);
    } catch (err) {
      toast.error(err.message || "Could not start reset");
    } finally {
      setLoading(false);
    }
  };

  const onConfirm = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await confirmForgotPasswordUseCase(cognitoAuthRepository)(email, code, newPassword);
      toast.success("Password updated.");
      navigate("/login");
    } catch (err) {
      toast.error(err.message || "Reset failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthCard
      testid="admin-forgot-page"
      title="Reset admin password"
      subtitle={
        step === 1
          ? "We'll email you a one-time code."
          : "Enter the code and choose a new password (min 12 chars)."
      }
      footer={
        <Link to="/login" data-testid="link-login" className="text-primary hover:underline">
          Back to sign in
        </Link>
      }
    >
      {step === 1 ? (
        <form onSubmit={onRequest} className="flex flex-col gap-5">
          <MdTextField
            label="Admin email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            testid="admin-forgot-email-input"
          />
          <MdButton type="submit" disabled={loading} data-testid="admin-forgot-request-btn">
            {loading ? "Sending…" : "Send reset code"}
          </MdButton>
        </form>
      ) : (
        <form onSubmit={onConfirm} className="flex flex-col gap-5">
          <MdTextField
            label="Code"
            inputMode="numeric"
            required
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/[^0-9]/g, ""))}
            testid="admin-forgot-code-input"
          />
          <MdTextField
            label="New password"
            type="password"
            required
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            testid="admin-forgot-newpw-input"
          />
          <MdButton type="submit" disabled={loading} data-testid="admin-forgot-confirm-btn">
            {loading ? "Updating…" : "Update password"}
          </MdButton>
        </form>
      )}
    </AuthCard>
  );
}
