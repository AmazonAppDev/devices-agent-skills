# Migration Validation Checklist

Use this checklist to verify each phase is complete before proceeding.

## Phase 1: Analysis ✓

- [ ] Project structure documented
- [ ] All dependencies classified (Category A, B, C)
- [ ] Screen-by-screen analysis complete
- [ ] Services inventory created
- [ ] Native modules identified
- [ ] Migration phases defined
- [ ] Effort estimates provided
- [ ] Risk assessment complete
- [ ] Analysis document reviewed and approved

**Before proceeding to Phase 2:**
- [ ] Stakeholders have reviewed the analysis
- [ ] Any descoping decisions have been made
- [ ] Development environment is ready

---

## Phase 2: Implementation ✓

### Step 2A: Scaffold Monorepo

- [ ] Root workspace configured with Yarn 4.5+
- [ ] Root `tsconfig.json` created (required by Expo CLI)
- [ ] `.yarnrc.yml` has `nmHoistingLimits: workspaces`
- [ ] Shared package created with `"main": "src/index.ts"`
- [ ] Shared package has barrel exports (`src/index.ts`)
- [ ] Code copied to shared package per Phase 1 analysis
- [ ] Vega package references `@myapp/shared`
- [ ] Metro configs updated for monorepo resolution
- [ ] Vega builds successfully with original imports
- [ ] Duplicated code removed from vega package
- [ ] Babel config aliases updated to point to shared
- [ ] TypeScript paths updated to point to shared
- [ ] Vega builds and runs after cleanup

### Step 2B: Component Extraction (Optional)

- [ ] Decision made: extract now or defer to Phase 3?
- [ ] If extracting now:
  - [ ] Shared components identified
  - [ ] Platform-specific implementations created
  - [ ] Components exported from `@myapp/shared`
  - [ ] Screens updated to use shared components
  - [ ] Vega builds and runs with extracted components

### Step 2C: VMRP / Generic Imports

- [ ] Shared package imports refactored to standard library names
- [ ] VMRP configured in vega `babel.config.js`
- [ ] Both library versions added to vega `package.json`
- [ ] Kepler-only components kept in vega package
- [ ] Vega builds successfully with refactored imports
- [ ] All tests pass
- [ ] App runs identically to before migration

**Before proceeding to Phase 3:**
- [ ] Vega app is stable and fully functional
- [ ] No regressions from original app
- [ ] Code review completed
- [ ] CI/CD updated for monorepo (if applicable)

---

## Phase 3: Platform Support ✓

### Expo TV Setup

- [ ] Root `tsconfig.json` exists (from Phase 2)
- [ ] Expo TV package created
- [ ] `app.json` configured with correct plugins
- [ ] `package.json` has correct Expo 52 dependencies
- [ ] Metro config set up for monorepo + TV extensions
- [ ] Babel config created
- [ ] `@myapp/shared` dependency added
- [ ] `yarn expotv:prebuild` succeeds

### Android TV

- [ ] Prebuild generates Android project
- [ ] Kotlin version set to 1.9.25
- [ ] App launches on Android TV emulator
- [ ] All screens render without crashes
- [ ] Navigation works correctly
- [ ] Focus management works
- [ ] Scaling utility applied to shared components
- [ ] Core functionality tested

### Apple TV

- [ ] Prebuild generates iOS project
- [ ] tvOS deployment target set to 15.1+
- [ ] Fix script created (if needed)
- [ ] App launches on Apple TV simulator
- [ ] All screens render without crashes
- [ ] Navigation works correctly
- [ ] Focus management works
- [ ] Core functionality tested

### Platform-Specific Implementations

- [ ] All Vega dependencies have replacements identified
- [ ] Platform-specific files created where needed
- [ ] Video player implemented (if applicable)
- [ ] DRM implemented (if applicable)
- [ ] Native modules implemented (if applicable)
- [ ] Platform-specific services implemented

### Testing & Validation

- [ ] Unit tests pass on all platforms
- [ ] Integration tests pass on all platforms
- [ ] Manual testing completed on physical devices
- [ ] Performance acceptable on all platforms
- [ ] No memory leaks detected
- [ ] Error handling works correctly

**Final Validation:**
- [ ] All three platforms build successfully
- [ ] All three platforms run without crashes
- [ ] Core features work on all platforms
- [ ] Code reuse target achieved (70-85%)
- [ ] Documentation updated
- [ ] Team trained on new structure

---

## Post-Migration

- [ ] CI/CD pipelines updated
- [ ] Deployment process documented
- [ ] Monitoring and analytics configured
- [ ] Team onboarding materials created
- [ ] Architecture decision records (ADRs) written
- [ ] Performance benchmarks established
- [ ] Rollback plan documented

---

## Troubleshooting Reference

If you encounter issues, check:

- **Metro resolution errors**: Verify `watchFolders` and `nodeModulesPaths` in metro.config.js
- **Duplicate React versions**: Check `.yarnrc.yml` has `nmHoistingLimits: workspaces`
- **VMRP mapping errors**: Verify babel.config.js and library versions
- **Expo prebuild failures**: Review app.json configuration
- **tvOS deployment errors**: Run fix-tvos-deployment.sh script
- **Focus issues**: Check platform-specific focus implementations
- **Scaling issues**: Verify scaling utility is applied to all hardcoded values

For detailed troubleshooting, see the phase reference documents.
