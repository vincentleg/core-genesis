const el=id=>document.getElementById(id);
try{
 const response=await fetch('./hq-status.json');if(!response.ok)throw Error('No recorded status available');const s=await response.json();
 el('load-status').textContent='Recorded execution evidence · no inference triggered by this page';
 for(const [label,value] of [['Requested branch/ref',s.source.requested_ref],['Inspected commit',s.source.commit],['Environment',s.source.environment],['Full eligible files read',s.complete_source_files_read],['Tracked file inventory',s.source.file_count]]){
  const term=document.createElement('dt'),description=document.createElement('dd');term.textContent=label;description.textContent=value??'Not inspected';el('source').append(term,description);
 }
 el('production').textContent='Public production: '+s.production.url+'. '+s.production.status+' Exact production commit: '+(s.production.commit||'unverified')+'.';
 for(const r of s.sessions){const tr=document.createElement('tr');for(const value of [r.run,r.mode+(r.model?' · '+r.model:''),r.passed?'Checks passed':(r.completed?'Recorded failures':'Incomplete'),(r.sessions||[]).reduce((n,v)=>n+(v.task_completion?.succeeded||0),0)+' / '+(r.sessions||[]).reduce((n,v)=>n+(v.task_completion?.attempted||0),0),(r.runtime_ms/1000).toFixed(1)+'s',r.model_calls??'unknown','$'+(r.cost_usd??'unknown')]){const td=document.createElement('td');td.textContent=value;tr.append(td);}el('sessions').append(tr);}
 if(!s.sessions.length)el('sessions').textContent='No completed browser sessions recorded.';
 el('pilot').textContent=s.pilot.planned_sessions+' sessions · '+s.pilot.status.replaceAll('_',' ')+' · concurrency '+s.pilot.concurrency;
 el('humans').textContent=s.human_testing.verified_participants+' independently verified participants. '+s.human_testing.status;
 el('authority').textContent=s.authority;el('history').textContent=s.historical_evidence;
}catch(e){el('load-status').textContent=e.message;}
