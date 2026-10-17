"""Export actual build evidence and runnable source; separately label the browser-only preview."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
from .artifact_builder import ROOT, FILES, run_directory

EXTRAS = ('spec.json', 'manifest.json', 'research-brief.json', 'build-report.json', 'failed-build-report.json', 'mission-events.json', 'mission-result.json', 'browser-acceptance.json')


def export_artifact(mission, output):
    prototype = mission.get('artifacts', {}).get('prototype')
    if not prototype:
        return
    directory = run_directory(mission['id'])
    output = Path(output)
    source = output / 'source'
    source.mkdir(parents=True, exist_ok=True)
    for name, digest in prototype['files'].items():
        if name not in (*FILES, 'spec.json', 'research-brief.json') or hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Artifact source differs from recorded build: ' + name)
    if json.loads((directory / 'build-report.json').read_text()) != prototype['test_report']:
        raise ValueError('Artifact report differs from actual mission evidence')
    events = [{k: e[k] for k in ('timestamp', 'mission_id', 'department', 'type', 'status', 'evidence', 'message') if k in e} for e in mission['events']]
    (directory / 'mission-events.json').write_text(json.dumps(events, indent=2))
    names = [name for name in (*FILES, *EXTRAS) if (directory / name).is_file()]
    with zipfile.ZipFile(output / 'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            data = (directory / name).read_bytes()
            (source / (name + '.txt')).write_bytes(data)
            archive.writestr(name, data)
    for name in ('index.html', 'app.js', 'style.css', 'spec.json'):
        shutil.copyfile(directory / name, output / name)
    html = (output / 'index.html').read_text().replace('LOCAL WORKING PROTOTYPE', 'BROWSER-ONLY ARTIFACT PREVIEW').replace('<script src="./app.js">', '<script src="./preview-api.js"></script><script src="./app.js">')
    (output / 'index.html').write_text(html)
    client = (output / 'app.js').read_text().replace('async function api(path,data,review=false){', 'async function api(path,data,review=false){if(window.CORE_PREVIEW)return window.CORE_PREVIEW(path,data,review);')
    (output / 'app.js').write_text(client)
    (output / 'preview-api.js').write_text(PREVIEW)
    (output / 'preview-mode.json').write_text(json.dumps({'mode': 'browser_only_preview', 'mission_id': mission['id'], 'python_backend': False, 'fresh_inference': False, 'note': 'Interactive derivative preview uses local browser storage. Actual Python acceptance and original source are in source.zip and build-report evidence.'}))


PREVIEW = r'''// Explicit browser-only preview. This adapter is not the tested Python backend.
(()=>{const key='core-first-brick-preview-v1';let spec;
window.CORE_PREVIEW=async(path,data,review)=>{
 spec=spec||await(await fetch('./spec.json')).json();
 const state=JSON.parse(localStorage.getItem(key)||'{"problems":[],"solutions":[]}');
 if(path==='state')return {...state,spec,notice:'BROWSER-ONLY PREVIEW: local browser storage, no Python backend or AI calls. Proposals and local human review never authorize real-world implementation. Download source.zip for the tested Python application.'};
 const text=(v,min,max)=>{if(typeof v!=='string'||v.trim().length<min||v.trim().length>max)throw Error('Please complete required fields within the displayed limits.');return v.trim();};
 let record={id:crypto.randomUUID(),created_at:new Date().toISOString()};
 if(path==='problems'){
  const evidence=data.evidence||'';if(evidence){const url=new URL(evidence);if(url.protocol!=='https:'||url.username)throw Error('Evidence must be a public HTTPS URL.');}
  record={...record,title:text(data.title,3,120),description:text(data.description,spec.minimum_description_chars,spec.maximum_description_chars),location:text(data.location,spec.require_location?1:0,160),evidence,status:'unreviewed'};state.problems.push(record);
 }else if(path==='solutions'){
  if(!state.problems.some(p=>p.id===data.problem_id))throw Error('Unknown problem');
  record={...record,problem_id:data.problem_id,description:text(data.description,10,spec.maximum_description_chars),status:'pending_human_review',authorized_for_real_world:false};state.solutions.push(record);
 }else if(path==='review'){
  if(!review||!['approve','reject'].includes(data.decision))throw Error('Explicit human review required');
  record=state.solutions.find(s=>s.id===data.solution_id);if(!record)throw Error('Unknown solution');Object.assign(record,{status:data.decision==='approve'?'human_approved':'human_rejected',authorized_for_real_world:false});
 }else throw Error('Unsupported browser-preview action');
 localStorage.setItem(key,JSON.stringify(state));return record;
};})();
'''
