// Explicit browser-only preview. This adapter is not the tested Python backend.
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
