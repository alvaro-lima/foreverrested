"""Exercise build invalidation, safe exports/imports, and stable progress migration."""
import importlib.util
import json
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
runtime = runpy.run_path(str(ROOT / "tests/validate.py"))
lua = runtime["lua"]
lua.execute(r'''
F.db.questData=nil; F.QuestData:Initialize()
function UnitLevel() return 7 end
function GetQuestID() return 95212 end
function GetTitleText() return 'A "quoted" quest — β\nnext' end
function GetRewardXP() return 700 end
function GetNumQuestRewards() return 1 end
function GetNumQuestChoices() return 2 end
function GetQuestItemInfo(kind,index) return 'Reward',nil,1,2,true end
function GetQuestItemLink(kind,index) return '|Hitem:'..(kind=='reward' and 123 or 200+index)..':0|h[Reward]|h' end
function GetItemInfo() return 'Reward',nil,2,10,5,'Weapon','Sword',1,'INVTYPE_WEAPON' end
function GetItemStats() return {ITEM_MOD_STRENGTH_SHORT=2} end
F.QuestData:ObserveDialogue()
F.QuestData:ObserveLog({{id=95212,title='Test',level=8,zone='Dun Morogh',objectives={{text='Pelts',numRequired=6,type='item'}}}})
assert(F.QuestData:Get(95212).choiceRewards[2].itemID==202)
assert(F.QuestData:Get(95212).rewardXPObserved.value==700)
F.QuestData:TurnedIn(95212,750)
assert(F.QuestData:Get(95212).rewardXPObserved.context=='QUEST_TURNED_IN')
exported=F.QuestData:Export()
function GetBuildInfo() return '1.60.1','new-build','',16001 end
F.QuestData:Initialize()
assert(F.QuestData.buildChanged)
local record,state=F.QuestData:Get(95212); assert(record==nil and state=='stale')
assert(not F.QuestData:Export():find('Pristine',1,true))
F.QuestData:ObserveLog({{id=95212,title='Tuned quest',level=8,zone='Dun Morogh',objectives={{numRequired=8,type='item'}}}})
assert(F.QuestData:Get(95212).rewardXPObserved==nil,'old reward XP must not survive a new build')
assert(F.QuestData:Get(95212).objectives[1].required==8)
GetRewardXP=nil; GetQuestItemInfo=nil; GetQuestItemLink=nil
F.QuestData:ObserveDialogue(); F.QuestData:ShowExport()
local originalGuide=F.Guide
local migration={id='migration-test',revision=2,quests={},steps={
 {id='new',type='note'},{id='first',type='note'},{id='second',type='note'},
}}
F.GuideLibrary:Register(migration)
F.GuideLibrary:ApplyState(migration,{revision=1,step=2,stepID='second',skippedIDs={first=true}})
assert(F.db.step==3 and F.db.skipped[2] and not F.db.skipped[1])
F.GuideLibrary:ApplyState(migration,{revision=1,step=9,stepID='removed',skippedIDs={first=true}})
assert(F.db.step==1 and F.db.skipped[2])
assert(not pcall(function() F.GuideLibrary:Register({id='bad',steps={{id='same'},{id='same'}}}) end))
F.QuestData.limit=2
F.db.questData=nil; F.QuestData:Initialize()
F.QuestData:Record(1); F.QuestData:Record(2); F.QuestData:Record(3)
local count=0; for _ in pairs(F.QuestData.saved.observations) do count=count+1 end
assert(count==2,'observation storage is bounded')
''')
document = json.loads(lua.globals().exported)
assert document["quests"][0]["rewardXPObserved"]["value"] == 750
assert document["quests"][0]["guaranteedRewards"][0]["stats"]["ITEM_MOD_STRENGTH_SHORT"] == 2
spec = importlib.util.spec_from_file_location("refresh", ROOT / "tools/refresh_quest_data.py")
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)
catalog, _ = refresh.merge(document)
assert catalog["revision"] == 1
assert refresh.merge(document, catalog)[0]["revision"] == 1, "identical imports should not bump revision"
lua.execute("parsed=" + refresh.lua(catalog))
assert lua.globals().parsed["quests"]["95212"]["questID"] == 95212
tricky = 'quotes " \\ newline\nβ -- ]] os.execute("bad")'
lua.execute("escaped=" + refresh.lua(tricky))
assert lua.globals().escaped == tricky
partial = {**document, "quests": []}
assert "95212" in refresh.merge(partial, catalog)[0]["quests"], "partial refresh must retain missing quests"
new = json.loads(json.dumps(document))
new["source"]["buildKey"] = "1.60.1:new:16001"
new["quests"] = []
retained, report = refresh.merge(new, catalog)
assert "stale: 1" in report
invalid = json.loads(json.dumps(document))
invalid["quests"][0]["baseRewardXP"] = 700
try:
    refresh.validate(invalid)
except ValueError:
    pass
else:
    raise AssertionError("Observed XP must not become base XP without evidence")
for change in ({"questID": -1}, {"buildKey": "wrong"}, {"unknownField": 1}, {"questID": True}):
    invalid = json.loads(json.dumps(document))
    invalid["quests"][0].update(change)
    try:
        refresh.validate(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError(f"Invalid import accepted: {change}")
print("PASS: build-scoped observations, reward capture, JSON/Lua round-trip, safe merge, validation, bounded storage and stable step migration.")
