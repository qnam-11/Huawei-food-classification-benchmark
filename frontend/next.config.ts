import type { NextConfig } from "next";

// Fail a Vercel build instead of shipping a frontend that calls localhost.
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

if (process.env.VERCEL && !apiUrl?.startsWith("https://")) {
  throw new Error(
    "NEXT_PUBLIC_API_URL must be the backend's https:// URL. Set it in the Vercel project before deploying.",
  );
}

const nextConfig: NextConfig = {
  /* config options here */
  allowedDevOrigins: ["172.16.4.212"],
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
