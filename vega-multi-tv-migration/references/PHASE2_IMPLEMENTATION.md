# Vega Shared Workspace Conversion

Convert an existing Vega OS project to a yarn workspaces monorepo enabling code reuse across Vega, Android TV, and Apple TV.

## Prerequisites

- Completed Phase 1 analysis document (see [PHASE1_ANALYSIS.md](PHASE1_ANALYSIS.md))
- Source Vega project path
- Target monorepo destination path

## Tools

| Tool | Version | Purpose |
|---|---|---|
| yarn | 4.5.0+ | Package manager with workspaces |
| node | 18.x+ | JavaScript runtime |
| metro | 0.72.x | React Native bundler |
| babel | 7.x | JavaScript compiler with VMRP preset |

```bash
yarn init -2                              # Initialize yarn 4
yarn set version stable                   # Set to latest stable
yarn install                              # Install dependencies
yarn workspace @myapp/vega run <script>   # Run vega package scripts
```

## Conversion Parts

| Part | Description | Checkpoint |
|---|---|---|
| A | Scaffold monorepo, preserve original imports | Vega builds identically |
| B | Screen-by-screen component extraction (optional) | Shared components work |
| C | Refactor to generic imports via VMRP | Platform-agnostic shared code |

Replace `myapp` with project name throughout.

## Target Structure

```
myapp/
├── package.json                 # Root workspace config
├── tsconfig.json                # Required by Expo CLI
├── .yarnrc.yml                  # Yarn 4 config
├── packages/
│   ├── shared/                  # @myapp/shared
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── index.ts             # Barrel exports
│   │   └── src/
│   │       ├── assets/          # Shared images, animations
│   │       ├── components/      # Shared UI (with platform extensions)
│   │       ├── hooks/           # Shared custom hooks
│   │       ├── providers/       # Context providers
│   │       ├── reactquery/      # React Query hooks/config
│   │       ├── services/        # API clients, business logic
│   │       └── utils/           # Utility functions (scaling, math, etc.)
│   ├── vega/                    # @myapp/vega
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── metro.config.js
│   │   ├── babel.config.js
│   │   ├── manifest.toml
│   │   ├── index.js
│   │   └── src/
│   │       ├── App.tsx          # Main app entry
│   │       ├── assets/          # Vega-specific assets
│   │       ├── components/      # Vega-specific components
│   │       ├── navigation/      # Navigation config
│   │       └── screens/         # Screen containers
│   └── expotv/                  # @myapp/expotv
│       ├── package.json
│       ├── tsconfig.json
│       ├── metro.config.js
│       ├── app.json             # Expo config
│       ├── app/                 # Expo Router screens
│       │   ├── _layout.tsx
│       │   └── (tabs)/          # Tab-based navigation
│       ├── assets/              # Expo TV-specific assets
│       ├── components/          # Expo TV-specific components
│       ├── constants/           # Theme constants (Colors, TextStyles)
│       ├── hooks/               # Platform-specific hooks (useScale, useColorScheme)
│       └── layouts/             # Layout components (TabLayout)
```

## Configuration Templates

All templates in [assets/templates/](../assets/templates/) with companion `.md` docs for critical settings. Templates are referenced in each Part below where they're needed.

Expo TV templates:
- **package.json** — [Template](../assets/templates/expotv-package.json) | [Docs](../assets/templates/expotv-package.json.md)
- **app.json** — [Template](../assets/templates/expotv-app.json) | [Docs](../assets/templates/expotv-app.json.md)
- **metro.config.js** — [Template](../assets/templates/expotv-metro.config.js)

## Part A: Scaffold Monorepo

Create the monorepo structure, move code per Phase 1 analysis, keep all `@amazon-devices/*` imports unchanged.

### Directory Setup

```bash
mkdir myapp
cd myapp
yarn init -2
yarn set version stable
mkdir -p packages/shared/src/{assets,components,hooks,providers,reactquery,services,utils}
mkdir -p packages/vega/src/{assets,components,navigation,screens}
mkdir -p packages/expotv/{app,assets,components,constants,hooks,layouts}
mkdir -p packages/expotv/app/\(tabs\)
mkdir -p packages/expotv/assets/{fonts,images,tv_icons}
mkdir -p packages/expotv/components/navigation
mkdir -p packages/expotv/scripts
```

### Configuration Files

Apply templates from [assets/templates/](../assets/templates/):

1. **Root package.json** — [Template](../assets/templates/root-package.json): workspaces config with `nohoist` for React/React Native
2. **Root tsconfig.json** — [Template](../assets/templates/root-tsconfig.json): required by Expo CLI
3. **.yarnrc.yml** — [Template](../assets/templates/yarnrc.yml): MUST have `nmHoistingLimits: workspaces`
4. **Shared package.json** — [Template](../assets/templates/shared-package.json): ONLY `peerDependencies`, no `devDependencies` for react/react-native
5. **Vega metro.config.js** — [Template](../assets/templates/vega-metro.config.js): monorepo resolution with `watchFolders`

### Shared Package Barrel Exports

`packages/shared/index.ts` (at package root, not in src/):

```typescript
// Re-export from src modules
export * from "./src/components/Banner";
export * from "./src/components/HomeScreen";
export * from "./src/utils/scaling";
export * from "./src/services/httpClient";
// Add more exports as needed
```

`packages/shared/src/index.ts` (optional, for internal use):

```typescript
export { Banner } from "./components/Banner";
export { HomeScreen } from "./components/HomeScreen";
export { scaleWidth, scaleHeight } from "./utils/scaling";
```

### Vega Package Setup

Copy existing Vega project to `packages/vega/`. Add shared dependency to `packages/vega/package.json`:

```json
{
  "name": "@myapp/vega",
  "dependencies": {
    "@myapp/shared": "*"
  }
}
```

The `*` version ensures Yarn uses the local workspace version.

### Code Migration

Per Phase 1 analysis, move to `packages/shared/src/`:
- Category A dependencies (JS-only)
- Category B dependencies (VMRP-compatible)
- Shared components, hooks, services, utils

Keep original `@amazon-devices/*` imports unchanged. Update consumer imports to use `@myapp/shared`:

```typescript
import { Banner, useFocusState } from "@myapp/shared";
```

Platform-specific files use extensions:
```
components/
├── BannerLogo.tsx           # Default/fallback
├── BannerLogo.kepler.tsx    # Vega-specific
├── BannerLogo.android.tsx   # Android TV
├── BannerLogo.ios.tsx       # Apple TV
└── BannerLogo.web.tsx       # Web
```

**Checkpoint:** `yarn install && yarn vega:build` — app builds and runs identically to before.

## Part B: Component Extraction (Optional)

Skip if extracting components later during Phase 3.

For each screen:
1. Identify shared UI vs platform-specific components
2. Create shared component with platform-agnostic props
3. Create platform-specific implementations where needed (`.kepler.tsx`, `.android.tsx`)
4. Update screen to import from shared
5. Verify on Vega

## Platform-Specific Strategies

### Strategy 1: File Extensions

Metro resolves the correct file based on target platform:
```
Component.tsx           # Default/fallback
Component.kepler.tsx    # Vega
Component.android.tsx   # Android TV
Component.ios.tsx       # Apple TV
```

Use when: implementation differs significantly but API is identical.

### Strategy 2: Inline Conditionals

```tsx
import { Platform } from "react-native";
const padding = Platform.select({ kepler: 20, android: 16, web: 24 });
```

Use when: small styling or feature flag differences.

### Strategy 3: Screen Container Pattern

```
vega/screens/HomeScreen.tsx       → Platform container
expotv/screens/HomeScreen.tsx     → Platform container
  └── both import <HomeContent /> → from @myapp/shared
```

Use when: screens have platform-specific navigation/lifecycle but share visual layout. Also for components requiring different native modules (VideoPlayer, MediaControls).

### Strategy 4: VMRP

Write standard React Native imports; VMRP maps to `@amazon-devices/*` at bundle time:

```tsx
// Shared code writes:
import Animated from "react-native-reanimated";
// VMRP resolves to @amazon-devices/react-native-reanimated on Vega
```

Use when: third-party libraries have Vega-ported equivalents.

### Strategy Selection

| Scenario | Strategy |
|---|---|
| Different native implementations | File Extensions |
| Minor styling/feature differences | Inline Conditionals |
| Platform-specific navigation/lifecycle | Screen Container |
| Platform-specific native modules (VideoPlayer) | Screen Container |
| Third-party library with Vega port | VMRP |

## Part C: VMRP Configuration

Refactor shared package to standard React Native imports. VMRP handles mapping to `@amazon-devices/*` at bundle time.

### 1. Add VMRP Dependencies

`packages/vega/package.json` devDependencies:

```json
{
  "devDependencies": {
    "@amazon-devices/kepler-module-resolver-preset": "^0.1.15",
    "babel-plugin-module-resolver": "^5.0.2"
  }
}
```

### 2. Configure Babel

`packages/vega/babel.config.js`:

```javascript
module.exports = {
  presets: [
    "module:metro-react-native-babel-preset",
    "module:@amazon-devices/kepler-module-resolver-preset",
  ],
  plugins: [["@babel/plugin-transform-react-jsx", { runtime: "automatic" }]],
};
```

### 3. Add Both Library Versions

For each VMRP-compatible library, add both standard and Vega versions to `packages/vega/package.json`:

```json
{
  "dependencies": {
    "react-native-reanimated": "3.5.4",
    "@amazon-devices/react-native-reanimated": "~2.0.0",

    "react-native-gesture-handler": "2.13.0",
    "@amazon-devices/react-native-gesture-handler": "2.0.0+2.13.0",

    "@react-navigation/native": "6.1.9",
    "@amazon-devices/react-navigation__native": "^2.0.0"
  }
}
```

### 4. Refactor Shared Imports

Change from `@amazon-devices/*` to standard imports:

```tsx
// Before
import Animated from "@amazon-devices/react-native-reanimated";

// After
import Animated from "react-native-reanimated";
```

**Checkpoint:** `yarn install && yarn vega:build` — shared code uses standard imports, ready for other platforms.

## Expo TV Scaffold

The Expo TV package uses Expo Router for file-based routing. It will NOT fully work until platform dependencies are implemented in [Phase 3](PHASE3_PLATFORM_SUPPORT.md).

`packages/expotv/package.json`:

```json
{
  "name": "mytvproject",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "start": "EXPO_TV=1 npx expo start",
    "android": "EXPO_TV=1 npx expo run:android --device",
    "ios": "EXPO_TV=1 npx expo run:ios",
    "web": "EXPO_TV=1 npx expo start --web",
    "prebuild": "EXPO_TV=1 npx expo prebuild --clean && ./scripts/fix-tvos-deployment.sh",
    "clean": "rm -rf node_modules android ios .expo"
  },
  "dependencies": {
    "@myapp/shared": "*",
    "expo": "~52.0.0",
    "expo-build-properties": "~0.13.0",
    "expo-router": "~4.0.0",
    "react": "18.3.1",
    "react-native": "npm:react-native-tvos@~0.76.0-0"
  },
  "devDependencies": {
    "@react-native-tvos/config-tv": "~0.0.12"
  }
}
```

Root scripts reference by package name:

```json
{
  "scripts": {
    "expotv": "yarn workspace mytvproject",
    "expotv:prebuild": "yarn workspace mytvproject run prebuild",
    "expotv:android": "yarn workspace mytvproject run android",
    "expotv:ios": "yarn workspace mytvproject run ios",
    "expotv:web": "yarn workspace mytvproject run web"
  }
}
```

`packages/expotv/app.json`:

```json
{
  "expo": {
    "name": "MyAppTV",
    "slug": "myapp-tv",
    "orientation": "landscape",
    "platforms": ["android", "ios"],
    "scheme": "myapp-tv",
    "plugins": [
      "@react-native-tvos/config-tv",
      ["expo-build-properties", {
        "android": { "kotlinVersion": "1.9.25" },
        "ios": { "deploymentTarget": "15.1" }
      }],
      "expo-router"
    ]
  }
}
```

## Migration Checklist

### Part A
- [ ] Root workspace configured with yarn 4.5
- [ ] Root tsconfig.json created
- [ ] .yarnrc.yml has `nmHoistingLimits: workspaces`
- [ ] Shared package created with barrel exports
- [ ] Code moved to shared per Phase 1 analysis
- [ ] Vega package references `@myapp/shared`
- [ ] Metro config updated for monorepo
- [ ] Vega builds and runs

### Part B (Optional)
- [ ] Shared components extracted
- [ ] Platform-specific implementations created where needed
- [ ] Vega builds with extracted components

### Part C
- [ ] VMRP configured in babel.config.js
- [ ] Both library versions in vega package.json
- [ ] Shared imports refactored to standard names
- [ ] Vega builds with refactored imports

## Common Issues

| Issue | Solution |
|---|---|
| Yarn 3.x or lower installed | `corepack enable && yarn set version stable` |
| Node.js < 20 | Upgrade to Node.js 20+; use `nvm install --lts && nvm use --lts` |
| Wrong yarn version used in CI | Add `"packageManager": "yarn@4.5.0"` to root package.json |
| node_modules not found after install | Ensure .yarnrc.yml has `nodeLinker: node-modules` (Yarn 4 defaults to PnP) |
| Metro can't resolve shared | Configure `watchFolders` and `nodeModulesPaths` in metro.config.js |
| Symlink resolution failures | Add `resolver.unstable_enableSymlinks: true` to metro.config.js |
| Duplicate React versions | Verify .yarnrc.yml has `nmHoistingLimits: workspaces` |
| Can't find `@myapp/shared` at runtime | Verify `"@myapp/shared": "*"` in consumer's dependencies, not just imports |
| Workspace changes not detected | Run `yarn install` after modifying any workspace package.json |
| Lint/type errors in shared package | Add dependencies as devDependencies in shared's package.json (not just peerDependencies) |
| TypeScript path aliases not resolving | Add paths mapping in root tsconfig.json for `@myapp/*` packages |
| Kepler imports fail in shared | Use `.kepler.tsx` extension or move to vega package |
| Babel cache stale after VMRP changes | Run `yarn vega run clean` or delete `node_modules/.cache` |
| Native module version mismatch | Ensure native deps (reanimated, gesture-handler) have identical versions across all packages |

## Related Documents

- Analysis (previous phase): [PHASE1_ANALYSIS.md](PHASE1_ANALYSIS.md)
- Platform dependencies (next phase): [PHASE3_PLATFORM_SUPPORT.md](PHASE3_PLATFORM_SUPPORT.md)
- Templates: [assets/templates/](../assets/templates/)
