#!/usr/bin/env node
/**
 * audit.js — static helper for the rn-tv-ui-best-practices skill.
 *
 * Runs grep-style checks against the rules in the reference files.
 * **This is a helper, not a complete review.** It only catches statically
 * detectable patterns. Many of the rules in the reference files require
 * judgement, hardware, or human review — those will not be caught here
 * regardless of how clean the audit output is. Treat findings as candidates
 * to inspect; treat a clean run as "no obvious lint hits", not "the app is
 * correct."
 *
 * Sections:
 *   focus       — navigation-and-focus.md  (5 checks)
 *   input       — input-handling.md        (4 checks)
 *   layout      — layout-patterns.md       (4 checks)
 *   typography  — typography-and-color.md  (9 checks)
 *
 * Usage:
 *   node audit.js [path ...]                  # all sections, default path: src
 *   node audit.js src --only typography
 *   node audit.js src --only focus,input
 *   node audit.js src --skip typography
 *   node audit.js src --min-font-size 22      # raise the typography floor
 *
 * Output:
 *   Findings grouped by section, then by check, with file:line and snippet.
 *   Exits 0 if no findings, 1 if any findings — usable as a CI signal.
 *
 * Limitations (read these before reporting findings):
 *   - Regex-based, not AST-based. False positives exist: comments, strings,
 *     non-RN code with similar prop names, debug-only styles. Read each
 *     match in context.
 *   - Won't see tokens defined in JSON / theme files referenced by name.
 *   - Multi-line JSX with props spread far below the opening tag may slip
 *     past element-scoped checks.
 *   - Runtime detection (used by focus and input checks) reads package.json
 *     once at the project root determined from the first scan path's parent
 *     walk. Monorepos with per-package runtimes will only see the root.
 */

const fs = require("node:fs");
const path = require("node:path");

// ---- args ----

const args = process.argv.slice(2);
const roots = [];
let only = null;
let skip = null;
let minFontSize = 20;

for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === "--only") only = (args[++i] || "").split(",").map((s) => s.trim()).filter(Boolean);
  else if (a === "--skip") skip = (args[++i] || "").split(",").map((s) => s.trim()).filter(Boolean);
  else if (a === "--min-font-size") {
    minFontSize = parseInt(args[++i], 10);
    if (Number.isNaN(minFontSize)) {
      console.error("--min-font-size requires an integer");
      process.exit(2);
    }
  } else if (a === "--help" || a === "-h") {
    console.log(
      "Usage: node audit.js [path ...] [--only sections] [--skip sections] [--min-font-size N]\n" +
        "Sections: focus, input, layout, typography"
    );
    process.exit(0);
  } else {
    roots.push(a);
  }
}
if (roots.length === 0) roots.push("src");

const ALL_SECTIONS = ["focus", "input", "layout", "typography"];
const sections = ALL_SECTIONS.filter((s) => {
  if (only && !only.includes(s)) return false;
  if (skip && skip.includes(s)) return false;
  return true;
});

// ---- file walking ----

const SOURCE_EXT = new Set([".ts", ".tsx", ".js", ".jsx"]);
const SKIP_DIRS = new Set([
  "node_modules",
  ".git",
  "ios",
  "android",
  "build",
  "dist",
  ".expo",
  ".next",
  "coverage",
  "__tests__",
  "__mocks__",
]);

function* walk(dir) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (SKIP_DIRS.has(entry.name)) continue;
      yield* walk(full);
    } else if (SOURCE_EXT.has(path.extname(entry.name))) {
      yield full;
    }
  }
}

// ---- runtime detection ----

function findPackageJson(start) {
  let dir = path.resolve(start);
  while (true) {
    const candidate = path.join(dir, "package.json");
    if (fs.existsSync(candidate)) return candidate;
    const parent = path.dirname(dir);
    if (parent === dir) return null;
    dir = parent;
  }
}

let projectRuntime = "unknown"; // 'tvos' | 'vega' | 'stock' | 'unknown'
const pkgPath = findPackageJson(roots[0]);
if (pkgPath) {
  try {
    const pkg = JSON.parse(fs.readFileSync(pkgPath, "utf8"));
    const deps = { ...pkg.dependencies, ...pkg.devDependencies };
    const rn = deps["react-native"] || "";
    if (/react-native-tvos/.test(rn)) projectRuntime = "tvos";
    else if (deps["@amazon-devices/react-native-kepler"]) projectRuntime = "vega";
    else if (deps["react-native"]) projectRuntime = "stock";
  } catch {
    // leave as 'unknown'
  }
}

// ---- WCAG helpers (typography contrast check) ----

function parseHex(hex) {
  const m = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(hex);
  if (!m) return null;
  const h = m[1];
  if (h.length === 3) {
    return [
      parseInt(h[0] + h[0], 16),
      parseInt(h[1] + h[1], 16),
      parseInt(h[2] + h[2], 16),
    ];
  }
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}

function relativeLuminance([r, g, b]) {
  const channel = (c) => {
    const v = c / 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  };
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

function contrastRatio(hexA, hexB) {
  const a = parseHex(hexA);
  const b = parseHex(hexB);
  if (!a || !b) return null;
  const lA = relativeLuminance(a);
  const lB = relativeLuminance(b);
  const [light, dark] = lA > lB ? [lA, lB] : [lB, lA];
  return (light + 0.05) / (dark + 0.05);
}

// ---- findings ----

const findings = {
  // focus
  modalWithoutTrap: [],
  multiplePreferredFocus: [],
  ungatedNextFocus: [],
  pressableOnFocusOnStockRn: [],
  unsupportedTouchableFocus: [],

  // input
  textInputNoKeyboardType: [],
  passwordWithoutSecureEntry: [],
  searchWithoutSubmit: [],
  vegaUseTVEventHandlerWrongImport: [],

  // layout
  scrollViewWithMap: [],
  flashListBadProps: [],
  inlineRenderItem: [],
  hardcodedResolution: [],

  // typography
  fontSizeTooSmall: [],
  fontWeightTooThin: [],
  pureWhiteOnPureBlack: [],
  uppercaseTextTransform: [],
  textWithoutNumberOfLines: [],
  textShadowRadiusTooLarge: [],
  lineHeightImplausible: [],
  negativeLetterSpacingSmallFont: [],
  contrastTooLow: [],
};

const FLASHLIST_BAD_PROPS = [
  "windowSize",
  "getItemLayout",
  "initialNumToRender",
  "maxToRenderPerBatch",
  "updateCellsBatchingPeriod",
];

const TV_RESOLUTIONS = {
  width: [1280, 1920, 3840],
  height: [720, 1080, 2160],
};

const PASSWORD_PLACEHOLDER =
  /placeholder\s*=\s*\{?["'`].*\b([Pp]assword|PIN|[Cc]ode|[Pp]asscode)\b/;
const SEARCH_PLACEHOLDER = /placeholder\s*=\s*\{?["'`].*\b[Ss]earch/;

const PURE_WHITE_RE = /['"`](#fff|#ffffff)['"`]/i;
const PURE_BLACK_RE = /['"`](#000|#000000)['"`]/i;

const CONTRAST_THRESHOLD = 4.5;

// ---- scan ----

const isFocus = sections.includes("focus");
const isInput = sections.includes("input");
const isLayout = sections.includes("layout");
const isTypo = sections.includes("typography");

for (const root of roots) {
  if (!fs.existsSync(root)) {
    console.error(`Path not found: ${root}`);
    continue;
  }

  for (const file of walk(root)) {
    let content;
    try {
      content = fs.readFileSync(file, "utf8");
    } catch {
      continue;
    }
    const lines = content.split("\n");

    // Per-file state.
    let preferredFocusCount = 0;
    const preferredFocusLines = [];
    const fileImportsFork =
      /from\s+['"]react-native-tvos['"]/.test(content) ||
      /from\s+['"]@amazon-devices\/react-native-kepler['"]/.test(content);

    let hasPureWhite = false;
    let hasPureBlack = false;
    let firstWhiteLine = null;
    let firstBlackLine = null;

    // Input check 4: Vega useTVEventHandler import.
    if (isInput && projectRuntime === "vega") {
      const importRe =
        /import\s*\{[^}]*\b(useTVEventHandler|TVEventHandler)\b[^}]*\}\s*from\s*['"]react-native['"]/g;
      let m;
      while ((m = importRe.exec(content)) !== null) {
        const lineNo = content.slice(0, m.index).split("\n").length;
        findings.vegaUseTVEventHandlerWrongImport.push({
          file,
          line: lineNo,
          snippet: lines[lineNo - 1].trim(),
        });
      }
    }

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const lineNo = i + 1;

      // ---------- FOCUS ----------
      if (isFocus) {
        if (/<Modal\b/.test(line)) {
          const window = lines.slice(i, Math.min(i + 12, lines.length)).join("\n");
          if (!/trapFocus/.test(window)) {
            findings.modalWithoutTrap.push({ file, line: lineNo, snippet: line.trim() });
          }
        }

        if (/\bhasTVPreferredFocus\b/.test(line)) {
          preferredFocusCount++;
          preferredFocusLines.push(lineNo);
        }

        if (/\bnextFocus(Up|Down|Left|Right|Forward)\b/.test(line)) {
          const fileGated = /Platform\.OS\s*===\s*['"]android['"]/.test(content);
          if (!fileGated) {
            findings.ungatedNextFocus.push({ file, line: lineNo, snippet: line.trim() });
          }
        }

        if (
          projectRuntime === "stock" &&
          !fileImportsFork &&
          /\bon(Focus|Blur)\s*=/.test(line)
        ) {
          const lookback = lines.slice(Math.max(0, i - 5), i + 1).join("\n");
          const inSupported =
            /<(Pressable|TouchableOpacity|TouchableHighlight)\b/.test(lookback);
          const inUnsupported =
            /<Touchable(NativeFeedback|WithoutFeedback)\b/.test(lookback);
          if (inSupported && !inUnsupported) {
            findings.pressableOnFocusOnStockRn.push({
              file,
              line: lineNo,
              snippet: line.trim(),
            });
          }
        }

        if (/<Touchable(NativeFeedback|WithoutFeedback)\b/.test(line)) {
          const window = lines.slice(i, Math.min(i + 6, lines.length)).join("\n");
          if (/\bon(Focus|Blur)\s*=/.test(window)) {
            findings.unsupportedTouchableFocus.push({
              file,
              line: lineNo,
              snippet: line.trim(),
            });
          }
        }
      }

      // ---------- INPUT ----------
      if (isInput && /<TextInput\b/.test(line)) {
        let element = line;
        const closesOnSameLine = /\/>|>(?!.*<TextInput)/.test(line);
        if (!closesOnSameLine) {
          for (let j = i + 1; j < Math.min(i + 12, lines.length); j++) {
            element += "\n" + lines[j];
            if (/\/>/.test(lines[j]) || /^\s*>/.test(lines[j])) break;
          }
        }

        if (!/\bkeyboardType\s*=/.test(element)) {
          findings.textInputNoKeyboardType.push({
            file,
            line: lineNo,
            snippet: line.trim(),
          });
        }
        if (PASSWORD_PLACEHOLDER.test(element) && !/\bsecureTextEntry\b/.test(element)) {
          findings.passwordWithoutSecureEntry.push({
            file,
            line: lineNo,
            snippet: line.trim(),
          });
        }
        if (
          SEARCH_PLACEHOLDER.test(element) &&
          !/\bonSubmitEditing\s*=/.test(element) &&
          !/\breturnKeyType\s*=/.test(element)
        ) {
          findings.searchWithoutSubmit.push({
            file,
            line: lineNo,
            snippet: line.trim(),
          });
        }
      }

      // ---------- LAYOUT ----------
      if (isLayout) {
        if (/<ScrollView\b/.test(line)) {
          let body = line;
          for (let j = i + 1; j < Math.min(i + 30, lines.length); j++) {
            body += "\n" + lines[j];
            if (/<\/ScrollView>/.test(lines[j])) break;
          }
          if (/\.map\s*\(/.test(body)) {
            findings.scrollViewWithMap.push({
              file,
              line: lineNo,
              snippet: line.trim(),
            });
          }
        }

        if (/<FlashList\b/.test(line)) {
          let element = line;
          for (let j = i + 1; j < Math.min(i + 20, lines.length); j++) {
            element += "\n" + lines[j];
            if (/\/>/.test(lines[j]) || /^\s*>/.test(lines[j])) break;
          }
          for (const prop of FLASHLIST_BAD_PROPS) {
            const re = new RegExp(`\\b${prop}\\s*=`);
            if (re.test(element)) {
              findings.flashListBadProps.push({
                file,
                line: lineNo,
                prop,
                snippet: line.trim(),
              });
            }
          }
        }

        if (/\brenderItem\s*=\s*\{\s*\(/.test(line)) {
          const lookback = lines.slice(Math.max(0, i - 10), i + 1).join("\n");
          if (/<(FlatList|FlashList|LegendList)\b/.test(lookback)) {
            findings.inlineRenderItem.push({
              file,
              line: lineNo,
              snippet: line.trim(),
            });
          }
        }

        const widthMatch = /\bwidth\s*:\s*(\d+)\b/.exec(line);
        if (widthMatch && TV_RESOLUTIONS.width.includes(parseInt(widthMatch[1], 10))) {
          findings.hardcodedResolution.push({
            file,
            line: lineNo,
            dimension: "width",
            value: parseInt(widthMatch[1], 10),
            snippet: line.trim(),
          });
        }
        const heightMatch = /\bheight\s*:\s*(\d+)\b/.exec(line);
        if (heightMatch && TV_RESOLUTIONS.height.includes(parseInt(heightMatch[1], 10))) {
          findings.hardcodedResolution.push({
            file,
            line: lineNo,
            dimension: "height",
            value: parseInt(heightMatch[1], 10),
            snippet: line.trim(),
          });
        }
      }

      // ---------- TYPOGRAPHY (per-line) ----------
      if (isTypo) {
        const fsMatch = /\bfontSize\s*:\s*(\d+)\b/.exec(line);
        if (fsMatch) {
          const size = parseInt(fsMatch[1], 10);
          if (size < minFontSize) {
            findings.fontSizeTooSmall.push({
              file,
              line: lineNo,
              size,
              snippet: line.trim(),
            });
          }
        }

        const fwMatch = /\bfontWeight\s*:\s*['"]?(100|200)['"]?/.exec(line);
        if (fwMatch) {
          findings.fontWeightTooThin.push({
            file,
            line: lineNo,
            weight: fwMatch[1],
            snippet: line.trim(),
          });
        }

        if (!hasPureWhite && PURE_WHITE_RE.test(line)) {
          hasPureWhite = true;
          firstWhiteLine = lineNo;
        }
        if (!hasPureBlack && PURE_BLACK_RE.test(line)) {
          hasPureBlack = true;
          firstBlackLine = lineNo;
        }

        if (/\btextTransform\s*:\s*['"]uppercase['"]/.test(line)) {
          findings.uppercaseTextTransform.push({
            file,
            line: lineNo,
            snippet: line.trim(),
          });
        }

        const textOpen = /<Text(\s[^>]*)?>/.exec(line);
        if (textOpen && !/numberOfLines/.test(line)) {
          findings.textWithoutNumberOfLines.push({
            file,
            line: lineNo,
            snippet: line.trim(),
          });
        }

        const tsrMatch = /\btextShadowRadius\s*:\s*(\d+(?:\.\d+)?)/.exec(line);
        if (tsrMatch) {
          const radius = parseFloat(tsrMatch[1]);
          if (radius > 3) {
            findings.textShadowRadiusTooLarge.push({
              file,
              line: lineNo,
              radius,
              snippet: line.trim(),
            });
          }
        }
      }
    }

    // Per-file emits (after the line loop).
    if (isFocus && preferredFocusCount > 1) {
      findings.multiplePreferredFocus.push({
        file,
        count: preferredFocusCount,
        lines: preferredFocusLines,
      });
    }

    if (isTypo && hasPureWhite && hasPureBlack) {
      findings.pureWhiteOnPureBlack.push({
        file,
        whiteLine: firstWhiteLine,
        blackLine: firstBlackLine,
      });
    }

    // Typography object-scan checks (lineHeight, letterSpacing, contrast).
    if (isTypo) {
      const objectRe = /\{([^{}]*)\}/g;
      let m;
      while ((m = objectRe.exec(content)) !== null) {
        const body = m[1];
        const objLine = content.slice(0, m.index).split("\n").length;

        const fsMatch = /\bfontSize\s*:\s*(\d+(?:\.\d+)?)/.exec(body);
        const fontSize = fsMatch ? parseFloat(fsMatch[1]) : null;

        if (fontSize !== null) {
          const lhMatch = /\blineHeight\s*:\s*(\d+(?:\.\d+)?)/.exec(body);
          if (lhMatch) {
            const lineHeight = parseFloat(lhMatch[1]);
            const ratio = lineHeight / fontSize;
            if (ratio < 0.9 || ratio > 2) {
              findings.lineHeightImplausible.push({
                file,
                line: objLine,
                fontSize,
                lineHeight,
                ratio: ratio.toFixed(2),
              });
            }
          }
          const lsMatch = /\bletterSpacing\s*:\s*(-\d+(?:\.\d+)?)/.exec(body);
          if (lsMatch && fontSize < 40) {
            findings.negativeLetterSpacingSmallFont.push({
              file,
              line: objLine,
              fontSize,
              letterSpacing: parseFloat(lsMatch[1]),
            });
          }
        }

        const colorMatch = /\bcolor\s*:\s*['"`](#[0-9a-fA-F]{3,8})['"`]/.exec(body);
        const bgMatch = /\bbackgroundColor\s*:\s*['"`](#[0-9a-fA-F]{3,8})['"`]/.exec(body);
        if (colorMatch && bgMatch) {
          const ratio = contrastRatio(colorMatch[1], bgMatch[1]);
          if (ratio !== null && ratio < CONTRAST_THRESHOLD) {
            findings.contrastTooLow.push({
              file,
              line: objLine,
              color: colorMatch[1],
              backgroundColor: bgMatch[1],
              ratio: ratio.toFixed(2),
            });
          }
        }
      }
    }
  }
}

// ---- output ----

let total = 0;

function header(title, count) {
  total += count;
  const prefix = count > 0 ? "✗" : "✓";
  console.log(`\n${prefix} ${title} (${count})`);
  console.log("─".repeat(60));
}

function emitList(list, fmt) {
  if (list.length === 0) {
    console.log("  no findings");
    return;
  }
  for (const f of list) console.log(fmt(f));
}

console.log(`Sections: ${sections.join(", ")}`);
console.log(`Detected runtime: ${projectRuntime}`);

if (isFocus) {
  console.log("\n══════════ FOCUS ══════════");

  header("<Modal> without trapFocus nearby (review)", findings.modalWithoutTrap.length);
  if (findings.modalWithoutTrap.length > 0) {
    console.log("  (modals wrapped from outside or via custom abstraction may be false positives)");
  }
  emitList(findings.modalWithoutTrap, (f) => `  ${f.file}:${f.line}\n    ${f.snippet}`);

  header("Multiple hasTVPreferredFocus in the same file", findings.multiplePreferredFocus.length);
  emitList(findings.multiplePreferredFocus, (f) =>
    `  ${f.file}  (${f.count} occurrences at lines ${f.lines.join(", ")})`
  );

  header(
    "nextFocus* without Platform.OS === 'android' gate (stock RN only)",
    findings.ungatedNextFocus.length
  );
  if (findings.ungatedNextFocus.length > 0 && projectRuntime !== "stock") {
    console.log(`  (project runtime is ${projectRuntime} — gating is not required; ignore unless stock RN)`);
  }
  emitList(findings.ungatedNextFocus, (f) => `  ${f.file}:${f.line}\n    ${f.snippet}`);

  header(
    "Pressable.onFocus / onBlur on stock React Native (handler never fires)",
    findings.pressableOnFocusOnStockRn.length
  );
  if (projectRuntime !== "stock") {
    console.log("  not applicable — project is on", projectRuntime);
  } else {
    emitList(findings.pressableOnFocusOnStockRn, (f) => `  ${f.file}:${f.line}\n    ${f.snippet}`);
  }

  header(
    "TouchableNativeFeedback / TouchableWithoutFeedback with onFocus / onBlur",
    findings.unsupportedTouchableFocus.length
  );
  if (findings.unsupportedTouchableFocus.length > 0) {
    console.log("  (these two variants do not fire focus events; use Pressable / TouchableOpacity / TouchableHighlight)");
  }
  emitList(findings.unsupportedTouchableFocus, (f) => `  ${f.file}:${f.line}\n    ${f.snippet}`);
}

if (isInput) {
  console.log("\n══════════ INPUT ══════════");

  header("<TextInput> without keyboardType", findings.textInputNoKeyboardType.length);
  emitList(findings.textInputNoKeyboardType, (f) => `  ${f.file}:${f.line}\n    ${f.snippet}`);

  header("Password-shaped input without secureTextEntry", findings.passwordWithoutSecureEntry.length);
  emitList(findings.passwordWithoutSecureEntry, (f) => `  ${f.file}:${f.line}\n    ${f.snippet}`);

  header(
    "Search-shaped input without onSubmitEditing / returnKeyType",
    findings.searchWithoutSubmit.length
  );
  emitList(findings.searchWithoutSubmit, (f) => `  ${f.file}:${f.line}\n    ${f.snippet}`);

  header(
    "Vega: useTVEventHandler imported from 'react-native' (wrong package)",
    findings.vegaUseTVEventHandlerWrongImport.length
  );
  if (projectRuntime !== "vega") {
    console.log("  not applicable — project is not on Vega");
  } else {
    if (findings.vegaUseTVEventHandlerWrongImport.length > 0) {
      console.log("  (import from '@amazon-devices/react-native-kepler' instead)");
    }
    emitList(findings.vegaUseTVEventHandlerWrongImport, (f) =>
      `  ${f.file}:${f.line}\n    ${f.snippet}`
    );
  }
}

if (isLayout) {
  console.log("\n══════════ LAYOUT ══════════");

  header("<ScrollView> containing .map(...) — virtualise instead", findings.scrollViewWithMap.length);
  emitList(findings.scrollViewWithMap, (f) => `  ${f.file}:${f.line}\n    ${f.snippet}`);

  header(
    "FlashList with FlatList-only tuning props (no-op on FlashList)",
    findings.flashListBadProps.length
  );
  emitList(findings.flashListBadProps, (f) =>
    `  ${f.file}:${f.line}  ${f.prop}\n    ${f.snippet}`
  );

  header(
    "Inline renderItem={(...) => ...} on FlatList / FlashList / LegendList",
    findings.inlineRenderItem.length
  );
  if (findings.inlineRenderItem.length > 0) {
    console.log("  (define outside the component or wrap in useCallback)");
  }
  emitList(findings.inlineRenderItem, (f) => `  ${f.file}:${f.line}\n    ${f.snippet}`);

  header(
    "Hard-coded TV resolution dimensions in style props",
    findings.hardcodedResolution.length
  );
  emitList(findings.hardcodedResolution, (f) =>
    `  ${f.file}:${f.line}  ${f.dimension}: ${f.value}\n    ${f.snippet}`
  );
}

if (isTypo) {
  console.log("\n══════════ TYPOGRAPHY ══════════");

  header(`Font sizes below ${minFontSize}`, findings.fontSizeTooSmall.length);
  emitList(findings.fontSizeTooSmall, (f) =>
    `  ${f.file}:${f.line}  fontSize: ${f.size}\n    ${f.snippet}`
  );

  header("Ultra-thin font weights ('100' / '200')", findings.fontWeightTooThin.length);
  emitList(findings.fontWeightTooThin, (f) =>
    `  ${f.file}:${f.line}  fontWeight: '${f.weight}'\n    ${f.snippet}`
  );

  header(
    "Files containing both pure #FFFFFF and pure #000000",
    findings.pureWhiteOnPureBlack.length
  );
  if (findings.pureWhiteOnPureBlack.length > 0) {
    console.log("  (presence of both extremes — confirm they're not paired as text/background)");
  }
  emitList(findings.pureWhiteOnPureBlack, (f) =>
    `  ${f.file}  white@${f.whiteLine}  black@${f.blackLine}`
  );

  header("textTransform: 'uppercase'", findings.uppercaseTextTransform.length);
  emitList(findings.uppercaseTextTransform, (f) => `  ${f.file}:${f.line}\n    ${f.snippet}`);

  header(
    "<Text> without numberOfLines (review for tile-title usage)",
    findings.textWithoutNumberOfLines.length
  );
  if (findings.textWithoutNumberOfLines.length > 0) {
    console.log("  (button labels and short fixed strings legitimately don't need numberOfLines)");
  }
  emitList(findings.textWithoutNumberOfLines, (f) => `  ${f.file}:${f.line}\n    ${f.snippet}`);

  header("textShadowRadius greater than 3", findings.textShadowRadiusTooLarge.length);
  emitList(findings.textShadowRadiusTooLarge, (f) =>
    `  ${f.file}:${f.line}  textShadowRadius: ${f.radius}\n    ${f.snippet}`
  );

  header(
    "lineHeight implausible vs fontSize (outside 0.9×–2× range)",
    findings.lineHeightImplausible.length
  );
  emitList(findings.lineHeightImplausible, (f) =>
    `  ${f.file}:${f.line}  fontSize: ${f.fontSize}  lineHeight: ${f.lineHeight}  (ratio: ${f.ratio}×)`
  );

  header(
    "Negative letterSpacing on fontSize < 40 (only tighten on display sizes)",
    findings.negativeLetterSpacingSmallFont.length
  );
  emitList(findings.negativeLetterSpacingSmallFont, (f) =>
    `  ${f.file}:${f.line}  fontSize: ${f.fontSize}  letterSpacing: ${f.letterSpacing}`
  );

  header(
    `WCAG contrast below ${CONTRAST_THRESHOLD}:1 (same-object pairs)`,
    findings.contrastTooLow.length
  );
  if (findings.contrastTooLow.length > 0) {
    console.log("  (only same-object color/backgroundColor pairs; inherited / cross-component pairs need hardware spot-check)");
  }
  emitList(findings.contrastTooLow, (f) =>
    `  ${f.file}:${f.line}  color: ${f.color}  backgroundColor: ${f.backgroundColor}  (ratio: ${f.ratio}:1)`
  );
}

console.log(`\nTotal: ${total} finding(s) across ${roots.join(", ")}`);
console.log(
  "This audit only catches statically detectable patterns. Many rules in the reference files require judgement, hardware, or human review — a clean audit run is not the same as a correct app."
);
process.exit(total > 0 ? 1 : 0);
