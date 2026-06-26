const path = require("path");
const { getDefaultConfig, mergeConfig } = require("@react-native/metro-config");

const config = {
  // Watch parent directory (packages/) to enable hot reload for shared package
  watchFolders: [path.resolve(__dirname, "..")],
  
  resolver: {
    // Resolve dependencies from local, parent, and root node_modules
    // Required for monorepo to find shared package and its dependencies
    nodeModulesPaths: [
      path.resolve(__dirname, "node_modules"),
      path.resolve(__dirname, "../node_modules"),
      path.resolve(__dirname, "../../node_modules"),
    ],
  },
};

module.exports = mergeConfig(getDefaultConfig(__dirname), config);
