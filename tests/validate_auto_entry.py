from pathlib import Path
base=Path(__file__).with_name('validate.py');setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)};exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
F.QuestPolicy.unlocks={};F.QuestPolicy.foreverUnlocks={}
UnitLevel=function() return 22 end
GetRealZoneText=function() return 'Westfall' end
C_QuestLog.GetNextWaypoint=function() end
local action={id='accept',type='pickup',questID=100009}
local g={id='auto-entry',title='Auto entry',faction='Alliance',routeGroup='test',zone='Loch Modan',
 steps={action},authoredSteps={action},questData={[100009]={title='Gathering test',locations={{role='start',zone='Loch Modan',x=.4,y=.2}}}}}
F.GuideLibrary:Register(g);F.Guide=g;F.db.guideID=g.id;F.db.step=1
F.db.skipped={};F.db.manualSkippedSteps={};F.db.confirmedSteps={};F.QuestLog.byID={}
F.Travel.entryPending=true;F.Travel:EnsureEntry()
assert(g.steps[1].entryTravel,'fixture begins with travel')
F.Refresh=function() F.GuideEngine:CatchUpOnLoad();F.GuideEngine:AdvanceSafe();F.Travel:EnsureEntry() end
F.Tracker.ShowCurrentAtTop=function() end
F.GuideEngine:ResumeAuto()
assert(g.steps[F.db.step].entryTravel,'Auto recreates unresolved travel after rebuilding actions')
''')
print('PASS: Auto retains unresolved guide-entry travel')
