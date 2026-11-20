#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# App Template — Interactive Project Initializer
# Clones the template (if needed), renames & configures everything for your project.
# ─────────────────────────────────────────────────────────────────────────────

TEMPLATE_REPO="git@github.com:Consult/serverless-project-template.git"

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}▸${NC} $*"; }
ok()    { echo -e "${GREEN}✔${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠${NC} $*"; }
err()   { echo -e "${RED}✘${NC} $*" >&2; }

ask() {
  local prompt="$1" default="${2:-}" var="$3"
  if [[ -n "$default" ]]; then
    read -rp "$(echo -e "${BOLD}${prompt}${NC} [${default}]: ")" input
    eval "$var=\"${input:-$default}\""
  else
    while true; do
      read -rp "$(echo -e "${BOLD}${prompt}${NC}: ")" input
      if [[ -n "$input" ]]; then
        eval "$var=\"$input\""
        break
      fi
      err "This field is required."
    done
  fi
}

ask_yn() {
  local prompt="$1" default="${2:-y}" var="$3"
  while true; do
    read -rp "$(echo -e "${BOLD}${prompt}${NC} [${default}]: ")" input
    input="${input:-$default}"
    case "$input" in
      [Yy]*) eval "$var=y"; break;;
      [Nn]*) eval "$var=n"; break;;
      *) err "Please answer y or n.";;
    esac
  done
}

# ── Banner ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║       App Template — Project Initializer                 ║${NC}"
echo -e "${BOLD}║  Serverless Rust + DynamoDB + Cognito + AppSync + React     ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ── 1. Project basics ────────────────────────────────────────────────────────
echo -e "${CYAN}─── Project Details ───────────────────────────────────────────${NC}"
ask "Project title (human-readable)" "" PROJECT_TITLE
ask "Project slug (lowercase, no spaces, used for naming)" "$(echo "$PROJECT_TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')" PROJECT_SLUG
ask "Short description" "" PROJECT_DESCRIPTION
ask "Project prefix (short, for AWS resource naming, e.g. 'myapp')" "$(echo "$PROJECT_SLUG" | cut -c1-8)" PROJECT_PREFIX

echo ""
echo -e "${CYAN}─── Domain ────────────────────────────────────────────────────${NC}"
ask "Base domain (e.g. example.com, leave empty if not yet)" "" BASE_DOMAIN

echo ""
echo -e "${CYAN}─── Backend Language ──────────────────────────────────────────${NC}"
echo "  1) Rust only (recommended for production)"
echo "  2) Python only (faster iteration)"
echo "  3) Both (keep template as-is)"
ask "Backend language choice" "1" BE_LANG_CHOICE

echo ""
echo -e "${CYAN}─── Initial Features ──────────────────────────────────────────${NC}"
echo "The template ships with: auth, user_profile, admin"
ask_yn "Keep auth feature (Cognito sign-up/login)?" "y" FEAT_AUTH
ask_yn "Keep user_profile feature?" "y" FEAT_USER_PROFILE
ask_yn "Keep admin feature (admin dashboard)?" "y" FEAT_ADMIN

echo ""
echo -e "${CYAN}─── AWS Configuration ─────────────────────────────────────────${NC}"
ask "AWS Account ID" "" AWS_ACCOUNT_ID
ask "AWS Region" "ap-southeast-2" AWS_REGION
ask_yn "Configure AWS credentials now (access/secret key)?" "n" CONFIGURE_AWS_CREDS

AWS_ACCESS_KEY=""
AWS_SECRET_KEY=""
if [[ "$CONFIGURE_AWS_CREDS" == "y" ]]; then
  ask "AWS Access Key ID" "" AWS_ACCESS_KEY
  ask "AWS Secret Access Key" "" AWS_SECRET_KEY
fi

echo ""
echo -e "${CYAN}─── Pulumi State Backend ──────────────────────────────────────${NC}"
echo "Pulumi needs an S3 bucket for state storage (one per stack recommended)."
ask "S3 bucket for Pulumi state (dev)" "${PROJECT_SLUG}-pulumi-state-dev" PULUMI_BUCKET_DEV
ask "S3 bucket for Pulumi state (prod)" "${PROJECT_SLUG}-pulumi-state-prod" PULUMI_BUCKET_PROD
ask_yn "Create these S3 buckets now (requires AWS CLI configured)?" "n" CREATE_BUCKETS

echo ""
echo -e "${CYAN}─── Git Repository ────────────────────────────────────────────${NC}"

# Detect if running inside an already-cloned repo (e.g. GitHub "Use this template")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${SCRIPT_DIR}/iac/Pulumi.yaml" ]]; then
  IN_PLACE="y"
  TARGET_DIR="$SCRIPT_DIR"
  info "Detected: running inside the template repo. Will configure in-place."
else
  IN_PLACE="n"
  ask "Target directory for the project" "./${PROJECT_SLUG}" TARGET_DIR
fi

ask "Your git remote URL (leave empty to skip)" "" GIT_REMOTE

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}─── Summary ───────────────────────────────────────────────────${NC}"
echo -e "  Project:     ${BOLD}${PROJECT_TITLE}${NC}"
echo -e "  Slug:        ${PROJECT_SLUG}"
echo -e "  Prefix:      ${PROJECT_PREFIX}"
echo -e "  Description: ${PROJECT_DESCRIPTION}"
echo -e "  Domain:      ${BASE_DOMAIN:-<not set>}"
echo -e "  Backend:     $(case $BE_LANG_CHOICE in 1) echo Rust;; 2) echo Python;; 3) echo Both;; esac)"
echo -e "  Region:      ${AWS_REGION}"
echo -e "  Account:     ${AWS_ACCOUNT_ID}"
echo -e "  Target dir:  ${TARGET_DIR}${IN_PLACE:+ (in-place)}"
echo ""
ask_yn "Proceed with initialization?" "y" PROCEED

if [[ "$PROCEED" != "y" ]]; then
  echo "Aborted."
  exit 0
fi

# ── 2. Clone or copy ─────────────────────────────────────────────────────────
echo ""
info "Setting up project directory..."

if [[ "$IN_PLACE" == "y" ]]; then
  cd "$TARGET_DIR"
  ok "Working in-place at ${TARGET_DIR}"
elif [[ -d "$TARGET_DIR/.git" ]]; then
  cd "$TARGET_DIR"
  ok "Directory already exists and is a git repo. Using as-is."
else
  git clone "$TEMPLATE_REPO" "$TARGET_DIR"
  ok "Cloned template to ${TARGET_DIR}"
  cd "$TARGET_DIR"
fi

# If this was cloned from the template, reset history for a clean start
if git log --oneline -1 2>/dev/null | grep -q "template\|Template\|Initial commit"; then
  rm -rf .git
  git init
  ok "Initialized fresh git repository"
fi

# ── 3. Rename Pulumi project ─────────────────────────────────────────────────
info "Configuring Pulumi..."

sed -i.bak "s/name: emergent-serverless-template/name: ${PROJECT_SLUG}/" iac/Pulumi.yaml
sed -i.bak "s/description: .*/description: ${PROJECT_DESCRIPTION}/" iac/Pulumi.yaml
rm -f iac/Pulumi.yaml.bak

# Update dev stack config
sed -i.bak "s/emergent-serverless-template:projectPrefix: .*/  ${PROJECT_SLUG}:projectPrefix: ${PROJECT_PREFIX}/" iac/Pulumi.dev.yaml
sed -i.bak "s/emergent-serverless-template:stackName: .*/  ${PROJECT_SLUG}:stackName: dev/" iac/Pulumi.dev.yaml
sed -i.bak "s/emergent-serverless-template:logRetentionDays:/${PROJECT_SLUG}:logRetentionDays:/" iac/Pulumi.dev.yaml
sed -i.bak "s/emergent-serverless-template:lambdaArtifactsDir:/${PROJECT_SLUG}:lambdaArtifactsDir:/" iac/Pulumi.dev.yaml
sed -i.bak "s/emergent-serverless-template:userFrontendBundleDir:/${PROJECT_SLUG}:userFrontendBundleDir:/" iac/Pulumi.dev.yaml
sed -i.bak "s/emergent-serverless-template:adminFrontendBundleDir:/${PROJECT_SLUG}:adminFrontendBundleDir:/" iac/Pulumi.dev.yaml
sed -i.bak "s|aws:region: .*|aws:region: ${AWS_REGION}|" iac/Pulumi.dev.yaml
rm -f iac/Pulumi.dev.yaml.bak

# Update prod stack config
sed -i.bak "s/emergent-serverless-template:projectPrefix: .*/  ${PROJECT_SLUG}:projectPrefix: ${PROJECT_PREFIX}/" iac/Pulumi.prod.yaml
sed -i.bak "s/emergent-serverless-template:stackName: .*/  ${PROJECT_SLUG}:stackName: prod/" iac/Pulumi.prod.yaml
sed -i.bak "s/emergent-serverless-template:logRetentionDays:/${PROJECT_SLUG}:logRetentionDays:/" iac/Pulumi.prod.yaml
sed -i.bak "s/emergent-serverless-template:lambdaArtifactsDir:/${PROJECT_SLUG}:lambdaArtifactsDir:/" iac/Pulumi.prod.yaml
sed -i.bak "s/emergent-serverless-template:userFrontendBundleDir:/${PROJECT_SLUG}:userFrontendBundleDir:/" iac/Pulumi.prod.yaml
sed -i.bak "s/emergent-serverless-template:adminFrontendBundleDir:/${PROJECT_SLUG}:adminFrontendBundleDir:/" iac/Pulumi.prod.yaml
sed -i.bak "s|aws:region: .*|aws:region: ${AWS_REGION}|" iac/Pulumi.prod.yaml
rm -f iac/Pulumi.prod.yaml.bak

# Update region in __main__.py
sed -i.bak "s/ap-southeast-2/${AWS_REGION}/g" iac/__main__.py
rm -f iac/__main__.py.bak

ok "Pulumi config updated"

# ── 4. Update frontend config ────────────────────────────────────────────────
info "Updating frontend configuration..."

sed -i.bak "s/ap-southeast-2/${AWS_REGION}/g" frontend/src/aws-config.js
rm -f frontend/src/aws-config.js.bak

if [[ -f admin-frontend/src/aws-config.js ]]; then
  sed -i.bak "s/ap-southeast-2/${AWS_REGION}/g" admin-frontend/src/aws-config.js
  rm -f admin-frontend/src/aws-config.js.bak
fi

ok "Frontend config updated"

# ── 5. Remove unwanted backend implementations ───────────────────────────────
info "Pruning backend by language choice..."

case "$BE_LANG_CHOICE" in
  1)
    find backend/feature -type d -name "*_py" -exec rm -rf {} + 2>/dev/null || true
    rm -f backend/server.py backend/requirements.txt
    ok "Removed Python backend code (keeping Rust only)"
    ;;
  2)
    find backend/feature -type d -name "*_rs" -exec rm -rf {} + 2>/dev/null || true
    rm -f backend/Cargo.toml backend/rust-toolchain.toml
    rm -rf backend/shared/modules_rs
    ok "Removed Rust backend code (keeping Python only)"
    ;;
  3)
    ok "Keeping both Rust and Python backends"
    ;;
esac

# ── 6. Remove unwanted features ──────────────────────────────────────────────
info "Pruning features..."

if [[ "$FEAT_AUTH" == "n" ]]; then
  rm -rf backend/feature/auth_rs backend/feature/auth_py
  rm -rf frontend/src/features/auth admin-frontend/src/features/auth 2>/dev/null || true
  ok "Removed auth feature"
fi

if [[ "$FEAT_USER_PROFILE" == "n" ]]; then
  rm -rf backend/feature/user_profile_rs backend/feature/user_profile_py
  rm -rf frontend/src/features/user_profile admin-frontend/src/features/user_profile 2>/dev/null || true
  ok "Removed user_profile feature"
fi

if [[ "$FEAT_ADMIN" == "n" ]]; then
  rm -rf admin-frontend
  ok "Removed admin feature (entire admin-frontend)"
fi

# ── 7. Create .env files ─────────────────────────────────────────────────────
info "Creating environment files..."

cat > .env <<EOF
# Project: ${PROJECT_TITLE}
# Generated by init-project.sh

AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}
AWS_REGION=${AWS_REGION}
PROJECT_SLUG=${PROJECT_SLUG}
PROJECT_PREFIX=${PROJECT_PREFIX}
PULUMI_BACKEND_URL_DEV=s3://${PULUMI_BUCKET_DEV}
PULUMI_BACKEND_URL_PROD=s3://${PULUMI_BUCKET_PROD}
EOF

cat > frontend/.env <<EOF
REACT_APP_AWS_REGION=${AWS_REGION}
REACT_APP_USER_POOL_ID=
REACT_APP_USER_POOL_CLIENT_ID=
REACT_APP_APPSYNC_URL=
REACT_APP_FLAVOR=dev
EOF

if [[ -d admin-frontend ]]; then
  cat > admin-frontend/.env <<EOF
REACT_APP_AWS_REGION=${AWS_REGION}
REACT_APP_ADMIN_POOL_ID=
REACT_APP_ADMIN_POOL_CLIENT_ID=
REACT_APP_APPSYNC_URL=
REACT_APP_FLAVOR=dev
EOF
fi

ok "Created .env files (fill in values after first pulumi up)"

# ── 8. Configure AWS credentials ─────────────────────────────────────────────
if [[ "$CONFIGURE_AWS_CREDS" == "y" && -n "$AWS_ACCESS_KEY" ]]; then
  info "Configuring AWS credentials..."
  mkdir -p ~/.aws
  PROFILE="${PROJECT_SLUG}"

  if ! grep -q "\[profile ${PROFILE}\]" ~/.aws/config 2>/dev/null; then
    cat >> ~/.aws/config <<EOF

[profile ${PROFILE}]
region = ${AWS_REGION}
output = json
EOF
  fi

  if ! grep -q "\[${PROFILE}\]" ~/.aws/credentials 2>/dev/null; then
    cat >> ~/.aws/credentials <<EOF

[${PROFILE}]
aws_access_key_id = ${AWS_ACCESS_KEY}
aws_secret_access_key = ${AWS_SECRET_KEY}
EOF
  fi

  echo "export AWS_PROFILE=${PROFILE}" >> .env
  ok "AWS profile '${PROFILE}' configured"
fi

# ── 9. Create Pulumi state buckets ───────────────────────────────────────────
if [[ "$CREATE_BUCKETS" == "y" ]]; then
  info "Creating Pulumi state S3 buckets..."
  AWS_OPTS=""
  if [[ -n "${AWS_ACCESS_KEY:-}" ]]; then
    AWS_OPTS="--profile ${PROJECT_SLUG}"
  fi

  for bucket in "$PULUMI_BUCKET_DEV" "$PULUMI_BUCKET_PROD"; do
    if aws s3 ls "s3://${bucket}" $AWS_OPTS 2>/dev/null; then
      warn "Bucket ${bucket} already exists, skipping."
    else
      aws s3 mb "s3://${bucket}" --region "$AWS_REGION" $AWS_OPTS
      aws s3api put-bucket-versioning --bucket "$bucket" --versioning-configuration Status=Enabled $AWS_OPTS
      ok "Created bucket: ${bucket} (versioning enabled)"
    fi
  done
fi

# ── 10. Update README ────────────────────────────────────────────────────────
info "Updating README..."

cat > README.md <<EOF
# ${PROJECT_TITLE}

${PROJECT_DESCRIPTION}

**Stack:** Rust Lambdas · DynamoDB · Cognito · AppSync · React + Amplify · Pulumi (Python) · AWS \`${AWS_REGION}\`.

## Prerequisites

- Rust + cargo-lambda: \`rustup target add aarch64-unknown-linux-gnu && cargo install cargo-lambda\`
- Python 3.11+: \`pip install -r iac/requirements.txt\`
- Node.js 18+ & Yarn
- Pulumi CLI: \`brew install pulumi/tap/pulumi\` (or see https://www.pulumi.com/docs/install/)
- AWS CLI configured with profile \`${PROJECT_SLUG}\`
- Docker (for local DynamoDB)

## Quick Start

\`\`\`bash
# 1. Install dependencies
cd frontend && yarn install && cd ..
$(if [[ -d admin-frontend ]]; then echo "cd admin-frontend && yarn install && cd .."; fi)
cd iac && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# 2. Deploy infrastructure (dev)
export AWS_PROFILE=${PROJECT_SLUG}
export PULUMI_BACKEND_URL=s3://${PULUMI_BUCKET_DEV}
cd iac
pulumi stack init dev
pulumi up

# 3. Copy outputs to .env files
# After pulumi up, copy the outputted values (pool IDs, AppSync URL) to frontend/.env
\`\`\`

## Local Development (no AWS account needed)

\`\`\`bash
# Start local DynamoDB
docker run -d -p 8000:8000 amazon/dynamodb-local

# Start backend
cd backend && cargo run -p local_proxy    # http://localhost:9000

# Start frontend
cd frontend && yarn start                 # http://localhost:3000
$(if [[ -d admin-frontend ]]; then echo "
# Start admin
cd admin-frontend && yarn start           # http://localhost:3001"; fi)
\`\`\`

## Project Structure

| Directory | Purpose |
|-----------|---------|
| \`backend/\` | $(case $BE_LANG_CHOICE in 1) echo "Rust Lambda handlers";; 2) echo "Python Lambda handlers";; 3) echo "Rust + Python Lambda handlers";; esac) |
| \`frontend/\` | React user-facing app (Amplify v6, shadcn/ui) |
$(if [[ -d admin-frontend ]]; then echo "| \`admin-frontend/\` | React admin app |"; fi)
| \`iac/\` | Pulumi (Python) infrastructure-as-code |
| \`system-design-doc/\` | Architecture & feature documentation |

## Deployment

\`\`\`bash
# Production
export PULUMI_BACKEND_URL=s3://${PULUMI_BUCKET_PROD}
cd iac && pulumi stack select prod && pulumi up
\`\`\`
EOF

ok "README updated"

# ── 11. Set up git remote ────────────────────────────────────────────────────
if [[ -n "$GIT_REMOTE" ]]; then
  git remote add origin "$GIT_REMOTE"
  ok "Git remote set to ${GIT_REMOTE}"
fi

# ── 12. Initial commit ───────────────────────────────────────────────────────
git add -A
git commit -m "Initial project setup: ${PROJECT_TITLE}

Initialized from serverless-project-template template.
Backend: $(case $BE_LANG_CHOICE in 1) echo Rust;; 2) echo Python;; 3) echo Rust+Python;; esac)
Region: ${AWS_REGION}"

ok "Created initial commit"

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Project initialized successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BOLD}Next steps:${NC}"
echo ""
echo "  1. cd ${TARGET_DIR}"
echo ""
echo "  2. Install dependencies:"
echo "     cd frontend && yarn install && cd .."
if [[ -d admin-frontend ]]; then
echo "     cd admin-frontend && yarn install && cd .."
fi
echo "     cd iac && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
echo ""
echo "  3. For local development (no AWS needed):"
echo "     docker run -d -p 8000:8000 amazon/dynamodb-local"
echo "     cd backend && cargo run -p local_proxy &"
echo "     cd frontend && yarn start"
echo ""
echo "  4. To deploy to AWS:"
echo "     export AWS_PROFILE=${PROJECT_SLUG}"
echo "     export PULUMI_BACKEND_URL=s3://${PULUMI_BUCKET_DEV}"
echo "     cd iac && pulumi stack init dev && pulumi up"
echo ""
echo "  5. After 'pulumi up', copy the stack outputs to frontend/.env:"
echo "     REACT_APP_USER_POOL_ID=<from output>"
echo "     REACT_APP_USER_POOL_CLIENT_ID=<from output>"
echo "     REACT_APP_APPSYNC_URL=<from output>"
echo ""
if [[ -n "$GIT_REMOTE" ]]; then
echo "  6. Push to remote:"
echo "     git push -u origin main"
echo ""
fi
echo -e "${CYAN}Happy building! 🚀${NC}"
