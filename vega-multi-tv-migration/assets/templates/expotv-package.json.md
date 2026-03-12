# Expo TV Package Configuration

## Critical Settings

### Package Name
- `name: "mytvproject"` - The workspace package name referenced by root scripts

### scripts
- All scripts MUST use `EXPO_TV=1` environment variable
- `--device` flag on android avoids conflicts with Vega simulator
- `web` script uses `expo start --web` for web target

### dependencies
- `react-native: "npm:react-native-tvos@~0.76.0-0"` - Uses react-native-tvos fork
- `@myapp/shared: "*"` - Always uses local workspace version
- `expo-router: "~4.0.0"` - File-based routing

## Target Versions
- Expo SDK: ~52.0.0
- react-native-tvos: ~0.76.0-0
- React: 18.3.1
- expo-router: ~4.0.0

## Customization
Replace `@myapp` with your project namespace in the shared dependency
