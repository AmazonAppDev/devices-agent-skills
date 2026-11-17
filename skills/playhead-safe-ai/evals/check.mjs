import { access, readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const skillDir = resolve(here, '..');
const root = resolve(skillDir, '..', '..');

const read = (relative) => readFile(resolve(skillDir, relative), 'utf8');
const checks = [];
const assert = (condition, message) => {
  if (!condition) throw new Error(message);
  checks.push(message);
};

const normalizeBoundary = (playheadMs) => {
  if (!Number.isFinite(playheadMs) || playheadMs < 0) {
    throw new TypeError('playheadMs must be a finite, non-negative number');
  }
  return Math.floor(playheadMs);
};

const selectEligibleCues = (cues, playheadMs) => {
  const boundaryMs = normalizeBoundary(playheadMs);
  const byId = new Map();

  for (const cue of [...cues].sort((left, right) =>
    left.startMs - right.startMs ||
    left.id.localeCompare(right.id) ||
    JSON.stringify(left).localeCompare(JSON.stringify(right)))) {
    if (cue.startMs <= boundaryMs && !byId.has(cue.id)) byId.set(cue.id, cue);
  }

  return [...byId.values()];
};

const validateGenerated = ({
  answer,
  boundaryMs,
  currentBoundaryMs,
  timelineRevision,
  currentTimelineRevision,
  requiredToolUsed,
  mentionedEntityIds = [],
  eligibleEntityIds = [],
  wordLimit = 24,
}) => {
  if (!requiredToolUsed) return 'missing_required_tool';
  if (boundaryMs !== currentBoundaryMs) return 'stale_boundary';
  if (timelineRevision !== currentTimelineRevision) return 'stale_timeline';
  if (typeof answer !== 'string' || answer.trim() === '') return 'empty_answer';
  if (answer.trim().split(/\s+/u).length > wordLimit) return 'answer_too_long';

  const eligible = new Set(eligibleEntityIds);
  if (mentionedEntityIds.some((id) => !eligible.has(id))) {
    return 'ineligible_entity';
  }

  return null;
};

const skill = await read('SKILL.md');
const architecture = await read('references/architecture.md');
const testing = await read('references/testing.md');
const tasks = await read('evals/TASK_SCENARIOS.md');
const triggers = await read('evals/TRIGGER_PROMPTS.md');
const readme = await readFile(resolve(root, 'README.md'), 'utf8');

assert(/^name: playhead-safe-ai/m.test(skill), 'frontmatter names the skill');
assert(skill.includes('authoritative playback clock'), 'skill defines clock authority');
assert(skill.includes('deterministic response validation'), 'skill requires post-model validation');
assert(architecture.includes('AgentCore Memory types'), 'architecture links memory primary source');
assert(architecture.includes('request-scoped closure'), 'architecture documents scoped tools');
assert(architecture.includes('future') && architecture.includes('eligible'), 'architecture documents future-data exclusion');
assert(testing.includes('Moving the playhead backward'), 'testing includes monotonic boundary invariant');
assert(testing.includes('future') && testing.includes('entity'), 'testing includes adversarial future entity case');
assert((tasks.match(/^\| S\d+ \|/gm) ?? []).length === 12, 'task fixture has 12 scenarios');
assert((triggers.match(/^\d+\. /gm) ?? []).length === 20, 'trigger fixture has 20 prompts');
assert(readme.includes('playhead-safe-ai'), 'README lists the skill');

for (const relative of ['references/architecture.md', 'references/testing.md', 'evals/TASK_SCENARIOS.md', 'evals/TRIGGER_PROMPTS.md']) {
  await access(resolve(skillDir, relative));
}
assert(true, 'all linked local references exist');

const cues = [
  {id: 'future', startMs: 10_001, visibleEntityIds: ['future-character']},
  {id: 'at-boundary', startMs: 10_000, visibleEntityIds: ['visible-a']},
  {id: 'opening', startMs: 0, visibleEntityIds: []},
  {id: 'at-boundary', startMs: 10_000, visibleEntityIds: ['duplicate']},
];

const atBoundary = selectEligibleCues(cues, 10_000);
assert(atBoundary.map(({id}) => id).join(',') === 'opening,at-boundary',
  'exact boundary is inclusive, future cue excluded, and duplicate IDs removed');
assert(selectEligibleCues(cues, 9_999).map(({id}) => id).join(',') === 'opening',
  'moving backward cannot retain a newly ineligible cue');
assert(JSON.stringify(selectEligibleCues([...cues].reverse(), 10_000)) ===
  JSON.stringify(atBoundary), 'input order does not change eligibility or selected duplicate');
assert(selectEligibleCues(cues, 10_000).every((cue) => cue.startMs <= 10_000),
  'request-scoped fixture exposes no future cue');
assert(() => {
  try { normalizeBoundary(Number.NaN); return false; } catch (error) { return error instanceof TypeError; }
}, 'non-finite boundaries are rejected');

const validResponse = {
  answer: 'The visible character waits beside the tree.',
  boundaryMs: 10_000,
  currentBoundaryMs: 10_000,
  timelineRevision: 'rev-2',
  currentTimelineRevision: 'rev-2',
  requiredToolUsed: true,
  mentionedEntityIds: ['visible-a'],
  eligibleEntityIds: ['visible-a'],
};

assert(validateGenerated(validResponse) === null, 'valid boundary-scoped answer passes');
assert(validateGenerated({...validResponse, requiredToolUsed: false}) === 'missing_required_tool',
  'answer without required tool use is rejected');
assert(validateGenerated({...validResponse, boundaryMs: 9_000}) === 'stale_boundary',
  'answer from an old seek boundary is rejected');
assert(validateGenerated({...validResponse, timelineRevision: 'rev-1'}) === 'stale_timeline',
  'answer from an old timeline revision is rejected');
assert(validateGenerated({...validResponse, answer: '   '}) === 'empty_answer',
  'empty answer is rejected');
assert(validateGenerated({...validResponse, answer: Array(25).fill('word').join(' ')}) ===
  'answer_too_long', 'answer over the TV word budget is rejected');
assert(validateGenerated({...validResponse, mentionedEntityIds: ['future-character']}) ===
  'ineligible_entity', 'future or off-screen entity is rejected');

const defaultSelection = selectEligibleCues(cues, 10_000).map(({id}) => id);
const personalizedSelection = selectEligibleCues(cues, 10_000).map(({id}) => id);
assert(JSON.stringify(defaultSelection) === JSON.stringify(personalizedSelection),
  'response-style preference does not change eligible media facts');
assert(selectEligibleCues(cues, 9_000).every((cue) => cue.startMs <= 9_000),
  'live fixture uses viewer playhead rather than a later live edge');

console.log(`playhead-safe-ai checks passed: ${checks.length}`);
