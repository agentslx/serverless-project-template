/**
 * Amplify wrapper — USER app. The admin app has its own copy of this file
 * configured against the admin Cognito pool.
 */
import { Amplify } from "aws-amplify";
import { generateClient } from "aws-amplify/api";
import { userPoolConfig } from "@/aws-config";

export function bootstrap() {
  Amplify.configure(userPoolConfig);
}

export const gqlClient = () => generateClient();
