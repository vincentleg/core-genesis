"""Zero-inference replay checks for actual browser and synthetic research evidence."""
import argparse
import json
from pathlib import Path


def verify(record):
    browser, panel = record['browser'], record['audience']
    for phase in ('before', 'reproduced', 'after'):
        result = browser.get(phase)
        if result:
            passed = sum(agent['passed'] for agent in result['agents'])
            if result['completed'] != len(result['agents']) or result['successes'] != passed or result['passed'] != all(agent['passed'] for agent in result['agents']):
                raise ValueError('Browser totals differ from individual real cases')
            if result['new_model_requests'] != 0:
                raise ValueError('Unexpected browser reasoning claim')
    reviews = panel.get('reviews', [])
    if len(reviews) > panel.get('target', 100) or panel.get('target', 100) > 100 or len({r['persona']['id'] for r in reviews}) != len(reviews):
        raise ValueError('Synthetic target or persona identity mismatch')
    entries = {e['id']: e for batch in panel.get('batches', []) for e in (batch.get('usage') or {}).get('entries', [])}
    for review in reviews:
        entry = entries.get(review['request_id'])
        if not entry or entry.get('usage') != review['usage'] or entry['model'] != review['model'] or entry['role'] != review['persona']['id']:
            raise ValueError('Synthetic review differs from actual request accounting')
        if json.loads(review['output']) != review['response'] or review['input']['prototype'] != panel['frozen_context'] or 'reviews' in review['input']:
            raise ValueError('Synthetic output or independent context mismatch')
    return {'actual_browser_cases': browser.get('before', {}).get('completed', 0), 'actual_synthetic_calls': len(reviews), 'target_not_completed_claim': panel.get('target', 0), 'external_api_calls': 0, 'note': 'Historical browser results and independent synthetic request records checked. This does not rerun Chrome or establish real-user validation.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('record', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(json.loads(args.record.read_text())), indent=2))
