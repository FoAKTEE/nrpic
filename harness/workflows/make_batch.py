#!/usr/bin/env python3
"""make_batch.py <spec.json> <out.js>: build a batch workflow (decision 0020) from a spec.
spec = {"name": "...", "note": "...", "items": [
  {"type": "pkg", "owner": ID, "key": K},            package brief from scratch/orch/wave3_plans/<ID>.json
  {"type": "lead", "owner": ID},                      lead session of an owner
  {"type": "gate", "owner": ID, "gate": "G1"},        independent gate review
  {"type": "core-src", "key": K},                     core source package continued
  {"type": "core-merge", "version": "v0.5", "task": "..."},   merge by core's lead, then the release clerk
  {"type": "core-task", "key": K, "task": "...", "fable": false}   a session of core's lead with a free task
]}"""
import json, sys
ROOT = '/data/haiyangw/nrpic'
spec = json.load(open(sys.argv[1]))
core_js = open(ROOT + '/scratch/orch/nrpic-core-wave-3.js').read()
rounds_js = open(ROOT + '/scratch/orch/nrpic-rounds.js').read()
def grab(src, name, nxt):
    i = src.index('const ' + name + ' = ') + len('const ' + name + ' = '); j = src.index('\nconst ' + nxt + ' = ', i); return json.loads(src[i:j])
SRC = grab(core_js, 'SRC', 'CL'); CLERK = grab(core_js, 'CLERK', 'SLOT'); GATE = grab(rounds_js, 'GATE', 'AUX')
pre = core_js[core_js.index('const ROOT = '):core_js.index('const SRC = ')]
fn = core_js[core_js.index('const CW = ROOT'):core_js.index('// release candidate v0.4')].replace("phase: v === 'v0.6' ? 'Round' : 'Release ' + v", "phase: 'Core'")
OWN = {'A-emd-pbh': 'track/A-emd-pbh', 'B-emd-gw': 'track/B-emd-gw', 'C-sidm': 'track/C-sidm', 'D-bh-dress': 'track/D-bh-dress', 'E-stoch-inf': 'track/E-stoch-inf', 'F-hills': 'track/F-hills', 'kb': 'kb/main'}
READ = {'A-emd-pbh': 'problem S1 335-365; track sheet 708-725; verification suite 834-860', 'B-emd-gw': 'problem S2 366-379; track sheet 727-745; verification suite 834-860', 'C-sidm': 'problem S3 380-393; track sheet 747-764; verification suite 834-860', 'D-bh-dress': 'problem S4 394-405; track sheet 766-783; verification suite 834-860', 'E-stoch-inf': 'problem S11 445-465; track sheet 785-802; verification suite 834-860', 'F-hills': 'problem S12 466-492; track sheet 804-822; verification suite 834-860', 'kb': 'knowledge base 1218-1461'}
items = []
for it in spec['items']:
    it = dict(it)
    if it['type'] == 'pkg':
        plan = json.load(open(ROOT + '/scratch/orch/wave3_plans/%s.json' % it['owner']))
        pk = {p['key']: p for p in plan['packages']}[it['key']]
        it.update(title=pk.get('title', ''), task=pk['task'], card_hours=pk.get('card_hours', 0))
    if it['type'] == 'core-src':
        it.update({k: v for k, v in [h for h in SRC if h['key'] == it['key']][0].items()})
        it['type'] = 'core-src'
    if 'owner' in it:
        it.update(wt=ROOT + '/wt/' + it['owner'], branch=OWN[it['owner']], read=READ[it['owner']])
    items.append(it)
NOTE = ("BATCH '" + spec['name'] + "' (decision 0020: batches are sized to the five-hour usage window; each session works on something it can finish; coord/RUNBOOK.md). Release core-v0.4 is on main since 2026-11-20 (tag core-v0.4; CLAUDE.md names its executables and capabilities; announcement in tracks/orch/outbox/). Earlier sessions of wave 3 (a burst cut by the usage limit on 2026-11-20 14:35 PST, and batch 1 of the same evening, which finished) left reports in " + ROOT + "/scratch/orch/wave3_reports/<owner id>.md and briefly in " + ROOT + "/scratch/orch/batch1_result.json; sessions that were cut may have left uncommitted work in the worktree: continue your own package from it and leave other packages' files alone. No lead follows a package session in this batch unless your task says so: push your own commits when your work is closed (git pull --no-rebase --no-edit, then git push origin <branch>). " + spec.get('note', ''))
LEADNOTE = ("This is a lead session of wave 3 for the packages that have finished since the last lead session of this owner (their reports: the report files named above; their README and JOURNAL in the package directories; the plan in tracks/<ID>/PLAN-wave3.md). Where the rules above say wave 2, read wave 3 (review file tracks/<ID>/stage/REVIEW-wave3.md). Uncommitted files of sessions that were cut: commit what belongs to finished work; leave packages still in progress alone and list them, with what remains, in HANDOFF.md. Card jobs of this owner still queued or running: name them with what reads them. Gates already signed are in coord/GATES.md.")
meta = "export const meta = {\n  name: 'nrpic-batch',\n  description: " + json.dumps('Batch ' + spec['name'] + ' of wave 3 (sized to the five-hour window): ' + spec.get('what', '')) + ",\n  phases: [\n    { title: 'Core', detail: 'merges, release clerk, source packages' },\n    { title: 'Tracks', detail: 'packages, leads, gate reviews', model: 'opus' },\n  ],\n}\n\n"
body = ("const NOTE = " + json.dumps(NOTE) + "\nconst LEADNOTE = " + json.dumps(LEADNOTE) + "\nconst GATE = " + json.dumps(GATE) + "\nconst CLERK = " + json.dumps(CLERK) + "\nconst ITEMS = " + json.dumps(items, indent=1) + "\n" + fn + r'''
function brief(r) { return r ? { status: r.status, established: (r.established || []).slice(0, 5).map(x => String(x).slice(0, 400)), open: (r.failed_or_open || []).slice(0, 5).map(x => String(x).slice(0, 300)), requests: (r.requests || []).slice(0, 4).map(x => String(x).slice(0, 250)) } : { status: 'no report' } }
async function one(it) {
  if (it.type === 'pkg') {
    const dir = 'tracks/' + it.owner + '/' + it.key
    const r = await agent(c3(it.owner, it.wt, it.branch) + '\n' + NOTE + '\n\n' + helperRules(it.owner, dir) + '\n\nBrief line ranges to read if your task needs them: ' + it.read + '\n\nWORK PACKAGE ' + it.key + ' (' + it.title + '), directory ' + dir + ', card time at most ' + (it.card_hours || 0) + ' card-hours. The brief was written by the planner of this owner on 2026-11-20 (tracks/' + it.owner + '/PLAN-wave3.md); where it waits for a core release, release core-v0.4 now exists:\n' + it.task,
      Object.assign({}, OPUS, { label: it.owner + ':' + it.key, phase: 'Tracks', schema: SUMMARY }))
    return [{ label: it.owner + ':' + it.key, r: brief(r) }]
  }
  if (it.type === 'lead') {
    const r = await agent(c3(it.owner, it.wt, it.branch) + '\n' + NOTE + '\n\n' + leadRules2(it.owner, it.branch) + '\n\nBrief line ranges to read: ' + it.read + '; stage gates 674-686; context protocol 957-1004.\n' + LEADNOTE.split('<ID>').join(it.owner) + (it.extra ? '\n' + it.extra : '') + LEADX,
      Object.assign({}, OPUS, { label: it.owner + ':lead', phase: 'Tracks', schema: LEAD_SCHEMA }))
    return [{ label: it.owner + ':lead', r: r ? { paused: r.paused, summary: String(r.summary || '').slice(0, 2600), gates_complete: r.gates_complete || [], failed: (r.failed || []).slice(0, 6).map(x => String(x).slice(0, 200)), next: (r.next || []).slice(0, 3).map(x => String(x).slice(0, 250)), requests_to_orch: (r.requests_to_orch || []).slice(0, 6).map(x => String(x).slice(0, 300)), runs_pending: (r.runs_pending || []).slice(0, 5) } : { status: 'no report' } }]
  }
  if (it.type === 'gate') {
    const r = await agent(c3(it.owner, it.wt, it.branch) + '\n' + NOTE + '\n\nOwner id <ID> = ' + it.owner + '.\n' + GATE.split('%s').join(it.gate),
      Object.assign({}, OPUS, { label: it.owner + ':gate-' + it.gate, phase: 'Tracks', schema: GATE_SCHEMA }))
    return [{ label: it.owner + ':gate-' + it.gate, r: r || { status: 'no report' } }]
  }
  if (it.type === 'core-src') {
    const r = await fable(solo(it, NOTE + '\n\n'), { label: 'core:' + it.key, phase: 'Core', schema: SUMMARY })
    return [{ label: 'core:' + it.key, r: brief(r) }]
  }
  if (it.type === 'core-merge') {
    const m = await fable(leadCore(NOTE + '\n\n' + it.task), { label: 'core:merge-' + it.version, phase: 'Core', schema: SUMMARY })
    const c = await clerk(it.version)
    return [{ label: 'core:merge-' + it.version, r: brief(m) }, { label: 'core:clerk-' + it.version, r: brief(c) }]
  }
  if (it.type === 'core-task') {
    const p = leadCore(NOTE + '\n\n' + it.task)
    const o = { label: 'core:' + it.key, phase: 'Core', schema: SUMMARY }
    const r = it.fable ? await fable(p, o) : await agent(p, Object.assign({}, OPUS, o))
    return [{ label: 'core:' + it.key, r: brief(r) }]
  }
  return [{ label: 'unknown item', r: { status: 'skipped' } }]
}
const res = await parallel(ITEMS.map(it => () => one(it)))
const out = []
res.filter(Boolean).forEach(x => x.forEach(y => out.push(y)))
return out
''')
open(sys.argv[2], 'w').write(meta + pre + body)
print(len(items), 'items ->', sys.argv[2], len(meta + pre + body), 'bytes')
