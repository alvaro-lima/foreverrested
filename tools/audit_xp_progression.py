"""Required-only XP and explicit recovery coverage for every playable chapter."""
import json
from pathlib import Path
from audit_01_10 import guides
ROOT=Path(__file__).resolve().parents[1]

def main():
    reference=json.loads((ROOT/'Data/alliance-reference.json').read_text(encoding='utf-8'))['quests']
    rows=[]
    for guide in guides(1,30):
        required=set();optional=set();classes=set()
        for step in guide['steps']:
            if step['type']!='turnin' or not step.get('questID'):continue
            bucket=classes if step.get('classes') else optional if step.get('optional') else required
            bucket.add(step['questID'])
        recovery=[{'stepID':s['id'],'targetLevel':s['targetLevel'],'zone':s.get('zone'),
                   'x':s.get('x'),'y':s.get('y'),'required':not bool(s.get('optional'))}
                  for s in guide['steps'] if s.get('levelRecovery')]
        flexible='zephras' in guide['id'] and guide['minLevel']>=10
        if not flexible:
            assert recovery and recovery[-1]['targetLevel']==guide['maxLevel'],guide['id']
            assert all(s['required'] and s['zone'] and s['x'] is not None and s['y'] is not None for s in recovery)
        missing=[i for i in required if reference.get(str(i),{}).get('listedXP') is None]
        rows.append({'guideID':guide['id'],'title':guide['title'],'requiredTurninIDs':sorted(required),
            'excludedOptionalTurninIDs':sorted(optional-required),'excludedClassTurninIDs':sorted(classes-required),
            'listedRequiredQuestXP':sum(reference.get(str(i),{}).get('listedXP',0) or 0 for i in required),
            'missingRewardIDs':missing,'recoverySteps':recovery,'flexibleExit':flexible,
            'questOnlyExitLevelVerified':False})
    output={'chaptersReviewed':len(rows),'optionalXPExcluded':True,'classXPExcluded':True,
            'limits':['Listed XP is reference data, not a verified level-adjusted reward.',
                      'These bands include explicit required combat recovery; quests alone do not guarantee the exit level.',
                      'Live level/XP governs recovery completion. Optional work may reduce recovery, but is never assumed.',
                      'Zephras 10+ continuation deliberately allows early departure.'],'chapters':rows}
    (ROOT/'Data/XP_PROGRESSION_AUDIT.json').write_text(json.dumps(output,indent=2)+'\n')
    lines=['# Required-only XP progression review','',f"All {len(rows)} playable chapters reviewed. Optional and class-specific turn-ins contribute zero to the general baseline.",'',
        'Level bands describe quest circuits plus explicit required combat recovery. They are not quest-only XP promises. Recovery uses actual level and displays live XP remaining; skipping recovery bypasses the intended level gate.','',
        '| Chapter | Required listed quest XP | Required recovery steps |','|---|---:|---:|']
    lines += [f"| {r['title']} | {r['listedRequiredQuestXP']:,} | {len(r['recoverySteps']) if not r['flexibleExit'] else 'Flexible exit'} |" for r in rows]
    lines += ['','## Ashenvale correction','',
        'Super Reaper 6000 is required local work beside the Gaxim circuit. Aggressive Defense is scheduled in the introductory chapter after a level-23 safety check, with the same action IDs and no duplicate objectives in the next chapter.',
        'Level-24 recovery uses Foulweald Warriors (23–24); earlier recovery retains Wrathtail Myrmidons (20–21). Final Ashenvale recovery uses Ghostpaw Alphas (27–28) instead of level-24–25 furbolgs. City deliveries, escorts and higher-level detours remain optional.',
        'The introductory chapter now includes the nearby Raene delivery and Elemental Bracers circuit, bringing its required listed reward XP to 25,535. The long city, Barrens, escort and high-level optional detours are no longer scheduled at its exit. This still leaves substantial XP recovery; the listed reward total cannot establish an exit level at 24.','',
        '## Limits','']+['- '+s for s in output['limits']]
    (ROOT/'Data/XP_PROGRESSION_AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('PASS:',len(rows),'chapters; required-only rewards, explicit recovery and flexible exits')

if __name__=='__main__':main()
