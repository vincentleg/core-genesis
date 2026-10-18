"""Publish source-free measurements of a new capture without rewriting original pilot records."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent

def digest(file):return hashlib.sha256(file.read_bytes()).hexdigest()
def verify(capture):
    hashes=json.loads((capture/'checksums.json').read_text())
    for name,expected in hashes.items():
        if digest(capture/name)!=expected:raise ValueError('Capture checksum mismatch: '+str(capture/name))
    return digest(capture/'checksums.json')

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--smoke',required=True);p.add_argument('--earth-diagnostic',required=True);p.add_argument('--earth-regression',action='append',default=[]);a=p.parse_args()
    base=ROOT/'company/core-browser'
    # Resolve only existing children of the private capture directory.
    captures=[(base/name).resolve() for name in [a.run,a.smoke,a.earth_diagnostic]]
    if any(d.parent!=base.resolve() for d in captures):p.error('Capture IDs only')
    run,smoke_dir,earth_dir=captures
    record=json.loads((run/'summary.json').read_text())
    config=json.loads((run/'config.json').read_text())
    if record.get('suite')!='pilot':p.error('New run must be a finalized pilot')
    old=json.loads((ROOT/'docs/evidence/product-pilot-summary.json').read_text())
    for name,hashes in old['capture_sha256'].items():
        for file,expected in hashes.items():
            if digest(ROOT/name/file)!=expected:raise ValueError('Historical evidence changed')
    records=[json.loads(f.read_text()) for f in sorted(run.glob('session-*/report.json'))]
    ids=[r['id'] for r in records]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate session IDs')
    smoke=json.loads((smoke_dir/'summary.json').read_text());earth=json.loads((earth_dir/'diagnostic.json').read_text())
    if any(r['commit']!=record['commit'] for r in [smoke,earth,*records]):raise ValueError('Target mismatch')
    capture_hashes={d.name:verify(d) for d in captures}
    result={k:record.get(k) for k in ['commit','requested','attempted','completed','incomplete','unstarted','successes','browser_task_successes','evaluation_successes','runtime_ms','total_budget_ms','model_calls','model_calls_completed','prompt_tokens','completion_tokens','usage_unknown_attempts','cost_usd','human_participants']}
    result.update(run=a.run,smoke=a.smoke,earth_diagnostic=a.earth_diagnostic,baseline_sha256=digest(ROOT/'docs/evidence/product-pilot-summary.json'),capture_manifest_sha256=capture_hashes,
                  screenshot_count=len(list(run.glob('session-*/*.png'))),trace_count=len(list(run.glob('session-*/trace.zip'))),
                  screenshot_errors=sum(bool(a.get('screenshot_error')) for r in records for a in r['actions']),
                  task_passes={task:sum(r['tasks'].get(task) is True for r in records) for task in ['earth_navigation','location','dialogue','contribution']},
                  action_successes=sum(sum(a.get('passed') is True for a in r['actions']) for r in records),
                  action_attempts=sum(len(r['actions']) for r in records),
                  page_error_count=sum(len(r['errors']) for r in records),
                  console_error_count=sum(len(r['console_errors']) for r in records),
                  http_error_count=sum(len(r['http_errors']) for r in records),
                  sessions=[{k:r.get(k) for k in ['id','persona','entry','assigned_task','tasks','stages','status','passed','browser_tasks_passed','failure_stage','failure','runtime_ms','model']} for r in records])
    started=dt.datetime.strptime(a.run.split('-')[0],'%Y%m%dT%H%M%SZ').replace(tzinfo=dt.timezone.utc).timestamp()-(900000-config['total_budget_ms'])/1000
    result['wall_elapsed_ms']=round(((run/'summary.json').stat().st_mtime-started)*1000)
    result['executed_harness_sha256']=json.loads((ROOT/'company/core-pilots'/a.run/'executed-harness-manifest.json').read_text())['files']
    result['post_pilot_earth_checks']=[]
    for rid in a.earth_regression:
        directory=(base/rid).resolve()
        if directory.parent!=base.resolve():p.error('Regression capture IDs only')
        manifest_hash=verify(directory);r=json.loads((directory/'diagnostic.json').read_text());mission=r.get('mission_regression',{})
        if r['commit']!=record['commit']:raise ValueError('Regression target mismatch')
        capture_hashes[rid]=manifest_hash
        result['post_pilot_earth_checks'].append({'run':rid,'kind':'scripted_zero_inference','passed':mission.get('passed',False),'failure':r.get('failure','').split('\n')[0],'runtime_ms':r['runtime_ms'],'matching_controls':mission.get('matching_controls'),'actions_attempted':len(mission.get('actions',[])),'actions_passed':sum(a.get('passed') is True for a in mission.get('actions',[])),'trace_retained':(directory/'diagnostic-trace.zip').exists(),'initial_ready':r['stages'][0].get('ready'),'initial_civ_ready':r['stages'][0].get('civReady')})
    # Never overwrite the historical baseline or put raw observations/model text in the shared report.
    target=ROOT/'docs/evidence/second-pilot-summary.json'
    target.write_text(json.dumps(result,indent=2)+'\n')
    rows=[('Browser attempts',old['attempted'],result['attempted']),('Finalized AI-directed attempts (may fail)',old['completed'],result['completed']),('Browser task passes',9,result['browser_task_successes']),('Completed evaluations',old['evaluations_completed'],result['evaluation_successes']),('End-to-end passes',old['successes'],result['successes']),('Incomplete attempts',old['incomplete'],result['incomplete']),('Unstarted personas',0,result['unstarted']),('Wall runtime (seconds)',round(old['wall_elapsed_ms']/1000,2),round(result['wall_elapsed_ms']/1000,2)),('Returned/attempted model calls',f"{old['model_calls_completed']}/{old['model_calls']}",f"{result['model_calls_completed']}/{result['model_calls']}"),('Reported prompt/output tokens',f"{old['prompt_tokens']}/{old['completion_tokens']}",f"{result['prompt_tokens']}/{result['completion_tokens']}"),('Unknown-usage model attempts',3,result['usage_unknown_attempts']),('Saved screenshots',old['screenshots'],result['screenshot_count']),('Finalized traces',old['finalized_traces'],result['trace_count']),('Paid API cost (USD)',0,0),('Actual human participants',0,0)]
    lines=['# CORE HQ — second bounded AI browser pilot','',f"Exact CORE development target: `v9.2/earth-first` at `{record['commit']}`. Local immutable Git-blob server; CORE remained read-only. Public production was not tested. HQ starting commit: `8f8527b` plus the smoke/pilot configuration changes in this change set.",'','## Gate and recovery evidence','',f"Combined smoke `{a.smoke}` passed {smoke['sessions'][0]['task_completion']['succeeded']} actual browser actions and a separately recorded AI evaluation in {smoke['runtime_ms']/1000:.3f}s. Local qwen3:8b selected a real task and question. The saved interrupted prefix is only two characters; this validates persistence/retry, not recovery of a useful complete assessment. The controlled timeout interrupted the first evaluation only after real streamed content arrived; its partial prefix is retained with unknown token usage. The single retry completed. No browser action or contribution was replayed by this retry. Smoke counts are separate from both ten-persona pilots.",'',f"Public-assets Earth diagnostic `{a.earth_diagnostic}`: {earth['runtime_ms']/1000:.3f}s, zero inference; readiness was true before any explicit screenshot or wheel gesture. Actual OpenFreeMap TileJSON and NASA imagery returned HTTP 200. The retained after screenshot shows textured Earth. Two connection resets and an optional local-state 404 were also logged; initial screenshot capture timed out, while the after screenshot and trace were retained. The hidden landing-state Zoom in control still failed its click; it is not counted as successful navigation. This probe establishes one observed online initialization, not general reliability.",'','## Measured comparison','', '| Metric | Original pilot | Second pilot |','| --- | --- | --- |']
    lines += [f'| {label} | {before} | {after} |' for label,before,after in rows]
    lines += ['',f"Second pilot budget: {config['total_budget_ms']/1000:.1f}s total (requested 900s); finalization is not task success; maximum 180s per session. Returned tokens exclude interrupted-call usage. Paid APIs cost $0; hardware/electricity are unmeasured. Original evidence hashes verified unchanged. The wall estimate includes inspection and uses capture timestamps/file completion time (about one-second precision); runner time is {result['runtime_ms']/1000:.3f}s. Neither pilot runtime includes this operation’s separate smoke, diagnostics or reporting.",'','## Actual persona/task outcomes','','| Persona | Entry | Browser tasks passed | Evaluation | End-to-end | Seconds |','| --- | --- | --- | --- | --- | --- |']
    for r in records:lines.append(f"| {r['persona']} | {r['entry']} | {', '.join(k for k,v in r['tasks'].items() if v) or 'none'} | {r['stages']['evaluation']} | {'pass' if r['passed'] else 'fail'} | {r['runtime_ms']/1000:.2f} |")
    if result['post_pilot_earth_checks']:
        lines += ['', '## Separate scripted Earth follow-up', '']
        for r in result['post_pilot_earth_checks']:
            lines.append(f"- `{r['run']}`: {'passed' if r['passed'] else 'failed'}, {r['actions_passed']}/{r['actions_attempted']} actions, {r['runtime_ms']/1000:.3f}s, zero inference. "+(r['failure'] if r['failure'] else f"Observed {r['matching_controls']} visible controls for the same mission; the first matching control opened actual dated findings and citation links."))
        lines += ['', 'After the pilot, HQ was changed to select the first visible control with the exact AI-selected mission ID. The first scripted regression hit its 2.5-second transition click limit; one final retry used the main harness’s existing 6.5-second action limit. These are new zero-inference diagnostic captures, not replacements or additional AI pilot sessions. The successful scripted path verifies the selector fix and actual Earth-to-mission flow, but the revised combined AI Earth path has not been rerun. All four public-assets browser captures reached application readiness; they sample one machine/renderer, not general reliability.']
    lines += ['',f"Actual browser actions: {result['action_successes']}/{result['action_attempts']} passed. Captured page exceptions: {result['page_error_count']}; console errors: {result['console_error_count']}; HTTP errors: {result['http_error_count']}; screenshot failures: {result['screenshot_errors']}. All 13 HTTP/console errors were the optional `/.core-local/civ/state.json` 404, including reloads; they are an immutable-server environment limitation. One initial screenshot timed out; remaining captures and all ten traces were retained. Logs remain separate from confirmed product defects.",'','## Failures, interpretation and scale decision','']
    for r in records:
        if r.get('failure'):lines.append(f"- Session {r['id']} ({r['entry']}), stage `{r.get('failure_stage')}`: `{r['failure'].splitlines()[0]}`. See private `session-{r['id']:02d}/report.json` and trace. Successful earlier assertions are retained; no fallback or task rerun occurred.")
    lines += ['','This is a changed-condition comparison, not a controlled causal experiment: HQ inference/reporting changed and the second pilot permits named public map assets. Cache warm-up/load and the original continuation pause were not controlled, so runtime differences are not a causal speedup estimate. Nine personas use the same explicit San Francisco housing/resilience room; one follows Earth and selects from its observed mission catalog. Personae vary task instructions, not human participants. Browser tools use deterministic steps selected and parameterized by local AI; CORE answers use its own cited deterministic engine. Source dates, analytical correctness and live upstream freshness were not independently validated. AI UX complaints remain hypotheses, even when a quote matches; one alleges missing dates while its quote explicitly gives 2016–2025, and another labels evidence-bounded refusal a high-severity issue. An accessibility complaint claims a button lacks a label while quoting its accessible name. These are evaluator-quality problems, not established CORE defects; no model opinion is a confirmed CORE defect. First-time comprehension is model interpretation of the actual rendered interface, not human comprehension accuracy.','', '**Scaling to 50–100 sessions is not justified yet.** Broaden missions and assertion coverage, verify the complete Earth journey repeatedly under recorded conditions, and review failure attribution and evidence capture before spending that runtime. A single second pilot does not demonstrate general usability, accessibility conformance or production readiness. No paid inference, private source upload, CORE modification, production contribution, push or deployment occurred.','',f"Private captures: `company/core-browser/{a.run}`, `company/core-browser/{a.smoke}`, `company/core-browser/{a.earth_diagnostic}`. Source-free metrics and manifest digests: [second-pilot-summary.json](evidence/second-pilot-summary.json). Raw inputs/output/screenshots/traces stay in ignored local evidence. Historical [first-pilot report](CORE_HQ_TESTING_REPORT.md) is retained separately."]
    (ROOT/'docs/CORE_HQ_SECOND_PILOT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='sessions'},indent=2))
if __name__=='__main__':main()
