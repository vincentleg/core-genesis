/** Triage hints only: no automatic CORE defect confirmation or human-usability claims. */
function classifyFailure(stage,message){
 if(['planning','evaluation'].includes(stage))return 'model_evaluation_failure';
 if(/strict mode violation|intercepts pointer events|unknown journey|invalid journey plan/i.test(message))return 'hq_harness_defect';
 if(/ERR_CONNECTION|ERR_NAME_NOT_RESOLVED|Failed to fetch|ECONNREFUSED|Local model HTTP/i.test(message))return 'environment_network_limitation';
 if(/Session budget|deadline|timed out|Timeout.*exceeded/i.test(message))return 'needs_triage';
 return 'needs_triage';
}
module.exports={classifyFailure};
