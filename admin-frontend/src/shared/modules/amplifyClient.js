import { Amplify } from "aws-amplify";
import { generateClient } from "aws-amplify/api";
import { adminPoolConfig } from "@/aws-config";

export function bootstrap() {
  Amplify.configure(adminPoolConfig);
}

export const gqlClient = () => generateClient();
