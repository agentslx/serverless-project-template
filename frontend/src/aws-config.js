/**
 * Amplify v6 configuration — USER app only.
 * For admin auth see the separate `/app/admin-frontend` project.
 */

const region = process.env.REACT_APP_AWS_REGION || "ap-southeast-2";

export const userPoolConfig = {
  Auth: {
    Cognito: {
      region,
      userPoolId: process.env.REACT_APP_USER_POOL_ID,
      userPoolClientId: process.env.REACT_APP_USER_POOL_CLIENT_ID,
      loginWith: { email: true },
    },
  },
  API: {
    GraphQL: {
      endpoint: process.env.REACT_APP_APPSYNC_URL,
      region,
      defaultAuthMode: "userPool",
    },
  },
};

export const flavour = process.env.REACT_APP_FLAVOR || "dev";
export const adminAppUrl =
  process.env.REACT_APP_ADMIN_APP_URL || "http://localhost:3001";
