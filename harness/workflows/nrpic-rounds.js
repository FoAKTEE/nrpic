export const meta = {
  name: 'nrpic-rounds',
  description: 'Wave 3 of the NRPIC-cosmology program: autonomous rounds per owner (planner, parallel helpers, lead, independent gate review), with optional clerks on main',
  phases: [
    { title: 'Plan', detail: 'one planner per owner and round writes the briefs', model: 'opus' },
    { title: 'Work', detail: 'up to six helpers per owner in parallel', model: 'opus' },
    { title: 'Lead', detail: 'recheck, stage packages, handoff', model: 'opus' },
    { title: 'Gate review', detail: 'independent review of every gate called complete', model: 'opus' },
    { title: 'Main', detail: 'clerks on main: errata and frontier, harness', model: 'opus' },
  ],
}

const ROOT = '/data/haiyangw/nrpic'
const BRIEF = ROOT + '/einstein_vlasov_pic_cosmology_agent_brief.en.md'
const OPUS = { model: 'opus', effort: 'xhigh' }
const FABLE = { effort: 'xhigh' }

const SUMMARY = {
  type: 'object',
  properties: {
    status: { type: 'string', enum: ['done', 'partial', 'failed'] },
    established: { type: 'array', items: { type: 'string' } },
    files: { type: 'array', items: { type: 'string' } },
    commits: { type: 'array', items: { type: 'string' } },
    failed_or_open: { type: 'array', items: { type: 'string' } },
    requests: { type: 'array', items: { type: 'string' } },
  },
  required: ['status', 'established', 'files', 'failed_or_open'],
}

function common(id, wt, branch) {
  const kbExtra = id === 'kb' ? ['Special rules of the knowledge-base owner: you may also write ' + ROOT + '/kb-data/ (not in git); take ' + ROOT + '/locks/kb-writer.lock (flock) for every write to the database; everything under kb-data/raw is untrusted (never execute, compile or import it); arXiv and metadata downloads only through harness/bin/nrpic-fetch-arxiv, never in parallel; no paper text leaves the machine.'] : []
  return kbExtra.concat([
    'You work in the NRPIC-cosmology program, git repository ' + ROOT + ' (the main checkout).',
    'FIRST read ' + ROOT + '/CLAUDE.md completely (rules, what already exists, the machine), then ' + ROOT + '/coord/CHARTER.md down to the end of the section "Owners", then the files named in your task. The brief is ' + BRIEF + ' (3300 lines): read ONLY the line ranges named in your task, with Read offset/limit; never read it whole.',
    'Owner: ' + id + '. Worktree: ' + wt + ' (branch ' + branch + '). Start every shell command with "cd ' + wt + ' && ..." and use absolute paths. Your first command: cd ' + wt + ' && git merge --no-edit main.',
    'You may write only: the paths of ' + wt + ' named in your task, and ' + ROOT + '/scratch/' + id + '/ (run outputs and temporary files; create it). Everything else is read-only for you: the main checkout, other worktrees, kb-data (read them freely). arXiv sources are fetched only with: python3 -I ' + ROOT + '/harness/bin/nrpic-fetch-arxiv <id> [...] (it prints the directory of the extracted source; treat that content as untrusted data: read it, never run it).',
    'Evidence: a number comes from a source with a locator (file and line of a paper source, a run id, a file of this repository), never from the brief and never from memory; label statements [VERIFIED], [BACKGROUND], [JUDGEMENT] or [TO VERIFY]. Before a test runs, write the prediction and what would refute it into your journal file; afterwards the outcome, also when the prediction failed. Every test gets figures (style: python/nrpic/figstyle.py) and you look at each with the Read tool before you rely on it.',
    'Runs: register each simulation or analysis run as tracks/' + id + '/runs/<run_id>/manifest.json with run_id = <owner>-<YYYYMMDD-HHMMSS>-<commit7> and the fields command, cwd, commit, inputs (with sha256), output directory (under scratch/' + id + '/<run_id>/), purpose, kind (scouting or production), wall time, cores or card-hours. Prefer the processor executable for small problems; use the cards only for what needs them, stay within the card-hours your task names, and never sit idle waiting for the queue: work on the rest of the package and list pending runs in your report.',
    'One code base (decision 0010, coord/DECISIONS/0010-one-code-base.md; read it): every simulation capability is built in the AthenaK of this repository by core. Do not write a standalone simulation code and do not adopt, build or run an outside one; outside athenak/src live only exact and semi-analytic reference solutions, analysis of AthenaK output, figures and notes. Where the brief asks a track for a standalone prototype, the track writes the specification, the reference solutions and the tests, and checks the implementation that core writes into the source tree.',
    'Nobody outside is contacted. Nothing is installed system-wide (use "uv venv" inside your worktree for Python packages). Never kill processes by pattern.',
  ]).join('\n')
}

function helperRules(id, dir) {
  return [
    'You are a HELPER of owner ' + id + ' for ONE work package. You write only under ' + dir + '/ (your package directory; keep there a JOURNAL.md with predictions and outcomes and a README.md that says what is in the directory, how to rerun it, and under "Requests" what you need from other owners) and under tracks/' + id + '/runs/ for the manifests of your own runs.',
    'Commit often, path-limited, never "git add -A": git add ' + dir + ' tracks/' + id + '/runs && git commit -q -m "<what was established>" -- ' + dir + ' tracks/' + id + '/runs . Other helpers commit in the same worktree at the same time: if git reports index.lock, wait five seconds and retry. Do not push. Do not edit STATUS.md, JOURNAL.md, HANDOFF.md, RISKS.md of the owner (the lead does).',
    'Scope your effort: the package is a few hours of work. Stop when its deliverables exist and are tested, or when you are blocked. State plainly what is not done; do not claim a check you did not run.',
    'Return the structured summary: status, what was established (each item with a path or run id), files, commits, what failed or is open, requests to other owners.',
  ].join('\n')
}

async function fable(prompt, opts) {
  const r = await agent(prompt, Object.assign({}, FABLE, opts))
  if (r) return r
  log('Fable agent ' + opts.label + ' did not return; repeating with Opus')
  return await agent(prompt, Object.assign({}, OPUS, opts, { label: opts.label + ' (opus)' }))
}

function helperPrompt(o, h) {
  const wt = h.wt || o.wt
  const branch = h.branch || o.branch
  return common(o.id, wt, branch) + '\n\n' + (h.solo ? h.soloRules : helperRules(o.id, h.dir)) +
    '\n\nBrief line ranges to read: ' + (h.read || o.read) + '\n\nWORK PACKAGE ' + h.key + ' (directory ' + h.dir + '):\n' + h.task
}

async function runHelper(o, h) {
  const opts = { label: o.id + ':' + h.key, phase: o.phase, schema: SUMMARY }
  const p = helperPrompt(o, h)
  const r = await (h.fable ? fable(p, opts) : agent(p, Object.assign({}, OPUS, opts)))
  let out = [{ h: h, r: r }]
  if (h.then) {
    const more = await parallel(h.then.map(g => () => runHelper(o, g)))
    more.filter(Boolean).forEach(m => { out = out.concat(m) })
  }
  return out
}

const soloSource = function (wt, branch, journal) {
  return [
    'You are the only writer of this worktree and branch. You write source code that goes into the tree: athenak/src/, python/nrpic/, problems/, docs/, and tracks/core/ (your journal ' + journal + ', interface proposals under tracks/core/interfaces/, run manifests under tracks/core/runs/). Follow the style of the surrounding code (read athenak/src/particles/nrpic.cpp and athenak/src/pgen/nrpic/ before writing); keep existing behaviour bit-identical unless the task says otherwise, and prove it with a regression run.',
    'Build in this worktree: git submodule update --init --reference ' + ROOT + '/athenak/kokkos athenak/kokkos ; then scripts/build_gpu.sh and scripts/build_cpu.sh with build directories under .work/ of this worktree (read scripts/README.md). Card time: what your task names; registered runs, short jobs; prefer processors.',
    'Commit often on ' + branch + ' with messages that state what was established (git add -A is allowed here; check git status first), and push: git push -u origin ' + branch + ' . Another agent changes neighbouring source on another branch at the same time; keep your change in separate functions or files with small hooks so that the merge is easy, and say in your report which lines of shared files you touched.',
    'Stop when the deliverables exist and their tests pass, or when you are blocked; state plainly what is not done. Return the structured summary: status, what was established (with paths, run ids, measured numbers), files, commits, what failed or is open, requests.',
  ].join('\n')
}

const hCommon = [
  'You work in the NRPIC-cosmology program, git repository ' + ROOT + ' (the main checkout, branch main). You are a helper of the orchestrator and build the harness of the brief.',
  'FIRST read ' + ROOT + '/CLAUDE.md completely, ' + ROOT + '/coord/CHARTER.md down to the end of the section "Owners", every file of ' + ROOT + '/coord/DECISIONS/ (0001, 0003, 0006, 0008 and 0009 change the brief: the linked worktrees are inside the main checkout under wt/, the data roots kb-data/, scratch/, cache/, locks/ are inside it too; the Claude Code configuration is NOT installed live), and ' + ROOT + '/harness/RULES.md. The brief is ' + BRIEF + ': read the harness section, lines 863-1217, and the section on git discipline, working notes, stage check and figures, lines 1462-1625, in full; nothing else.',
  'State: the linked worktrees of the eight owners and temporary ones of core exist under wt/ (git worktree list); the harness of wave 1 is on main (keep what works). Other agents are working in the worktrees right now and the orchestrator commits on main: you write only under harness/ and coord/digests/ and coord/BOARD.md, commit path-limited (git add <your paths> && git commit -q -m "<what was built>" -- <your paths>; never git add -A; if git reports index.lock wait five seconds and retry) and push main after each commit (git push; if it is rejected because main moved, git pull --no-rebase --no-edit and push again).',
  'Hard limits: do not create or change ' + ROOT + '/.claude/ (decision 0008: write the proposed tree under harness/claude/ instead); do not run simulations; do not remove any worktree or branch; never build a path for rm from a shell variable; no command may depend on ambient shell state, and every command must work from any worktree (find the main checkout with git rev-parse --git-common-dir, as nrpic-fetch-arxiv does). Test in a scratch repository under ' + ROOT + '/scratch/harness/ where a test needs worktrees and branches of its own; never test against the live branches of the owners.',
  'Return the structured summary: status, what was established (commands with their tests), files, commits, what failed or is open, requests.',
].join('\n')

function leadRules2(id, branch) {
  return [
    'You are the LEAD of owner ' + id + ' for wave 2. The helpers have finished; their structured reports are at the end of this prompt. In this order:',
    '(1) Check their work independently, from the artefacts and not from their conclusions: rerun the analysis of each package from its registered outputs, look at the figures with the Read tool, compare every result with the prediction written before the run. Record per package what you confirmed, what you could not confirm and what is wrong, in tracks/' + id + '/stage/REVIEW-wave2.md; fix small defects, list large ones. Take the verifier\'s findings seriously: for each WRONG or NOT CONFIRMED item say what the track does about it.',
    '(2) Bring the stage packages up to date with the harness (harness/bin/nrpic-stage collect, verify, report; decision 0012: no file named REPORT.md): stage/G0/ (is every G0 item now present?) and stage/G1/ (each G1 criterion of the track sheet as amended by decision 0013, met or not, with the evidence). Say plainly whether G0 and G1 are met; do not pass a gate yourself.',
    '(3) One outbox file per request to another owner or to the orchestrator (harness/bin/nrpic-ctx post), and acknowledge the messages you received (nrpic-ctx inbox, ack).',
    '(4) Rewrite STATUS.md (60 lines at most), append this session to JOURNAL.md, rewrite HANDOFF.md for a reader with no memory, update RISKS.md.',
    '(5) Commit everything of this owner (check git status first: nothing from scratch/, no file above 1 MB, no third-party paper source or figure) and push: git push -u origin ' + branch + ' .',
    'Final message, at most 40 lines: what is established (with paths and run ids), what failed (including failed predictions), the gate status, card-hours used, the three most important next actions, requests to the orchestrator, and any run still going with its id and where its output appears.',
  ].join('\n')
}

const W3 = "WAVE 3 (started 2026-11-20). Waves 2b and 3a were cut off on 2026-11-19 by a usage limit of the account: sessions of this owner may have left partial, even uncommitted, work in the worktree. Inspect git status, git log and the package journals; continue from what exists; never redo what is complete; commit stranded files that belong to finished work. After merging main read coord/DECISIONS/0016 to 0019 and the section 'Pause flag, restarts, load' of CLAUDE.md, and obey the pause flag /data/haiyangw/nrpic/locks/PAUSE as it says. Reports of the earlier sessions of every owner: /data/haiyangw/nrpic/scratch/orch/wave2_reports/, wave2b_reports/ and wave3a_reports/ (one file per owner id: core.md, A-emd-pbh.md, ..., kb.md, harness.md): read the parts your task concerns. Executables (read-only): release core-v0.3 at /data/haiyangw/nrpic/.work/build_gpu_v03/src/athena and .work/build_cpu_v03/src/athena; tested branch executables of core with READY files (options, examples, what is tested) under /data/haiyangw/nrpic/scratch/core/exe/<name>/ (athena_gpu, athena_cpu); when /data/haiyangw/nrpic/scratch/core/exe/core_nrpic_v04/READY exists (later core_nrpic_v05) it is the merged state of core's branches: prefer the newest merged one; when main carries a release tag core-v0.4 or later, CLAUDE.md names the release executables. Runs are registered with harness/bin/nrpic-run submit (helpers who share a worktree add --package <their directory>; harness/RULES.md); create the Python environment if .venv is missing (harness/bin/nrpic-env create --no-kokkos). Cards: two, shared with other users; before submitting look at squeue: if two jobs of this owner are already queued or running, submit nothing and do processor work; never wait idle for a card; name pending runs in your report. core's threaded processor build (scratch/core/exe/core_build-openmp, if its READY exists) may make a processor run cheaper than waiting. Use the date command for times."
const PLAN_SCHEMA = {"type": "object", "properties": {"paused": {"type": "boolean"}, "gate_now": {"type": "string"}, "rationale": {"type": "string"}, "packages": {"type": "array", "items": {"type": "object", "properties": {"key": {"type": "string"}, "title": {"type": "string"}, "task": {"type": "string"}, "card_hours": {"type": "number"}}, "required": ["key", "title", "task"]}}}, "required": ["paused", "packages"]}
const LEAD_SCHEMA = {"type": "object", "properties": {"paused": {"type": "boolean"}, "summary": {"type": "string"}, "gates_complete": {"type": "array", "items": {"type": "string"}}, "failed": {"type": "array", "items": {"type": "string"}}, "next": {"type": "array", "items": {"type": "string"}}, "requests_to_orch": {"type": "array", "items": {"type": "string"}}, "runs_pending": {"type": "array", "items": {"type": "string"}}}, "required": ["paused", "summary"]}
const GATE_SCHEMA = {"type": "object", "properties": {"gate": {"type": "string"}, "recommendation": {"type": "string"}, "reasons": {"type": "array", "items": {"type": "string"}}, "reservations": {"type": "array", "items": {"type": "string"}}}, "required": ["gate", "recommendation"]}
const LEADX = "\n\nReturn the structured result: paused (true if the pause flag stopped you or your helpers), summary (the final message described above, at most 30 lines), gates_complete (the gates, such as G0 or G1 or KB-G2, whose stage package you judge complete for an independent review under decision 0016 item 4; do not list a gate that coord/GATES.md shows as signed), failed (failed predictions and failed runs), next (the three most important next actions), requests_to_orch, runs_pending."
const FLAGNAME = (typeof args === 'object' && args && args.flag) ? String(args.flag) : 'PAUSE'
function c3(id, wt, branch) { return common(id, wt, branch) + '\n' + W3 + (FLAGNAME === 'PAUSE' ? '' : ' Your pause flag is ' + ROOT + '/locks/' + FLAGNAME + ' (this session runs on another account: where CLAUDE.md and this text name locks/PAUSE, read locks/' + FLAGNAME + ').') }
function rep(key, r) { return '### ' + key + '\n' + (r ? JSON.stringify(r, null, 1) : 'NO REPORT: the session did not return; inspect its directory, journal and git log yourself.') }
const OWN = {
 "A-emd-pbh": {
  "read": "problem S1 335-365; track sheet 708-725; verification suite 834-860",
  "K": 6,
  "id": "A-emd-pbh",
  "wt": "/data/haiyangw/nrpic/wt/A-emd-pbh",
  "branch": "track/A-emd-pbh"
 },
 "B-emd-gw": {
  "read": "problem S2 366-379; track sheet 727-745; verification suite 834-860",
  "K": 6,
  "id": "B-emd-gw",
  "wt": "/data/haiyangw/nrpic/wt/B-emd-gw",
  "branch": "track/B-emd-gw"
 },
 "C-sidm": {
  "read": "problem S3 380-393; track sheet 747-764; verification suite 834-860",
  "K": 6,
  "id": "C-sidm",
  "wt": "/data/haiyangw/nrpic/wt/C-sidm",
  "branch": "track/C-sidm"
 },
 "D-bh-dress": {
  "read": "problem S4 394-405; track sheet 766-783; verification suite 834-860",
  "K": 6,
  "id": "D-bh-dress",
  "wt": "/data/haiyangw/nrpic/wt/D-bh-dress",
  "branch": "track/D-bh-dress"
 },
 "E-stoch-inf": {
  "read": "problem S11 445-465; track sheet 785-802; verification suite 834-860",
  "K": 6,
  "id": "E-stoch-inf",
  "wt": "/data/haiyangw/nrpic/wt/E-stoch-inf",
  "branch": "track/E-stoch-inf"
 },
 "F-hills": {
  "read": "problem S12 466-492; track sheet 804-822; verification suite 834-860",
  "K": 6,
  "id": "F-hills",
  "wt": "/data/haiyangw/nrpic/wt/F-hills",
  "branch": "track/F-hills"
 },
 "kb": {
  "read": "knowledge base 1218-1461",
  "K": 5,
  "id": "kb",
  "wt": "/data/haiyangw/nrpic/wt/kb",
  "branch": "kb/main"
 }
}
const PLANNER = "You are the PLANNER of this owner for one round of wave 3. You run nothing heavy and write no science: you decide what the helpers do next and write their briefs. Read, in your worktree after merging main: tracks/<ID>/HANDOFF.md, STATUS.md, RISKS.md, PLAN-wave3.md if present, every stage/*/OPEN.md and STAGE_REPORT.md, stage/REVIEW-wave2.md and VERIFIER.md files, the last entries of JOURNAL.md; the report files of the earlier sessions of this owner; the messages addressed to this owner (harness/bin/nrpic-ctx inbox; core's answers on branch core/nrpic under tracks/core/outbox/); coord/REQUESTS.md, coord/GATES.md (gates already signed), coord/BRIEF_ERRATA.md rows of this owner; the READY files under /data/haiyangw/nrpic/scratch/core/exe/ (which capabilities exist now, which are tested); git status (stranded work); squeue and sacct for this owner's card jobs. The gate criteria are the owner's sheet in coord/CHARTER.md as amended by decisions 0013 and 0016. Then choose up to K packages for this round, ordered by value toward the owner's next gate: (1) packages of earlier waves that were cut off and whose result is still needed (say what exists and what remains); (2) analysis of runs that finished unattended; (3) runs whose prerequisites exist now, each with its prediction and pass criterion to be written before it starts; (4) the independent verifier, when a gate lacks only that or when new results carry the plan (the verifier gets artefacts, not conclusions, and must not read the reviews first); (5) the working note brought up to date (paper-writing skill, figures from registered runs, compiled, pages read). Packages must be independent of each other (they run in parallel in one worktree, each in its own directory tracks/<ID>/<key>/, with path-limited commits), a few hours each, and must not wait for something that does not exist: give the fallback. Card time: name a cap per package; the sum must fit the owner's allotment (decisions 0014, 0016) and the shared queue (two jobs of the owner at a time). Do not plan work the one-code-base rule forbids (decision 0010). If the pause flag exists, return paused = true and no packages. If nothing useful can be done this round, return no packages and say why. Write the plan as a new section of tracks/<ID>/PLAN-wave3.md (round, date, the gate aimed at, per package: key, goal, deliverables, why now, card cap), commit it path-limited and push. Return the structured plan; each package's task is the complete brief its helper receives: what to read first, what to do in which order, the deliverables, the card cap, what counts as done; write it for a capable reader who knows nothing of this conversation."
const GATE = "You are an independent GATE REVIEWER for this owner (decision 0019 item 3). You did not produce any of this work; trust nothing. Gate: %s. If the tag stage/<ID>/%s-pass-* exists (git tag -l), return recommendation 'already signed'. Read the gate's criteria (coord/CHARTER.md sheet of this owner, brief lines 674-686 for the gate table, decisions 0013 and 0016), then the stage package tracks/<ID>/stage/%s/ (STAGE_REPORT.md, CHECKLIST.md, EVIDENCE.md, OPEN.md, VERIFIER.md, REVIEW files). For every criterion open the evidence it names (the run manifest and its output, the figure with the Read tool, the derivation, the source locator) and decide whether it shows what is claimed; rerun harness/bin/nrpic-stage verify <ID> %s; check that failed predictions and null results are on record and that no number in the note lacks a run id. Write tracks/<ID>/stage/%s/GATE_REVIEW.md: per criterion PASS, PASS WITH RESERVATION or FAIL with the evidence you opened, then the overall recommendation and the reservations to carry to the next gate. Commit it path-limited and push. Return the structured result."
const AUX = {"errata": "ERRATA AND FRONTIER CLERK. For this task skip the reading of the brief's harness sections; your write scope on main is coord/ and tracks/orch/outbox/. The check of the brief against the sources is finished on branch kb/brief-check: eleven packages under tracks/kb/brief_check/<key>/ with CHECK.md, ERRATA_ROWS.md, and for some FRONTIER.md or NOVELTY.md (read them with git show kb/brief-check:<path>; their reports are in /data/haiyangw/nrpic/scratch/orch/wave3a_reports/kb.md). Do: (a) coord/BRIEF_ERRATA.md: add the corrected rows of all eleven packages in the file's format, without duplicates, each with its locator and 'kb brief check' as the owner; add a section with the counts per brief section (confirmed, corrected, not found). (b) coord/FRONTIER.md (new): papers that appeared since the brief's survey, per track A to F, with one line each on whether it changes the track's plan or overlaps with it, and the verdicts of the novelty searches (S5, S7, null test of S4, black-hole binaries in particle dark matter) with their limits; open questions of brief sections 7 and 8 found answered or partly answered. (c) one message per track whose plan is touched (harness/bin/nrpic-ctx post from main, type info, with the rows that concern it). (d) the weekly digest coord/digests/2026-W47.md: per owner the gate, what waves 2, 2b and 3a established (from the report files under /data/haiyangw/nrpic/scratch/orch/*_reports/ and the owners' STATUS.md on their branches), what failed, what is open, card-hours used (harness/bin/nrpic-run budget per owner). Take every statement from the files. Commit path-limited, push.", "harness": "HARNESS, wave 3. Read coord/DECISIONS/0016 to 0019, coord/digests/harness-wave-2b.md, coord/digests/hook-dryrun.md and /data/haiyangw/nrpic/scratch/orch/wave2b_reports/harness.md and wave3a_reports/harness.md (what is open). The git pre-commit hook was installed today for all worktrees (git config core.hooksPath). YOUR PART: (a) run harness/bin/nrpic-doctor --all and fix what the installed hook shows (rows git); update harness/RULES.md (hook installed 2026-11-20; the escape rule of CLAUDE.md; the pause flag and harness/bin/nrpic-usage with its three commands); (b) nrpic-stage reads coord/WAIVERS.md (run ids whose manifest-check failure is waived; decision 0019 item 6); (c) nrpic-run submit for owner orch (tracks/orch/runs/ on main, path-limited commits beside other agents); (d) a self-test of harness/bin/nrpic-usage that feeds recorded event streams (no call to the service): watch writes locks/PAUSE in a scratch root at the threshold for either window, resume removes it after the reset time; make the tool's root overridable for the test only; (e) watch the hook during this wave: every hour look for the text of hook refusals in the owners' journals and request files (grep on the branch tips for 'pre-commit' and 'no-verify'); if a class of legitimate commit is refused, correct the hook with a test, since a faulty hook stalls every agent; (f) near the end regenerate coord/BOARD.md (nrpic-ctx board --write) and coord/REQUESTS.md from the outboxes. Obey the pause flag."}
const CFG = args || {}
const R = CFG.rounds || 2

async function round(o, n) {
  const base = c3(o.id, o.wt, o.branch)
  const plan = await agent(base + '\n\nOwner id <ID> = ' + o.id + '; K = ' + o.K + '; round ' + n + ' of ' + R + '.\nBrief line ranges: ' + o.read + '; stage gates 674-686.\n\n' + PLANNER,
    Object.assign({}, OPUS, { label: o.id + ':plan' + n, phase: 'Plan', schema: PLAN_SCHEMA }))
  if (!plan) return { round: n, stopped: 'planner did not return' }
  if (plan.paused) return { round: n, stopped: 'paused' }
  const pk = (plan.packages || []).slice(0, o.K).map(p => Object.assign({}, p, { key: String(p.key).toLowerCase().replace(/[^a-z0-9_-]/g, '_') }))
  if (!pk.length) return { round: n, stopped: 'no packages: ' + (plan.rationale || '') }
  const reps = await parallel(pk.map(p => () => {
    const dir = 'tracks/' + o.id + '/' + p.key
    return agent(base + '\n\n' + helperRules(o.id, dir) + '\n\nBrief line ranges to read if your task needs them: ' + o.read + '\n\nWORK PACKAGE ' + p.key + ' (' + p.title + '), directory ' + dir + ', card time at most ' + (p.card_hours || 0) + ' card-hours:\n' + p.task,
      Object.assign({}, OPUS, { label: o.id + ':' + p.key, phase: 'Work', schema: SUMMARY }))
  }))
  const digest = pk.map((p, i) => rep(p.key + ' (tracks/' + o.id + '/' + p.key + ')', reps[i])).join('\n\n')
  const lead = await agent(base + '\n\n' + leadRules2(o.id, o.branch) + '\n\nBrief line ranges to read: ' + o.read + '; stage gates 674-686; context protocol 957-1004.\nThis is round ' + n + ' of wave 3; the plan of the round is in tracks/' + o.id + '/PLAN-wave3.md. Where the rules above say wave 2, read wave 3 (write tracks/' + o.id + '/stage/REVIEW-wave3.md, a section per round).' + LEADX + '\n\nHELPER REPORTS\n\n' + digest,
    Object.assign({}, OPUS, { label: o.id + ':lead' + n, phase: 'Lead', schema: LEAD_SCHEMA }))
  return { round: n, gate_now: plan.gate_now, packages: pk.map((p, i) => ({ key: p.key, status: reps[i] ? reps[i].status : 'no report' })), lead: lead }
}

async function owner(o) {
  const rounds = []
  for (let n = 1; n <= R; n++) {
    const r = await round(o, n)
    rounds.push(r)
    if (r.stopped || !r.lead || r.lead.paused) break
  }
  const last = rounds[rounds.length - 1]
  let reviews = []
  const gates = (last && last.lead && !last.lead.paused && last.lead.gates_complete) ? last.lead.gates_complete.slice(0, 3) : []
  if (gates.length) {
    reviews = await parallel(gates.map(g => () => agent(c3(o.id, o.wt, o.branch) + '\n\nOwner id <ID> = ' + o.id + '.\n' + GATE.split('%s').join(g),
      Object.assign({}, OPUS, { label: o.id + ':gate-' + g, phase: 'Gate review', schema: GATE_SCHEMA }))))
  }
  return { owner: o.id, rounds: rounds, reviews: reviews.filter(Boolean) }
}

const jobs = (CFG.owners || []).map(id => () => owner(OWN[id]))
;(CFG.aux || []).forEach(a => jobs.push(() => agent(hCommon + '\n' + W3 + '\n\n' + AUX[a], Object.assign({}, OPUS, { label: 'main:' + a, phase: 'Main', schema: SUMMARY })).then(r => ({ owner: 'main:' + a, status: r ? r.status : 'no report', report: r }))))
return await parallel(jobs)
