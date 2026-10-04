"""One release gate for guide changes; runs every check even after failures."""
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
CHECKS=[
    'tools/audit_action_locations.py',
    'tests/validate_action_location_rules.py',
    'tests/validate_online_action_locations.py',
    'tests/validate_aquatic_catchup.py',
    'tests/validate_class_return_journey.py',
    'tests/validate_turnin_travel.py',
    'tests/validate_entry_travel.py',
    'tests/validate_druid_travel.py',
    'tests/validate_chapters.py',
    'tests/validate_linked_catchup.py',
    'tests/validate_objective_queue.py',
    'tests/validate_object_gathering.py',
    'tests/validate_multiple_hunting_areas.py',
    'tests/validate_xp_progression.py',
]

def main():
    results=[]
    for script in CHECKS:
        run=subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,
                           capture_output=True,text=True)
        passed=run.returncode==0
        results.append(dict(check=script,passed=passed,exitCode=run.returncode,
                            output=(run.stdout+run.stderr).strip()))
        print(f"{'PASS' if passed else 'FAIL'} {script}",flush=True)
        if not passed: print(results[-1]['output'],flush=True)
    report=dict(passed=all(r['passed'] for r in results),checks=results,
                limits='Mock checks do not establish live client behavior or measured travel time.')
    (ROOT/'Data/GUIDE_QUALITY_REPORT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return 0 if report['passed'] else 1

if __name__=='__main__':
    raise SystemExit(main())
