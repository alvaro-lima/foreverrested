local _, F = ...
local D = F.GuideDraft
local g=D:New("alliance-zephras-10-14","Zephras 10-14 / Exit Choice","Zephras Isle",{"High Order Skyborne"},10,20)
g.targetLevel=14
g.description="Optional island continuation with exit reviews at 10 and 12; no measured fastest exit level yet."
local function cycle(key,label,ids,side,note)
    D:Group(g,key.."-pickup",label..": accept","pickup",ids,side,note)
    D:Group(g,key.."-objectives",label..": objectives","objective",ids,side,note)
    D:Group(g,key.."-return",label..": return","turnin",ids,side,note)
end
D:ClassStop(g,"entry-class","Finish your level-10 class unlock and training. This optional continuation assumes the opening island story is done. Auto recognizes completed quests. Follow-up availability is beta-dependent; check preceding hand-ins before using Skip.")
D:Note(g,"exit-at10","Exit review: level 10","Leave now if Alliance transport is available, your class milestone is done, and the remaining island tasks are long or contested. Select a mainland 10-20 guide from the minimap. Otherwise Next continues the island guide. Do not assume leaving early is possible until you check the dockmaster/story gate.")
cycle("fillion-intro","Fillion's Mission",{99260})
cycle("catching-wind","Catching Wind",{92840},{94896,94897,98512},"Batch accepted local hunts before returning. Do not start distant refugee or assassin detours simply because they are available.")
cycle("vengeance","Avenged Tenfold",{92834},nil,"Collect ten Al'Aketh Windstone Charms from the specified local enemies. Catching Wind's elemental data is interaction credit; do not treat its six data readings as six required kills.")
cycle("service","In Service of Zephras",{92860})
cycle("tower-intro","Tower Defense introduction",{93320})
D:Group(g,"tower-pickup","Take the tower's two overlapping objectives","pickup",{92642,92645})
D:Group(g,"tower-loop","Tower circuit: logistics and the breaker together","objective",{92642,92645})
D:Group(g,"tower-return","Return both tower objectives","turnin",{92642,92645})
cycle("valanaar-return","Return to Valanaar",{92880})
cycle("elder-request","The High Elder's Request",{92881})
cycle("turncoat","Find the Turncoat",{92643})
cycle("unfortunate-news","Return the Turncoat's news",{92644})
cycle("cult-plans","Report the cult's true plans",{94568})
cycle("desperate-times","Desperate Times",{92640})
D:Note(g,"exit-at12","Exit review: around level 12","Compare the next compact quest cluster with the mainland route, rather than staying until a fixed level. Stay for ready turn-ins or a useful nearby reward. Leave if the remaining battle/hermit chains mean long travel, waiting or repeated deaths and transport is available. The offline comparison is illustrative; it does not measure your current speed. Next continues the optional finale.")
cycle("battle-preparation","Prepare for Battle",{93065})
cycle("making-move","Making Our Move",{92947},nil,"Start the battle only when safe and available. Waiting for a heavily contested event can erase its XP advantage.")
cycle("inner-sanctum","The Inner Sanctum",{93958})
cycle("lorthuna","Confront Lorthuna",{93835},nil,"Follow the native quest objective; do not repeatedly attempt a dangerous event solo.")
cycle("fate","The Fate of Zephras",{94369})
cycle("next","What Comes Next",{93089})
D:Note(g,"hermit-choice","Optional hermit/refugee circuit","Do this only when nearby and offered. The Strange Hermit opens The Forest's Bounty and Free the Hollows. Unnerving Silence opens the Lady's tasks. Finish the two collection quests before taking their follow-ups. All of these are optional; Next keeps the exit path moving.")
g.steps[#g.steps].alongside={D:Task("pickup",93159,true),D:Task("objective",93159,true),D:Task("turnin",93159,true),
    D:Task("pickup",94484,true),D:Task("objective",94484,true),D:Task("turnin",94484,true)}
D:Group(g,"hermit-hunts","Optional hermit/refugee objectives together","pickup",{}, {93160,93172,94485,94486,94487,94896,94897},"Only accept follow-ups actually offered. Next confirms this optional circuit.")
g.steps[#g.steps].confirmOnNext=true
D:Group(g,"hermit-loop","Optional hermit/refugee circuit","objective",{}, {93160,93172,94485,94486,94487,94896,94897},"Native waypoints provide objective areas. Skip long or crowded detours; Next continues.")
g.steps[#g.steps].confirmOnNext=true
D:Group(g,"hermit-return","Batch accepted optional hand-ins","turnin",{}, {93160,93172,94485,94486,94487,94896,94897},"Turn in ready quests before leaving; Next continues.")
g.steps[#g.steps].confirmOnNext=true
D:Note(g,"exit-at14","Exit review: level 14 is optional","Do not grind to 14 solely to finish this guide. Leave once nearby rewards stop paying for the time. Choose Westfall / Redridge, Loch Modan / Redridge or Darkshore 10-20; Auto resumes at uncompleted steps, and Skip bypasses unwanted lower-level chains. Already accepted quest chains can still be useful at 12-14.")
D:Group(g,"onward-pickup","Take the Alliance onward introduction if offered","pickup",{}, {94946},"The Magical City of Dalaran follows What Comes Next. Confirm the actual transport destination and requirements with the dockmaster. Next confirms your departure decision.")
g.steps[#g.steps].confirmOnNext=true
D:Note(g,"finish","Island continuation finished","Choose a mainland 10-20 guide using the minimap book. Check actual Alliance transport availability; the addon never boards or travels automatically.")
F.GuideLibrary:Register(g)
