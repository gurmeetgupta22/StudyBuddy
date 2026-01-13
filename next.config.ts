import type { NextConfig } from "next";
import path from "node:path";

const LOADER = path.resolve(__dirname, 'src/visual-edits/component-tagger-loader.js');

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: '**',
      },
    ],
  },
  outputFileTracingRoot: path.resolve(__dirname, '../../'),
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  allowedDevOrigins: [
    '3000-eea3275b-cede-441c-8c1f-5109dd56111c.orchids.cloud'
  ],
  experimental: {
    serverActions: {
      allowedOrigins: [
        '3000-eea3275b-cede-441c-8c1f-5109dd56111c.proxy.daytona.works',
        '3000-eea3275b-cede-441c-8c1f-5109dd56111c.orchids.cloud'
      ],
    },
  },
  turbopack: {
    rules: {
      "*.{jsx,tsx}": {
        loaders: [LOADER]
      }
    }
  }
};

export default nextConfig;
// Orchids restart: 1768213824057
