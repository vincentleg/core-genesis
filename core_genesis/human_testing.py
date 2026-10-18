"""Validate locally imported human research records. No recruitment, provider calls, or inferred participation."""
import copy
import re


def validate_human_record(record):
    if not isinstance(record, dict) or set(record) != {'schema_version','platform','study_id','target','declared_participants','participants','evidence','consent_status'}:
        raise ValueError('Expected versioned human-study fields only')
    if record['schema_version'] != 1 or record['consent_status'] not in {'documented','pending','unknown'}:
        raise ValueError('Unsupported version or consent status')
    target = record['target']
    if not isinstance(target,dict) or not target.get('environment') or not (target.get('commit') or target.get('deployment')):
        raise ValueError('Exact commit or deployment and environment required')
    participants = record['participants']
    if not isinstance(participants,list) or type(record['declared_participants']) is not int or record['declared_participants'] != len(participants):
        raise ValueError('Participant count must match actual imported participant rows')
    if participants and (record['consent_status'] != 'documented' or not record['evidence']):
        raise ValueError('Participant records require documented consent and evidence; keep unconsented data outside ingestion')
    ids, tasks = set(), {}
    if participants and target.get('commit') and not re.fullmatch(r'[0-9a-f]{40}',str(target['commit'])):
        raise ValueError('An actual study commit must be a full SHA')
    for person in participants:
        if set(person) != {'participant_id','consent_evidence','tasks','feedback','issues','evidence'}:
            raise ValueError('Use pseudonymous participant records; unknown fields rejected')
        pid = person['participant_id']
        if not isinstance(pid,str) or not re.fullmatch(r'P[0-9]{1,8}',pid) or pid in ids:
            raise ValueError('Unique pseudonymous P-number required')
        ids.add(pid)
        if not all(isinstance(person[k],list) for k in ['tasks','feedback','issues','evidence']):
            raise ValueError('Tasks, feedback, issues and evidence must be structured lists')
        if not person['consent_evidence'] or not person['evidence']:
            raise ValueError('Participant consent and participation evidence required')
        if not isinstance(person['tasks'],list) or not person['tasks']:
            raise ValueError('Actual performed tasks required')
        seen = set()
        for task in person['tasks']:
            if set(task) != {'task_id','completed','evidence'} or type(task['completed']) is not bool or not task['evidence'] or task['task_id'] in seen:
                raise ValueError('Unique task IDs, boolean completion and evidence required')
            seen.add(task['task_id'])
            counts = tasks.setdefault(task['task_id'], {'performed':0,'completed':0})
            counts['performed'] += 1
            counts['completed'] += int(task['completed'])
    for counts in tasks.values(): counts['completion_rate'] = counts['completed']/counts['performed']
    result = copy.deepcopy(record)
    result.update(actual_human_participants=len(participants),task_metrics=tasks,verification='Imported claims validated structurally; external evidence authenticity requires human review')
    return result
