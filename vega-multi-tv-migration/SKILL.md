---
name: vega-multi-tv-migration
description: Migrate Vega OS (Amazon Fire TV) applications to multi-platform React Native monorepo supporting Android TV, Apple TV, and other platforms. Covers analysis, implementation, and native module integration. Use when migrating TV apps to support multiple platforms or building new multi-platform TV applications.
---

# Vega Multi-Platform Migration

## Overview

Migrate Vega OS (Fire TV) apps to multi-platform React Native monorepo with 70-85% code reuse across Android TV, Apple TV, and Vega OS.

## When to Apply

Use this skill when user mentions:
- Migrating Vega/Fire TV app to other platforms
- Building multi-platform TV application
- Converting single-platform TV app to monorepo
- Adding Android TV or Apple TV support
- Sharing code between TV platforms
- Setting up Yarn workspaces for TV apps

## Phase Priority Guide

| Priority | Phase | Impact | When to Use |
|----------|-------|--------|-------------|
| 1 | Analysis | CRITICAL | Starting migration, no existing analysis |
| 2 | Implementation | CRITICAL | Have analysis, need monorepo structure |
| 3 | Platform Support | HIGH | Have working Vega monorepo, adding platforms |
| 4 | Configuration | MEDIUM | Troubleshooting build/resolution issues |

## Quick Decision Tree

```
User has existing Vega app?
├─ YES → Do they have migration analysis?
│  ├─ NO → Start Phase 1 (Analysis)
│  └─ YES → Is monorepo set up?
│     ├─ NO → Start Phase 2 (Implementation)
│     └─ YES → Start Phase 3 (Platform Support)
└─ NO → Starting from scratch?
   └─ YES → Skip Phase 1, start Phase 2 with new project
```

## Quick Reference

### Critical: Project Structure
```bash
# Verify monorepo structure exists
ls -la packages/shared packages/vega packages/expotv

# Check Yarn workspaces configured
grep -A5 "workspaces:" package.json
```

### Critical: Dependency Classification
Common patterns for analysis:
- **Shared**: Business logic, UI components, utilities, state management
- **Platform-specific**: Navigation, video players, DRM, native modules
- **VMRP-compatible**: Standard RN libraries that map to Vega equivalents

### High: VMRP Configuration
Quick check if VMRP is working:
```bash
# Should see @vega-tv/react-native-module-resolver-preset
grep "vmrp" packages/vega/babel.config.js
```

## References

### Phase 1: Analysis (analysis-*)

| File | Impact | Description |
|------|--------|-------------|
| [PHASE1_ANALYSIS.md](references/PHASE1_ANALYSIS.md) | CRITICAL | Codebase analysis, dependency classification, migration planning |

**Use when**: Starting migration, no existing analysis document

### Phase 2: Implementation (impl-*)

| File | Impact | Description |
|------|--------|-------------|
| [PHASE2_IMPLEMENTATION.md](references/PHASE2_IMPLEMENTATION.md) | CRITICAL | Monorepo scaffolding, code migration, VMRP setup with template references |

**Use when**: Have analysis, ready to build monorepo structure

### Phase 3: Platform Support (platform-*)

| File | Impact | Description |
|------|--------|-------------|
| [PHASE3_PLATFORM_SUPPORT.md](references/PHASE3_PLATFORM_SUPPORT.md) | HIGH | Android TV and Apple TV implementation |

**Use when**: Have working Vega monorepo, adding new platforms

### Templates
All configuration templates in [assets/templates/](assets/templates/) with companion `.md` docs:
- `root-package.json` - Yarn workspaces setup
- `root-tsconfig.json` - TypeScript project references
- `yarnrc.yml` - Dependency deduplication (CRITICAL)
- `shared-package.json` + `.md` - Shared package config with rules
- `vega-metro.config.js` - Vega Metro with monorepo resolution
- `expotv-package.json` + `.md` - Expo TV package config
- `expotv-app.json` + `.md` - Expo TV configuration with plugins
- `expotv-metro.config.js` - Expo Metro with TV extensions

## Problem → Skill Mapping

| Problem | Start With |
|---------|------------|
| Need to analyze existing Vega app | PHASE1_ANALYSIS.md |
| Have analysis, need monorepo setup | PHASE2_IMPLEMENTATION.md → templates |
| Monorepo exists, adding Android TV | PHASE3_PLATFORM_SUPPORT.md |
| Metro resolution errors | PHASE2_IMPLEMENTATION.md → Metro config |
| Duplicate React versions | PHASE2_IMPLEMENTATION.md → .yarnrc.yml |
| VMRP not mapping imports | PHASE2_IMPLEMENTATION.md → VMRP section |
| TypeScript path errors | PHASE2_IMPLEMENTATION.md → TypeScript config |
| Native module integration | PHASE3_PLATFORM_SUPPORT.md → Native Modules |
| Build configuration issues | PHASE2_IMPLEMENTATION.md → Configuration Files |
| Starting from scratch | PHASE2_IMPLEMENTATION.md (skip Phase 1) |

## Workflow

1. Use the decision tree above to determine the starting phase
2. Load the appropriate reference file for that phase
3. Follow Quick Start → Deep Dive pattern in each reference
4. Verify at each phase's checkpoint before moving to the next phase
5. Use [VALIDATION_CHECKLIST.md](assets/templates/VALIDATION_CHECKLIST.md) for comprehensive verification

## Attribution

Based on Vega OS multi-platform migration patterns and React Native monorepo best practices.
