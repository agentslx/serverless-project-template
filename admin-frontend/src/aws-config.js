/**
 * Amplify v6 configuration — ADMIN app only.
 * This app has *no* awareness of the user pool. It only ever talks to the
 * admin Cognito pool. That separation is the whole point of running two
 * physically distinct frontends.
 */
const region = process.env.REACT_APP_AWS_REGION || "ap-southeast-2";

export const adminPoolConfig = {
  Auth: {
    Cognito: {
      region,
      userPoolId: process.env.REACT_APP_ADMIN_POOL_ID,
      userPoolClientId: process.env.REACT_APP_ADMIN_POOL_CLIENT_ID,
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
export const userAppUrl =
  process.env.REACT_APP_USER_APP_URL || "http://localhost:3000";
