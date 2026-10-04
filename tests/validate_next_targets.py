from pathlib import Path
base=Path(__file__).with_name('validate.py');setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)};exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
F.Guide={steps={{id='return',type='turnin',questID=1071},{id='venom',type='objective',questID=1134}}}
F.db.step=1;F.db.skipped={}
F.QuestLog.TurnedIn=function() return false end
F.QuestLog.byID={[1071]={complete=true},[1134]={id=1134,title='Pridewings of Stonetalon',complete=false,objectives={{text='Pridewing Venom Sac: 0/12',type='item',finished=false}}}}
assert(#F.GuideEngine:Targets()==4,'upcoming accepted collection offers normal Pridewing sources')
F.SecureTarget:Create()
F.SecureTarget:UpdateTasks(F.GuideEngine:Targets())
local button=F.SecureTarget.buttons[1]
assert(#F.SecureTarget.desiredTargets==1 and #button.mobs==4,'one icon for shared drop objective')
assert(not F.SecureTarget.buttons[2]:IsShown())
local expected='/cleartarget\n/targetexact Young Pridewing\n/targetexact [@target,noexists][@target,dead][@target,noharm] Pridewing Wyvern\n/targetexact [@target,noexists][@target,dead][@target,noharm] Pridewing Skyhunter\n/targetexact [@target,noexists][@target,dead][@target,noharm] Pridewing Consort\n/cleartarget [@target,dead][@target,noharm]\n/tm [@target,exists,harm,nodead] !8'
assert(button.attributes.macrotext==expected,'fallback exact matches preserve a living hostile target')
F.SecureTarget:UpdateTasks(F.SecureTarget.desiredTargets)
assert(#button.mobs==4 and button.attributes.macrotext==expected,'refresh preserves grouped sources')
local names={}
GameTooltip.AddLine=function(_,text) names[text]=true end
button.scripts.OnEnter(button)
assert(GameTooltip.text=='Target list' and names['Young Pridewing'] and names['Pridewing Consort'],'common tooltip title lists all grouped mob names')
UnitName=function() return 'Pridewing Consort' end
UnitGUID=function() return 'pridewing-guid' end
UnitCanAttack=function() return true end
UnitIsDeadOrGhost=function() return false end
button.scripts.PostClick(button,'LeftButton')
assert(F.SecureTarget.toolTargetGUID=='pridewing-guid','any grouped source activates target following')
combat=true
F.SecureTarget:UpdateTasks({{mob='Other mob'}})
assert(#button.mobs==4 and button.attributes.macrotext==expected,'group remains fixed in combat')
combat=false
assert(F.ObjectiveQueue:ObjectiveZone(F.QuestLog.byID[1134],F.QuestLog.byID[1134].objectives[1],1)=='Stonetalon Mountains','venom objective belongs to Stonetalon')
local record=F.GuideEngine:TargetRecord(F.QuestLog.byID[1134])
assert(record.location.x==.6054 and record.location.y==.4872,'hunting location has sourced coordinates')
GetRealZoneText=function() return 'Stonetalon Mountains' end
F.Guide.faction='Alliance';F.Guide.zone='Ashenvale'
F.db.step=2;F.Travel.entryPending=true
assert(not F.Travel:EnsureEntry(),'already at hunting zone; no trip back to nominal chapter zone')
assert(not F.Guide.steps[2].entryTravel)
F.db.step=1
F.db.skipped[2]=true
assert(#F.GuideEngine:Targets()==0,'skipped hunt offers no targets')
F.db.skipped={};F.QuestLog.byID[1134].complete=true
assert(#F.GuideEngine:Targets()==0,'finished hunt offers no targets')
F.QuestLog.byID[1134]=nil
assert(#F.GuideEngine:Targets()==0,'unaccepted hunt offers no targets')
''')
print('PASS: upcoming collection targets, source mapping, skips and completion')
