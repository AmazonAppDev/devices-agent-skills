# Expo TV app.json Configuration

## Critical Settings

### plugins
- `@react-native-tvos/config-tv` - Enables TV support (REQUIRED)
- `expo-build-properties` - Configures native build settings
- `expo-router` - File-based routing for the TV app

### expo-build-properties
- `android.kotlinVersion: "1.9.25"` - CRITICAL: Fixes Kotlin/Compose compiler compatibility
- `ios.deploymentTarget: "15.1"` - REQUIRED for ExpoModulesCore (may need manual fix for tvOS)

### platforms
- Only `["android", "ios"]` - No web support for TV apps

### orientation
- `"landscape"` - TV apps are always landscape

### scheme
- `"myapp-tv"` - URL scheme for deep linking with expo-router

## Customization

Replace these values:
- `name` - Your app display name
- `slug` - URL-friendly identifier
- `scheme` - Your app's URL scheme
