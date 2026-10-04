"""Release gate: each scheduled quest phase needs its own recorded location.

Run with --guide ID to gate a specific chapter. Missing evidence exits nonzero;
the JSON report is a repair list, never permission to guess destinations.
"""
import argparse
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def audit(guide_id=None):
    base = ROOT / 'tests/validate.py'
    setup = base.read_text().split("lua.execute(r'''", 2)
    ns = {'__file__': str(base)}
    exec(setup[0] + "lua.execute(r'''" + setup[1], ns)
    lua = ns['lua']
    lua.execute('F.LoadDatabase()')
    f = lua.globals().F
    missing, checked = [], 0
    for _, identity in f.GuideLibrary.order.items():
        g = f.GuideLibrary.guides[identity]
        if not g.sourceGuideID or guide_id and identity != guide_id:
            continue
        f.Guide = g
        for _, step in g.steps.items():
            for _, task in f.GuideEngine.Tasks(f.GuideEngine, step).items():
                role = {'pickup':'start', 'objective':'requirement', 'turnin':'end'}.get(task.type)
                if not role or not task.questID:
                    continue
                checked += 1
                locations = f.GuideEngine.ActionLocations(f.GuideEngine, task)
                located = len(locations) > 0
                if not located:
                    missing.append(dict(guideID=identity, stepID=step.id,
                        questID=task.questID, action=task.type))
    if not checked:
        raise ValueError('No quest actions selected')
    return dict(checkedActions=checked, missing=missing,
                passed=not missing, guideID=guide_id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guide')
    args = parser.parse_args()
    report = audit(args.guide)
    (ROOT / 'Data/MISSING_QUEST_LOCATIONS.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f"{'PASS' if report['passed'] else 'FAIL'}: {report['checkedActions']} actions; "
          f"{len(report['missing'])} missing action locations")
    raise SystemExit(0 if report['passed'] else 1)
