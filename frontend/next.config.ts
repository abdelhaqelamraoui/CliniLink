import type { NextConfig } from "next";

const nextConfig: NextConfig = {
<<<<<<< Updated upstream
  /* config options here */
  output: "standalone",
  experimental: {
    agentFeedback: true,
  },
  cacheComponents: true,
  partialPrefetching: true,
=======
  // Self-contained server in .next/standalone, used by the Docker image.
  output: "standalone",
  experimental: {
    // 404 page for URLs outside /en and /ar (the root layout lives under app/[lang]).
    globalNotFound: true,
  },
>>>>>>> Stashed changes
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
