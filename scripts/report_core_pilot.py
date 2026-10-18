"""Build a factual local investor report from actual product/pilot capture records."""
import argparse
import json
from pathlib import Path
import hashlib

ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser()
p.add_argument('--run',help='Pilot run directory name; latest pilot selected if omitted')
a=p.parse_args()
records=[]
for file in sorted((ROOT/'company/core-browser').glob('*/summary.json')):
    record=json.loads(file.read_text())
    if record.get('suite') in {'product','pilot'}:records.append((file.parent,record))
pilots=[(d,r) for d,r in records if r.get('suite')=='pilot' and (not a.run or d.name==a.run)]
if a.run and not pilots:p.error('No recorded pilot with that run ID')
run,pilot=pilots[-1] if pilots else (None,None)
# Combine immutable continuation captures; count only actual executed AI task sessions.
if pilot:
    pilot_root=pilot.get('resume_root') or run.name
    baseline=ROOT/'docs/evidence/product-pilot-summary.json'
    if baseline.exists() and json.loads(baseline.read_text()).get('pilot_root')!=pilot_root:
        p.error('Historical report is frozen; use compare_core_pilots.py for a later pilot')
    segments=[]
    for config_file in (ROOT/'company/core-browser').glob('*/config.json'):
        c=json.loads(config_file.read_text())
        if config_file.parent.name==pilot_root or c.get('resume_root')==pilot_root:
            segments.append(config_file.parent)
    actual=[]
    for segment in sorted(segments):
        for f in sorted(segment.glob('session-*/report.json')):
            r=json.loads(f.read_text())
            r['evidence']=str(f.relative_to(ROOT))
            original_status=r['status']
            if not r.get('tasks') and r.get('failure')=='Session budget reached':
                r['status']='incomplete_interrupted_before_tool'
                r['classification_note']='Original report closed after operator stop; model planning returned, but no selected task executed. Original record retained unchanged.'
            r['recorded_status']=original_status
            actual.append(r)
    actual.sort(key=lambda r:r['id'])
    if len({r['id'] for r in actual})!=len(actual):raise ValueError('Duplicate persona IDs; refusing to inflate pilot counts')
    completed=[r for r in actual if r['status'] in {'completed','completed_with_failure'} and r.get('tasks') and r['model'].get('calls_completed',0)>0]
    pilot={**pilot,'pilot_root':pilot_root,'captures':[str(d.relative_to(ROOT)) for d in segments],
           'attempted':len(actual),'completed':len(completed),'incomplete':len(actual)-len(completed),
           'successes':sum(bool(r['passed']) for r in actual),'passed':len(actual)==10 and all(r['passed'] for r in actual),
           'runtime_ms':sum(r['runtime_ms'] for r in actual),'model_calls':sum(r['model']['calls_attempted'] for r in actual),
           'model_calls_completed':sum(r['model']['calls_completed'] for r in actual),
           'prompt_tokens':sum(r['model']['prompt_tokens'] for r in actual),'completion_tokens':sum(r['model']['completion_tokens'] for r in actual),
           'evaluations_completed':sum('evaluation' in r for r in actual),'sessions':actual}
    original_config=ROOT/'company/core-browser'/pilot_root/'config.json'
    original=json.loads(original_config.read_text())
    import datetime as dt
    started=dt.datetime.strptime(pilot_root.split('-')[0],'%Y%m%dT%H%M%SZ').replace(tzinfo=dt.timezone.utc).timestamp()-(1800000-original['total_budget_ms'])/1000
    ended=max((d/'summary.json').stat().st_mtime for d in segments if (d/'summary.json').exists())
    pilot['wall_elapsed_ms']=round((ended-started)*1000)
    evaluated=[r['evaluation'] for r in actual if 'evaluation' in r]
    import re
    pilot['ai_scope_mentions_browser_local']=sum(bool(re.search(r'browser|local|not publish|only this computer',str(e.get('contribution_visibility','')),re.I)) for e in evaluated)
    pilot['screenshots']=sum(len(list(Path(r['evidence']).parent.glob('*.png'))) for r in actual)
    pilot['finalized_traces']=sum((Path(r['evidence']).parent/'trace.zip').exists() for r in actual)
    pilot['screenshot_errors']=sum(bool(a.get('screenshot_error')) for r in actual for a in r['actions'])
    pilot['capture_sha256']={str(d.relative_to(ROOT)):{str(f.relative_to(d)):hashlib.sha256(f.read_bytes()).hexdigest() for f in d.rglob('*') if f.is_file()} for d in segments}
    aggregate=ROOT/'company/core-pilots'/pilot_root
    aggregate.mkdir(parents=True,exist_ok=True)
    (aggregate/'aggregate.json').write_text(json.dumps(pilot,indent=2))

preflights=[(d,r) for d,r in records if r.get('suite')=='product']
commit=pilot['commit'] if pilot else preflights[-1][1]['commit'] if preflights else 'not inspected'
lines=['# CORE HQ — evidence-backed product testing report','',f'CORE development commit: `{commit}` (`v9.2/earth-first`). Public production was not tested.','',
       'CORE HQ preservation commit: `5dc8a4e`. No CORE modification, push, deployment, paid API use or external data disclosure.','',
       '## What was actually tested','',
       'Real Chrome against immutable local CORE source and committed datasets. Product preflight checks rendered dated findings, an actual agent/team conversation including an unsupported question, and a consented synthetic contribution in the browser-local mission queue, reload persistence and isolation. Earth and direct-room entry results are explicitly separate. No functions or data are replaced with mocks. Offline map tiles remain blocked.','',
       'Pilot control: a local qwen3:8b model sees rendered accessibility observations and the actual mission catalog, selects from actual observed mission controls and chooses a high-level browser task, and supplies its question or synthetic contribution text. Playwright executes that selected task through the real UI. A separate local-model evaluation reads the observed UI. These are bounded model-selected browser tools, not unrestricted autonomous browsing.','',
       '## Recorded execution','', '| Run | Kind | Completed | Passed | Runtime |', '| --- | --- | --- | --- |']
for directory,record in preflights:
    lines.append(f"| `{directory.name}` | {record.get('entry','earth')} preflight (scripted) | {record.get('completed',0)} | {record.get('successes',0)} | {record.get('runtime_ms',0)/1000:.1f}s |")
if pilot:
    lines.append(f"| `{run.name}` | AI pilot | {pilot['completed']}/{pilot['requested']} | {pilot['successes']} | {pilot['runtime_ms']/1000:.1f}s |")
    lines += ['',f"AI pilot: **{pilot['completed']} completed, {pilot.get('incomplete',0)} incomplete, {pilot['requested']-pilot.get('attempted',0)} unstarted** of {pilot['requested']} requested sessions. A completed session can contain a failed task; completion is not a pass.",
              f"Local inference: {pilot['model_calls_completed']}/{pilot['model_calls']} calls returned; {pilot['prompt_tokens']} reported prompt tokens and {pilot['completion_tokens']} reported output tokens. Tokens for interrupted calls are unknown. Paid API cost: **$0**. Hardware/electricity costs were not measured.",
              f"Comprehension evaluations returned: {pilot['evaluations_completed']}. Wall time, including the continuation pause: {pilot['wall_elapsed_ms']/1000:.1f}s of the original 1,800s budget. Each recorded session is capped at 180s.",
              '', '| AI persona | Actual result | Verified tasks | Runtime |', '| --- | --- | --- | --- |']
    for session in pilot['sessions']:
        verified=', '.join(k for k,v in session['tasks'].items() if v) or 'none'
        lines.append(f"| {session['persona']} | {session['status']}; {'pass' if session['passed'] else 'task failure'} | {verified} | {session['runtime_ms']/1000:.1f}s |")
else:
    lines += ['', '**Ten-session AI pilot not executed: critical-interaction preflight has not yet passed.** Earlier navigation AI sessions are separate evidence and are not counted as this pilot.']
lines += ['', 'Interrupted persona attempts are retained and not rerun. The aggregate counts actual executed tasks; an operator-stopped planning-only attempt is incomplete even if its raw process report was finalized.', '', '## Observations and reproducibility','']
issues=[]
selected=preflights+([(directory,json.loads((directory/'summary.json').read_text())) for directory in segments if (directory/'summary.json').exists()] if pilot else [])
for directory,summary in selected:
    for report_file in sorted(directory.glob('session-*/report.json')):
        r=json.loads(report_file.read_text());evidence=str(report_file.relative_to(ROOT))
        if r.get('failure'):
            short=r['failure'].split('\n')[0]
            lines.append(f'- Observed execution failure: {short} Evidence: `{evidence}` and its adjacent trace/screenshots. This may be a harness/environment failure; it is not automatically a confirmed CORE defect.')
        for issue in r.get('issues',[]):
            if issue.get('classification')=='grounded_ai_ux_hypothesis':
                issues.append({'run':directory.name,'session':r['id'],**issue})
                # Quote presence is an evidence anchor, not proof that the complaint is true.
                # Keep raw hypotheses in the private aggregate; do not promote them to investor findings.
                pass
        if r.get('http_errors'):
            lines.append(f"- Captured HTTP errors in `{evidence}`: "+', '.join(f"{e['status']} {e['url'].split('/',3)[-1]}" for e in r['http_errors'])+'. Optional local-state 404s are environment limitations, not established production regressions.')
if pilot:
    lines += ['',f"AI comprehension output: {pilot['ai_scope_mentions_browser_local']}/{pilot['evaluations_completed']} returned contribution-visibility answers explicitly mentioned browser/local/nonpublication scope (a text-presence check, not a human comprehension score).",'Automated UX complaints are not confirmed defects. Manual review found at least one complaint about missing source dates contradicted by its own quoted retrieval date. Original model outputs and their quote checks are retained privately. A quote match alone does not establish a valid usability issue.']
lines += ['', 'Reproduce with `python3 scripts/test_core.py --suite product --ref '+commit+'`. After a passing critical preflight, use `--suite pilot --mode local-agent --model qwen3:8b --sessions 10 --execute-pilot`. Use `--entry room` for the explicitly selected direct conversation-room path; it does not imply that the Earth entry works. Each capture retains exact commit provenance, actions, screenshots, trace, model decisions and SHA-256 capture hashes. These commands use existing local inference only.',
          '', '## Recommended improvements and scale decision','',
          'Prioritize any reproducible product issue recorded in docs/CORE_HQ_PRODUCT_ISSUES.md. Investigate source/data readiness and make unavailable features explicit; separate deterministic agent responses, optional local-model wording and recorded simulations in comprehension checks. Retest proposed changes on a new exact commit before claiming a product fix.',
          '', '**Not ready to scale to 100+ sessions.** One small local-model pilot cannot establish general usability, correctness of every data analysis or production reliability. Expand task-specific assertions and review failure attribution first. The current scope does not validate online map imagery, live upstream freshness, production deployment or real-world impact.',
          '', '## AI versus human testing','',
          '**Actual human participants: 0.** Named AI personas are task instructions, not recruited people. First-time comprehension is model-reported interpretation of the rendered interface; it is not a human completion rate. No external panel, account or recruitment was used.']
if pilot:
    domain_passes=sum(all(r['tasks'].get(k) for k in (['location',r['assigned_task']] if r['assigned_task'] in {'dialogue','contribution'} else ['location'])) for r in actual)
    max_runtime=max(r['runtime_ms'] for r in actual)
    lines=['# CORE HQ — product testing report','',
           f"CORE: `v9.2/earth-first` at `{commit}`. CORE HQ preservation commit: `5dc8a4e`. No CORE changes, push, deployment, external disclosure or paid APIs.",'',
           '## Actual scope and results','',
           'Real Chrome tested the existing direct conversation room for the San Francisco housing/resilience mission. Local qwen3:8b selected a browser task and supplied the question or synthetic contribution text; Playwright operated actual controls. This is a bounded tool controller. CORE’s own conversation answers came from its deterministic cited engine, not an autonomous language model.',
           '',f"**10 persona/browser attempts: {pilot['completed']} completed, {pilot['incomplete']} incomplete. {domain_passes} executed sessions passed their assigned product checks; {pilot['successes']} also completed the comprehension evaluation.** Three early evaluations timed out. The environmental-researcher attempt was interrupted after planning, before its selected task; it was not rerun. The six remaining personas continued in a second preserved capture under the original deadline.",
           '', '| AI persona | Verified product checks | Evaluation / completion |', '| --- | --- | --- |']
    for r in actual:
        checks=', '.join(k for k,v in r['tasks'].items() if v) or 'none executed'
        outcome='completed; evaluation returned' if r['passed'] else 'completed checks; evaluation timeout' if r['tasks'] and 'timeout' in r.get('failure','') else 'incomplete; interrupted before task'
        lines.append(f"| {r['persona']} | {checks} | {outcome} |")
    lines += ['',
              'Verified interactions: dated committed datasets delivered and displayed; four agent consultations with question/answer and unsupported-question refusal checks; three consented synthetic mission contributions with consent rejection, reload persistence and independent-context isolation. Contributions remained in disposable local browser storage. The encrypted vault, live upstream freshness and analytical calculations were not independently validated.',
              '',f"**Runtime:** {pilot['wall_elapsed_ms']/60000:.2f} minutes wall time, including the continuation pause, within the original 30-minute budget. Longest session: {max_runtime/1000:.1f}s, below 180s. **Inference:** {pilot['model_calls_completed']}/{pilot['model_calls']} calls returned; {pilot['prompt_tokens']:,} prompt + {pilot['completion_tokens']:,} output tokens reported. Usage for three interrupted evaluation calls is unknown. **Paid API cost: $0**; hardware/electricity unmeasured.",
              '', '## Failures and reproducible findings','',
              '- **Earth startup remains broken in the recorded offline setup.** Local records returned 200, while a diagnostic showed map/style loaded but CORE readiness false. Waiting and CORE’s low-quality option did not recover it. The direct-room success does not validate the Earth journey. See [CORE issue HQ-CORE-001](CORE_HQ_PRODUCT_ISSUES.md) for captures and reproduction; production impact is unverified.',
              '- **Controller evaluation needed correction.** Forty-second inference caps caused three failures; remaining personas used shorter observed context and up to ninety seconds within their session budgets. A premature staged-dialogue assertion was fixed in HQ and then passed. CORE was never patched.',
              f"- **AI comprehension remains noisy.** Six evaluations returned; {pilot['ai_scope_mentions_browser_local']}/6 contribution-visibility answers explicitly mentioned browser/local/nonpublication scope. This is a text-presence check, not human comprehension accuracy. At least one claimed missing source dates while quoting a retrieval date. Such complaints are retained as hypotheses, not confirmed CORE defects.",
              '- Optional local backend-state requests returned 404 and remain in the logs. External map requests were blocked. Online map rendering, production behavior, live CORE model wording and real-world impact were not tested.',
              '', '## Recommendations and scale decision','',
              'CORE team: investigate map-independent mission initialization and truthful loading/unavailable controls. Retest the Earth entry on an exact new commit after any approved fix. HQ: improve semantic review of UX claims and broaden task/mission coverage before scaling.',
              '', '**Not ready for 100+ sessions.** The bounded local pipeline works, but Earth entry, evaluation reliability and coverage of only one mission remain material limits. **Actual human participants: 0.** AI personas and model interpretations are separate from human beta testing.',
              '', '## Evidence','',
              f"Private aggregate: `company/core-pilots/{pilot['pilot_root']}/aggregate.json`. Immutable captures: "+', '.join('`'+d+'`' for d in pilot['captures'])+f". Retained: {pilot['screenshots']} screenshots and {pilot['finalized_traces']} finalized traces. All nine completed task sessions have traces. The interrupted fourth attempt lacks a finalized trace, and two initial screenshots timed out; these capture failures remain in the logs. Returned decisions and capture hashes are retained.",
              '', 'Reproduce critical interactions: `python3 scripts/test_core.py --suite product --entry room --ref '+commit+'`. The [handoff](CORE_HQ_HANDOFF.md) records gates, limitations and Git state. Report generation runs no additional browser sessions.']
    projection={k:pilot[k] for k in ['pilot_root','commit','requested','attempted','completed','incomplete','successes','runtime_ms','wall_elapsed_ms','model_calls','model_calls_completed','prompt_tokens','completion_tokens','cost_usd','human_participants','evaluations_completed','ai_scope_mentions_browser_local','captures','capture_sha256','screenshots','finalized_traces','screenshot_errors']}
    projection['sessions']=[{k:r.get(k) for k in ['id','persona','status','recorded_status','tasks','passed','runtime_ms','task_completion','model','evidence','classification_note']} for r in actual]
    evidence_dir=ROOT/'docs/evidence';evidence_dir.mkdir(exist_ok=True)
    (evidence_dir/'product-pilot-summary.json').write_text(json.dumps(projection,indent=2))

out=ROOT/'docs/CORE_HQ_TESTING_REPORT.md';out.write_text('\n'.join(lines)+'\n')
print('Report written:',out)
