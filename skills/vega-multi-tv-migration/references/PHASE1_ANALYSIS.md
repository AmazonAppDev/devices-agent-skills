# Vega Shared Workspace Migration Analysis

Guidance for analyzing Vega React Native codebases for conversion to a shared workspace (monorepo). The monorepo enables code reuse across Vega, Android TV, and Apple TV while keeping platform-specific implementations where necessary.

## When to Use

- Planning multi-platform TV support from a single codebase
- Evaluating migration complexity before committing resources
- Maximizing code reuse between Vega and Stock React Native

## Target Monorepo Structure

```
myapp/
├── package.json              # Root workspaces config
├── tsconfig.json             # Shared TypeScript config
├── .yarnrc.yml               # Yarn 4 config
├── packages/
│   ├── shared/               # @myapp/shared
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── index.ts          # Barrel exports
│   │   └── src/
│   │       ├── assets/       # Shared images, animations
│   │       ├── components/   # Shared UI components
│   │       ├── hooks/        # Shared custom hooks
│   │       ├── providers/    # Context providers
│   │       ├── reactquery/   # React Query hooks/config
│   │       ├── services/     # API/business logic
│   │       └── utils/
│   ├── vega/                 # @myapp/vega
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── metro.config.js
│   │   ├── manifest.toml
│   │   └── src/
│   │       ├── components/   # Vega-specific components
│   │       ├── navigation/
│   │       └── screens/      # Screen containers
│   └── expotv/               # @myapp/expotv
│       ├── package.json
│       ├── tsconfig.json
│       ├── app.json          # Expo config
│       ├── metro.config.js
│       ├── app/              # Expo Router screens
│       │   ├── _layout.tsx
│       │   └── (tabs)/       # Tab-based navigation
│       ├── assets/           # Expo TV-specific assets
│       ├── components/       # Expo TV-specific components
│       ├── constants/        # Theme constants
│       ├── hooks/            # Platform-specific hooks
│       └── layouts/          # Layout components
```

Root workspaces config uses `nohoist` for React/React Native to avoid duplicate module issues in native builds.

**Key constraint:** vega/expotv import FROM shared, but shared CANNOT import from vega/expotv. Use dependency injection when shared code needs platform behavior.

## Dependency Classification

Categorize all `@amazon-devices/*` dependencies into three categories.

### Category A: JS Implementations → Shared Package

Pure JavaScript/TypeScript with no native code: custom hooks, utilities, UI components wrapping platform APIs, state management (Zustand, Context), business logic services.

### Category B: VMRP-Compatible → Shared Package

Use standard import paths in shared code. VMRP maps them to `@amazon-devices/*` at bundle time for Vega.

| Standard Import | Vega Equivalent |
|---|---|
| `react-native-reanimated` | `@amazon-devices/react-native-reanimated` |
| `react-native-gesture-handler` | `@amazon-devices/react-native-gesture-handler` |
| `react-native-screens` | `@amazon-devices/react-native-screens` |
| `react-native-safe-area-context` | `@amazon-devices/react-native-safe-area-context` |
| `react-native-linear-gradient` | `@amazon-devices/react-native-linear-gradient` |
| `react-native-svg` | `@amazon-devices/react-native-svg` |
| `react-native-fast-image` | `@amazon-devices/react-native-fast-image` |
| `react-native-device-info` | `@amazon-devices/react-native-device-info` |
| `react-native-vector-icons` | `@amazon-devices/react-native-vector-icons` |
| `react-native-mmkv` | `@amazon-devices/react-native-mmkv` |
| `react-native-qrcode-svg` | `@amazon-devices/react-native-qrcode-svg` |
| `lottie-react-native` | `@amazon-devices/lottie-react-native` |
| `@react-navigation/*` | `@amazon-devices/react-navigation-*` |
| `@react-native-async-storage/async-storage` | `@amazon-devices/async-storage` |
| `@react-native-cookies/cookies` | `@amazon-devices/cookies` |
| `@react-native-masked-view/masked-view` | `@amazon-devices/masked-view` |
| `expo-*` libraries | Various `@amazon-devices/expo-*` |

TV Focus APIs share the same API across Vega and react-native-tvos: `TVFocusGuideView`, `nextFocusUp/Down/Left/Right`, `hasTVPreferredFocus`, `isTVSelectable`.

### Category C: Requires Native Implementation → Platform Package

These MUST remain in the vega package. Other platforms need native implementations (Kotlin/Swift):

```
@amazon-devices/headless-task-manager
@amazon-devices/kepler-player-server
@amazon-devices/kepler-player-client
@amazon-devices/keplerscript-turbomodule-api
@amazon-devices/react-native-w3cmedia
@amazon-devices/asset-resolver-lib
@amazon-devices/kepler-channel
@amazon-devices/kepler-epg-provider
@amazon-devices/kepler-epg-sync-scheduler
@amazon-devices/kepler-performance-api
@amazon-devices/kepler-media-controls
@amazon-devices/kepler-media-types
@amazon-devices/kepler-ui-components
@amazon-devices/keplerscript-audio-lib
@amazon-devices/keplerscript-kepleri18n-lib
@amazon-devices/keplerscript-netmgr-lib
@amazon-devices/kepler-cli-platform
@amazon-devices/kepler-file-system
@amazon-devices/kepler-media-account-login
@amazon-devices/kepler-media-content-launcher
@amazon-devices/keplerscript-appstore-iap-lib
@amazon-devices/security-manager-lib
```

`@amazon-devices/react-native-kepler` is a special case—it belongs in the vega package, but most components using it go in shared since they map 1:1 to `@react-native-tvos`.

## Screen Analysis

For each screen, determine placement:

- **Container → Shared**: Entire screen is platform-agnostic
- **Container → Vega, Components → Shared**: Container has platform-specific logic, child components are reusable

Common pattern:
```
vega/screens/HomeScreen.tsx      → platform-specific container
  └── imports <HomeContent />    → from shared/
        └── uses <ContentRow />  → from shared/
        └── uses <HeroCard />    → from shared/
```

### Per-Screen Documentation

For each screen, capture: file path, complexity rating, container placement, Vega dependencies used, migration path per dependency, native code requirements.

**Complexity ratings:**

| Rating | Criteria |
|---|---|
| Low | No native deps, standard UI patterns |
| Medium | Some VMRP-compatible deps, moderate state |
| High | Multiple native deps, complex navigation |
| Critical | Heavy native integration (player, EPG) |

### Component Extraction

For shared components: purpose, required props/callbacks, platform-specific dependencies.

For platform-specific components: why it can't be shared, common interface both platforms use, whether to use file extensions (`.android.tsx`, `.kepler.tsx`).

Example:
```
SelectUserProfile Screen:
├── Shared: Layout, styling, props interface (profiles[], onSelect, onAdd)
├── Vega: <Avatar> from kepler-ui-components
├── Android: <Image> + Pressable with onFocus/onBlur
└── Use SelectUserProfile.kepler.tsx / .android.tsx
```

## Services Inventory

Identify services referenced by 2+ screens. Services with no Vega dependencies are prime shared candidates.

| Service | Used By | Vega Dependencies | Placement |
|---|---|---|---|
| AuthService | Login, Home, Settings | None | Shared |
| PlayerService | Details, Player | kepler-player-client | Vega |
| AnalyticsService | All screens | None | Shared |

## Pre-Migration Refactoring

Recommend light refactoring before migration only if:
- 2+ screens tightly mix platform-specific logic with UI rendering
- Duplicated patterns (loading states, error handling) appear 3+ times
- No clear prop boundaries between platform-specific and platform-agnostic code

Refactoring scope: extract content components from screens, define prop interfaces between container and content. Do NOT restructure folders or change navigation.

## Migration Phases

Group screens by dependency complexity:

1. **Foundation** — Scaffolding, shared navigation, theme, core utilities, auth flow
2. **Core UI Components** — Shared buttons, cards, lists, modals with platform-specific implementations where needed
3. **Content/Browse Screens** — Home, browse, search, details (read-heavy, standard UI)
4. **Interactive Features** — Settings, profiles, favorites, watchlists (state management, limited native)
5. **Media Playback** — Player, controls, progress tracking (heavy native, most complex)

## Effort Estimation

Typical code reuse percentages:

| Category | Expected Reuse |
|---|---|
| Services | 70-90% |
| Utilities/Hooks | 80-95% |
| Components | 50-70% |
| Screens | 30-50% |
| Overall | 50-70% |

## Analysis Output Format

Use this as a sensible default structure, adapting sections based on what the analysis reveals:

```markdown
# [PROJECT NAME] → MONOREPO MIGRATION ANALYSIS

## Executive Summary
[2-3 sentences on complexity and key challenges]
**Estimated Code Reuse: ~XX-XX% overall**

## 1. Project Overview
## 2. Vega Dependency Classification (A/B/C)
## 3. Screen-by-Screen Dependency Mapping
## 4. Services Inventory
## 5. Migration Phases
## 6. Native Modules Required
## 7. Estimated Effort
## 8. Risk Assessment
## 9. Next Steps
```

## Key Rules

- Start with screens having fewest native dependencies
- Validate Vega builds after each change
- Use platform file extensions (`.vega.tsx`, `.android.tsx`) for divergent implementations
- Do NOT migrate player/media screens first
- Do NOT over-abstract before understanding platform differences

## Related Documents

- Implementation: [PHASE2_IMPLEMENTATION.md](PHASE2_IMPLEMENTATION.md)
- Platform support: [PHASE3_PLATFORM_SUPPORT.md](PHASE3_PLATFORM_SUPPORT.md)
- Templates: [assets/templates/](../assets/templates/)
