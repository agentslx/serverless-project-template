import React from "react";
import { Link } from "react-router-dom";
import { MdButton } from "@/shared/ui/MdButton";
import { adminAppUrl } from "@/aws-config";

const features = [
  {
    icon: "bolt",
    title: "Rust Lambdas",
    body: "Cold-starts under 50 ms. Each handler is its own crate, deployed via cargo-lambda.",
  },
  {
    icon: "schema",
    title: "Clean architecture",
    body: "Per-feature domain / data / presentation. No cross-feature imports — ever.",
  },
  {
    icon: "graphic_eq",
    title: "AppSync JS resolvers",
    body: "Direct DynamoDB reads, Lambda-backed writes. Cognito-secured.",
  },
  {
    icon: "construction",
    title: "Pulumi IaC",
    body: "Infrastructure / application split. Two stacks: dev & prod, ap-southeast-2.",
  },
  {
    icon: "verified_user",
    title: "Two Cognito pools",
    body: "Self-serve user pool + admin-created admin pool. Amplify v6 wires both.",
  },
  {
    icon: "deployed_code",
    title: "GitHub Actions CI/CD",
    body: "Per-area pipelines for backend / frontend / IaC + tagged prod release.",
  },
];

export default function LandingPage() {
  return (
    <div data-testid="landing-page" className="flex flex-col gap-16">
      <section className="pt-6 sm:pt-12">
        <span
          data-testid="region-pill"
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-primary-container text-on-primary-container"
        >
          <span className="material-symbols-rounded text-[16px]">public</span>
          ap-southeast-2 · dev flavour
        </span>
        <h1 className="mt-6 text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight text-on-surface leading-[1.05] max-w-3xl">
          A serverless template that gets out of your way.
        </h1>
        <p className="mt-5 text-on-surface-variant max-w-2xl text-base sm:text-lg">
          Rust Lambdas, DynamoDB, Cognito, AppSync, Pulumi, GitHub Actions — wired
          with clean architecture per feature on both backend and frontend.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link to="/signup">
            <MdButton size="lg" data-testid="cta-create-account">
              Create account
            </MdButton>
          </Link>
          <Link to="/login">
            <MdButton size="lg" variant="outlined" data-testid="cta-sign-in">
              Sign in
            </MdButton>
          </Link>
          <Link to="/admin/login">
            <MdButton size="lg" variant="text" data-testid="cta-admin">
              I'm an admin →
            </MdButton>
          </Link>
        </div>
      </section>

      <section
        data-testid="features-grid"
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        {features.map((f) => (
          <article
            key={f.title}
            className="bg-surface rounded-3xl shadow-md3-1 p-6 border border-outline-variant transition-shadow hover:shadow-md3-2"
          >
            <span className="material-symbols-rounded text-primary text-[28px]">
              {f.icon}
            </span>
            <h3 className="mt-4 text-lg font-medium text-on-surface">{f.title}</h3>
            <p className="mt-2 text-sm text-on-surface-variant leading-relaxed">
              {f.body}
            </p>
          </article>
        ))}
      </section>

      <section
        data-testid="quickstart"
        className="bg-surface rounded-3xl shadow-md3-1 p-8 border border-outline-variant"
      >
        <h2 className="text-xl font-medium text-on-surface">Local quick-start</h2>
        <pre className="mt-4 overflow-x-auto text-xs leading-relaxed bg-surface-variant text-on-surface rounded-2xl p-5 border border-outline-variant">
{`# 1. DynamoDB local
docker run -p 8000:8000 amazon/dynamodb-local

# 2. Backend (simulated API Gateway, in-process)
cd backend && cargo run -p local_proxy

# 3. Frontend
cd frontend && yarn start`}
        </pre>
      </section>
    </div>
  );
}
