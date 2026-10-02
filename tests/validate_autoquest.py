"""Guide-scoped quest automation, reward choices and manual override."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
namespace = {"__file__": str(root / "tests/validate.py")}
setup = (root / "tests/validate.py").read_text().split("lua.execute(r'''\nF.LoadDatabase()", 1)[0]
exec(setup, namespace)
namespace["lua"].execute(r'''
F.LoadDatabase()
F.Guide={steps={{type='pickup',questID=1},{type='pickup',questID=2},
 {type='turnin',questID=2},{type='pickup',questID=3,classes={'MAGE'}}}}
F.db.step=2;F.db.skipped={}
local A=F.AutoQuest
assert(not A:Allowed(1,'pickup') and A:Allowed(2,'pickup') and A:Allowed(2,'turnin'))
assert(not A:Allowed(2,'objective') and not A:Allowed(999,'pickup'))
function UnitClass() return 'Warrior','WARRIOR' end
assert(not A:Allowed(3,'pickup'))
F.db.skipped[2]=true;assert(not A:Allowed(2,'pickup'));F.db.skipped={}
local id,accepted,completed,reward,choices,shift=2,0,0,nil,0,false
function GetQuestID() return id end
function AcceptQuest() accepted=accepted+1 end
function IsQuestCompletable() return true end
function CompleteQuest() completed=completed+1 end
function GetNumQuestChoices() return choices end
function GetQuestReward(n) reward=n end
function IsShiftKeyDown() return shift end
A:Handle('QUEST_DETAIL');assert(accepted==1)
id=999;A:Handle('QUEST_DETAIL');assert(accepted==1);id=2
shift=true;A:Handle('QUEST_DETAIL');assert(accepted==1);shift=false
A:Handle('QUEST_PROGRESS');assert(completed==1)
A:Handle('QUEST_COMPLETE');assert(reward==0)
choices=1;A:Handle('QUEST_COMPLETE');assert(reward==1)
choices=2;reward=nil;A:Handle('QUEST_COMPLETE');assert(reward==nil)
function QuestRequiresGold() return true end
A:Handle('QUEST_PROGRESS');assert(completed==1)
combat=true;A:Handle('QUEST_DETAIL');assert(accepted==1);combat=false
local selected
C_GossipInfo={GetActiveQuests=function() return {{questID=999,isComplete=true},{questID=2,isComplete=true}} end,
 SelectActiveQuest=function(n) selected=n end}
A:Handle('GOSSIP_SHOW');assert(selected==2)
C_GossipInfo.GetActiveQuests=function() return {} end
C_GossipInfo.GetAvailableQuests=function() return {{questID=999},{questID=2}} end
C_GossipInfo.SelectAvailableQuest=function(n) selected=n end
selected=nil;A:Handle('GOSSIP_SHOW');assert(selected==2)
''')
print("PASS: Lua compilation, current/future guide filtering, skipped/class exclusions, acceptance, completion, rewards, gold, Shift/combat override and gossip selection.")
