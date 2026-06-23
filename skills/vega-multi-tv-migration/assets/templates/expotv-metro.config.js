const { getDefaultConfig } = require("expo/metro-config");
const path = require("path");

const projectRoot = __dirname;
const monorepoRoot = path.resolve(projectRoot, "..");

const config = getDefaultConfig(projectRoot);

// Watch shared package for hot reload
config.watchFolders = [path.resolve(monorepoRoot, "shared")];

// Resolve from local and parent node_modules
config.resolver.nodeModulesPaths = [
  path.resolve(projectRoot, "node_modules"),
  path.resolve(monorepoRoot, "node_modules"),
];

config.resolver.resolverMainFields = ["react-native", "browser", "main"];

// TV-specific file extensions: .tv.tsx, .tv.ts resolved before .tsx, .ts
// Allows platform-specific implementations for TV platforms
if (process.env?.EXPO_TV === "1") {
  const originalSourceExts = config.resolver.sourceExts;
  config.resolver.sourceExts = [
    ...originalSourceExts.map((e) => `tv.${e}`),
    ...originalSourceExts,
  ];
}

module.exports = config;
