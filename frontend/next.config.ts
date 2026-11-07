import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "export",
  webpack(config, { isServer }) {
    if (!isServer && config.optimization?.splitChunks && typeof config.optimization.splitChunks === "object") {
      config.optimization.splitChunks.cacheGroups = {
        ...config.optimization.splitChunks.cacheGroups,
        reactPdf: {
          test: /[\\/]node_modules[\\/](@react-pdf|yoga-layout|fontkit|linebreak|unicode-properties|jsbarcode)[\\/]/,
          name: "react-pdf",
          chunks: "async",
          priority: 30,
          reuseExistingChunk: true,
        },
      };
    }
    return config;
  },
};

export default nextConfig;
