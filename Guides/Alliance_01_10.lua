local _, F = ...
local D = F.GuideDraft
-- Independently authored route circuits. Facts live in AllianceQuestData.lua.
-- No hard-coded objective counts: live Forever progress determines completion.
local g = D:New("alliance-dun-morogh-01-10", "Dun Morogh 1-10", "Dun Morogh", {"Dwarf", "Gnome"})
D:Group(g,"outfitters-pickup","Coldridge: start at Sten Stoutarm","pickup",{179},nil,
    "Approximate beta route. Take nearby offered side quests; use Next/Skip if an offer changed. Counts come from your live log.")
D:Group(g,"outfitters-hunt","Hunt the wolves near the starting camp","objective",{179})
D:Group(g,"outfitters-return","Return for gloves and the next quests","turnin",{179})
D:Trainer(g,"coldridge-class","Anvilmar: class introduction and training","Dun Morogh",.289,.670,3)
D:Group(g,"coldridge-pickup","Take the trogg quest and westbound mail","pickup",{170,233})
D:Group(g,"troggs-first","Clear the nearby troggs before leaving the camp area","objective",{170})
D:Group(g,"troggs-return","Hand in the trogg quest before the western loop","turnin",{170})
D:Group(g,"felix-pickup","Take Felix's belongings quest before the southern loop","pickup",{3361},nil,
    "Felix is in Anvilmar. If still below level 3, gain the small remaining amount nearby before taking his quest.")
D:Group(g,"mail-talin","Deliver the first mail to Talin Keeneye","turnin",{233})
D:Group(g,"boars-pickup","Take Talin's boars and onward mail","pickup",{183,234})
D:Group(g,"boars-hunt","Clear the small boars nearby","objective",{183})
D:Group(g,"boars-return","Return to Talin before heading south","turnin",{183})
D:Group(g,"grelin-mail","Deliver the second mail to Grelin Whitebeard","turnin",{234},nil,
    "Compare the reward choices with equipped gear; choose an item your class can use.")
D:Group(g,"cave-pickup","Take The Troll Cave","pickup",{182})
D:Group(g,"cave-loop","Troll cave loop: trolls and Felix's belongings","objective",{182,3361},nil,
    "Collect all three belongings during the same southern loop. The native waypoint takes priority over approximate areas.")
D:Group(g,"cave-return","Return to Grelin; take the journal follow-up","turnin",{182})
D:Group(g,"journal-pickup","Take The Stolen Journal","pickup",{218})
D:Group(g,"journal-hunt","Recover the journal from the cave leader","objective",{218},nil,
    "Fight with nearby players if the leader is difficult; avoid waiting a long time for a contested spawn.")
D:Group(g,"journal-return","Return the journal to Grelin","turnin",{218})
D:Group(g,"coldridge-exit-pickup","Take Senir's Observations and nearby hot-drink delivery","pickup",{282},{3364})
D:Group(g,"anvilmar-return","Return Felix's belongings on the way through Anvilmar","turnin",{3361},{3364})
D:Note(g,"mug-option","Optional: Bring Back the Mug",
    "If Nori's delivery led to Bring Back the Mug, return it only while still nearby. Avoid a separate long return after leaving Coldridge.")
g.steps[#g.steps].optional=true
g.steps[#g.steps].alongside = {D:Task("pickup",3365,true), D:Task("turnin",3365,true)}
D:Group(g,"pass-mail","Hand Senir's Observations to Mountaineer Thalos","turnin",{282})
D:Group(g,"pass-pickup","Take the onward report and supplies","pickup",{420},{2160})
D:Group(g,"kharanos-arrive","Kharanos: deliver the report and supplies","turnin",{420},{2160})
D:Trainer(g,"kharanos-class","Kharanos: train, vendor and set a useful hearthstone","Dun Morogh",.472,.522,5)
D:Group(g,"steelgrill-mail","Take Tools for Steelgrill","pickup",{400},{98321,98319})
D:Group(g,"steelgrill-delivery","Deliver the tools at Steelgrill's Depot","turnin",{400})
D:Group(g,"depot-pickup","Collect the depot's hunting quests","pickup",{317,313},{5541})
D:Group(g,"depot-hunt","Collect boar meat and bear fur near the depot","objective",{317},nil,
    "Required kill XP contributes to this loop. Do not make separate trips for each drop type.")
D:Group(g,"depot-first-return","Hand in Stocking Jetsteam","turnin",{317})
D:Group(g,"west-mail","Take Evershine before travelling west","pickup",{318})
D:Group(g,"kharanos-west-pickup","Kharanos: take the gnome objective before the western circuit","pickup",{412},{287})
D:Group(g,"wendigo-loop","Complete the Grizzled Den while moving west","objective",{313},{5541},
    "Ammo for Rumbleshot is optional: deliver only while already near Hegnar; do not let it force a separate trip.")
D:Group(g,"evershine-delivery","Deliver Evershine at Brewnall Village","turnin",{318},{5541})
D:Group(g,"brewnall-pickup","Take the wildlife follow-up and stout quest","pickup",{319,315},{98326})
D:Group(g,"west-wildlife","Western circuit: wildlife, stout and nearby gnomes","objective",{319,412,315},{287,98326},
    "Work accepted side quests in the same loop. Avoid Old Icebeard's separate elite detour; compare available equipment rewards.")
D:Group(g,"brewnall-return","Batch Brewnall hand-ins","turnin",{319,315},{98326})
D:Group(g,"bellowfiz-mail","Take Return to Bellowfiz","pickup",{320})
D:Group(g,"western-return","Kharanos and depot: batch western hand-ins","turnin",{412,313,320},{287,98321},
    "Return to Bellowfiz offers usable weapons. Compare damage and proficiency instead of item colour alone.")
D:Trainer(g,"kharanos-refresh","Train on the return through Kharanos","Dun Morogh",.472,.522,10)
D:Group(g,"east-ranch","Eastern road: take the leopard pelts at Amberstill","pickup",{95212},{314})
D:Group(g,"quarry-pickup","Collect the quarry's overlapping trogg quests","pickup",{432,433},{95217,95214})
D:Group(g,"quarry-loop","Quarry circuit: troggs, nearby leopards and accepted side tasks","objective",{432,433,95212},{95217,95214},
    "A dropped blasting-powder item may start 95213 before 95214 is offered. Use it manually if found. The smith's green reward is a blacksmithing recipe, not a gear upgrade.")
D:Group(g,"quarry-return","Batch quarry turn-ins before leaving","turnin",{432,433},{95217,95213,95214})
D:Group(g,"ranch-return","Return the pelts at Amberstill","turnin",{95212},{314},
    "Optional gear detour: Protecting the Herd offers green equipment, including a usable hammer. Attempt the elite only with suitable help; skip it when the extra time/risk is high.")
D:Note(g,"vagash-gear-option","Optional: Amberstill green equipment",
    "If Protecting the Herd is accepted and you have suitable help, complete it while here. Compare the usable reward with equipped gear. Next continues when this detour is not worthwhile.")
g.steps[#g.steps].optional=true
g.steps[#g.steps].optionalBenefit='gear'
g.steps[#g.steps].gearQuestIDs={314}
g.steps[#g.steps].alongside = {D:Task("objective",314,true), D:Task("turnin",314,true)}
D:Note(g,"pilot-gear-option","Optional eastern-road weapon upgrade",
    "If you are still levelling near the north-pass road, The Lost Pilot (419) leads to A Pilot's Revenge (417), which offers green dagger/hammer choices. Compare them with your class and current weapon before taking that detour.")
g.steps[#g.steps].optional=true
g.steps[#g.steps].optionalBenefit='gear'
g.steps[#g.steps].gearQuestIDs={417}
g.steps[#g.steps].alongside = {D:Task("pickup",419,true), D:Task("turnin",419,true),
    D:Task("pickup",417,true), D:Task("objective",417,true), D:Task("turnin",417,true)}
D:Finish(g,"dun-morogh","The next region is normally Loch Modan.")

g = D:New("alliance-elwynn-01-10", "Elwynn Forest 1-10", "Elwynn Forest", {"Human"})
D:Group(g,"northshire-intro","Northshire: speak to Deputy Willem","pickup",{783})
D:Group(g,"northshire-mcbride","Deliver A Threat Within inside the abbey","turnin",{783})
D:Group(g,"northshire-pickup","Take kobolds and nearby wolves","pickup",{7,33})
D:Group(g,"northshire-hunt","Clear wolves and kobolds around the abbey","objective",{7,33})
D:Group(g,"northshire-return","Batch the first Northshire hand-ins","turnin",{7,33})
D:Trainer(g,"northshire-class","Northshire: class introduction and training","Elwynn Forest",.495,.425,3)
D:Group(g,"echo-pickup","Take Investigate Echo Ridge","pickup",{15})
D:Group(g,"echo-workers","Clear the workers near Echo Ridge","objective",{15})
D:Group(g,"echo-return","Return to Marshal McBride","turnin",{15})
D:Group(g,"northshire-final-pickup","Take the final kobolds and vineyard objectives","pickup",{21,18},{6,3903})
D:Group(g,"milly-intro","Visit Milly before the vineyard loop","turnin",{}, {3903},"If Milly Osworth is offered, turn it in and take Milly's Harvest before the vineyard loop. Next continues.")
g.steps[#g.steps].confirmOnNext = true
D:Group(g,"milly-harvest-pickup","Take Milly's Harvest if offered","pickup",{}, {3904},"Optional vineyard overlap. Next continues if this offer is absent.")
g.steps[#g.steps].confirmOnNext = true
D:Group(g,"northshire-final-hunt","Echo Ridge and vineyard: complete the nearby objectives","objective",{21,18},{6,3904})
D:Group(g,"northshire-final-return","Batch Northshire turn-ins","turnin",{21,18},{6,3904})
D:Group(g,"goldshire-mail-pickup","Take Report to Goldshire and nearby onward deliveries","pickup",{54},{2158,3905})
D:Group(g,"goldshire-arrive","Deliver the report in Goldshire","turnin",{54},{2158,3905})
D:Trainer(g,"goldshire-class","Goldshire: train, vendor and set a useful hearthstone","Elwynn Forest",.423,.658,5)
D:Group(g,"farm-necklace-pickup","Stonefield farm: ask about the necklace","pickup",{85})
D:Group(g,"farm-necklace-delivery","Ask Billy Maclure about the necklace","turnin",{85})
D:Group(g,"farm-pie-pickup","Take Pie for Billy","pickup",{86})
D:Group(g,"farm-pie-ingredients","Collect the pie ingredients from nearby boars","objective",{86})
D:Group(g,"farm-pie-return","Return the ingredients to Auntie Bernice","turnin",{86})
D:Group(g,"farm-billy-pickup","Take Back to Billy","pickup",{84})
D:Group(g,"farm-billy-return","Bring the pie to Billy","turnin",{84})
D:Group(g,"farm-goldtooth-pickup","Take Goldtooth before the mine visit","pickup",{87})
D:Group(g,"goldshire-pickup","Take the mine's overlapping objectives","pickup",{62,47,60})
D:Group(g,"fargodeep-loop","Fargodeep: explore while gathering candles and gold dust","objective",{62,47,60},nil,
    "Complete all three in one mine visit; do not return after only one collection finishes.")
D:Group(g,"farm-goldtooth-objective","Recover the necklace from Goldtooth","objective",{87},nil,
    "Check Goldtooth's level and clear a safe pull. Skip the fight explicitly if it is unsuitable for your character.")
D:Group(g,"farm-goldtooth-return","Return the necklace at Stonefield farm","turnin",{87})
D:Group(g,"goldshire-mine-return","Batch the mine hand-ins in Goldshire","turnin",{62,47,60})
D:Group(g,"jasperlode-pickup","Take Jasperlode and the east-road introduction","pickup",{76,40})
D:Group(g,"thomas-intro","Deliver A Fishy Peril to Marshal Dughan","turnin",{40})
D:Group(g,"east-road-pickup","Take Further Concerns","pickup",{35})
D:Group(g,"jasperlode-explore","Explore Jasperlode while heading east","objective",{76})
D:Group(g,"thomas-arrive","Deliver Further Concerns to Guard Thomas","turnin",{35})
D:Group(g,"east-hunt-pickup","Take eastern road and logging-camp objectives","pickup",{37,52,5545,83})
D:Group(g,"lost-guards","Find the first lost guard","turnin",{37})
D:Group(g,"rolf-pickup","Take Discover Rolf's Fate","pickup",{45})
D:Group(g,"east-loop","Eastern loop: wildlife, logs and Defias bandanas","objective",{52,5545,83},nil,
    "Do not enter a dense murloc camp alone just to finish the guard chain. Clear a safe path or ask nearby players.")
D:Group(g,"rolf-discovery","Find Rolf's remains when the camp is safe","turnin",{45})
D:Group(g,"thomas-report-pickup","Take Report to Thomas","pickup",{71})
D:Group(g,"thomas-report","Return the guard report","turnin",{71})
D:Group(g,"east-turnins","Batch eastern hand-ins","turnin",{52,5545,83})
D:Group(g,"dughan-report-pickup","Take Deliver Thomas' Report","pickup",{39},{46})
D:Group(g,"goldshire-east-return","Return to Goldshire with the mine and guard reports","turnin",{76,39},{46})
D:Trainer(g,"goldshire-refresh","Goldshire: train before the western circuit","Elwynn Forest",.423,.658,10)
D:Group(g,"westbrook-intro","Take Westbrook Garrison Needs Help!","pickup",{239})
D:Group(g,"westbrook-arrive","Deliver the Westbrook introduction","turnin",{239})
D:Group(g,"gnolls-pickup","Take Riverpaw Gnoll Bounty","pickup",{11},{176})
D:Group(g,"gnolls-hunt","Clear suitable gnolls near Westbrook","objective",{11},{176},
    "Hogger is an optional group/reward detour. Do not wait or repeatedly die for it. Skip unrelated long errands unless already on their path.")
D:Group(g,"gnolls-return","Return the bounty at Westbrook","turnin",{11},{176})
D:Note(g,"hogger-gear-option","Optional: Hogger group reward",
    "If Hogger is accepted and a nearby group can finish it promptly, compare its rewards with your current equipment. Next continues without this detour.")
g.steps[#g.steps].alongside = {D:Task("objective",176,true), D:Task("turnin",176,true)}
D:Finish(g,"elwynn","The next region is normally Westfall.")

g = D:New("alliance-teldrassil-01-10", "Teldrassil 1-10", "Teldrassil", {"NightElf"})
D:Group(g,"shadowglen-pickup","Shadowglen: take nearby wildlife quests","pickup",{456,458})
D:Group(g,"woodland-intro","Speak to Tarindrella","turnin",{458})
D:Group(g,"shadowglen-followup","Take The Woodland Protector follow-up","pickup",{459})
D:Group(g,"shadowglen-loop","Clear wildlife and grell around Shadowglen","objective",{456,459})
D:Group(g,"shadowglen-return","Batch the first hand-ins","turnin",{456,459})
D:Trainer(g,"shadowglen-class","Aldrassil: class introduction and training","Teldrassil",.588,.445,3)
D:Group(g,"webwood-pickup","Take the wildlife follow-up and Webwood Venom","pickup",{457,916},{4495})
D:Group(g,"webwood-loop","Northern loop: wildlife and cave spiders","objective",{457,916},{4495})
D:Group(g,"webwood-return","Return to Aldrassil","turnin",{457,916},{4495})
D:Group(g,"egg-pickup","Take Webwood Egg","pickup",{917})
D:Group(g,"egg-cave","Collect the egg in the spider cave","objective",{917},nil,
    "Only add Iverron's antidote ingredients if that quest is already offered/accepted while nearby; do not make a separate collection tour.")
D:Group(g,"egg-return","Return the egg","turnin",{917})
D:Group(g,"tenaron-pickup","Take Tenaron's Summons","pickup",{920})
D:Group(g,"tenaron-visit","Climb Aldrassil to Tenaron","turnin",{920})
D:Group(g,"first-water-pickup","Take Crown of the Earth","pickup",{921})
D:Group(g,"first-water","Fill the vessel at the nearby moonwell","objective",{921})
D:Group(g,"first-water-return","Return the vessel to Tenaron","turnin",{921})
D:Group(g,"dolanaar-mail-pickup","Take Crown of the Earth onward delivery","pickup",{928},{2159})
D:Group(g,"dolanaar-arrive","Dolanaar: deliver the vessel and nearby mail","turnin",{928},{2159})
D:Trainer(g,"dolanaar-class","Dolanaar: train, vendor and set a useful hearthstone","Teldrassil",.557,.598,5)
D:Group(g,"dolanaar-pickup","Take the east-village, dreamcatcher and nearby collection quests","pickup",{475,2438,488,997},{87288})
D:Group(g,"breeze-visit","Visit Gaerolas Talvethren in Starbreeze Village","turnin",{475})
D:Group(g,"corruption-pickup","Take Gnarlpine Corruption","pickup",{476})
D:Group(g,"dreamcatcher","Collect the dreamcatcher and nearby wildlife materials","objective",{2438,488},{87288})
D:Group(g,"dreamcatcher-return","Return the dreamcatcher, corruption report and Zenn's materials","turnin",{2438,476,488})
D:Group(g,"ferocitas-pickup","Take Ferocitas the Dream Eater and Seek Redemption","pickup",{2459,489})
D:Group(g,"ferocitas-loop","Finish the eastern furbolg loop and collect fel cones","objective",{2459,489},{87288})
D:Group(g,"ferocitas-return","Batch the eastern hand-ins","turnin",{2459,489},{87288})
D:Group(g,"denalan-delivery","Deliver Denalan's Earth beside Lake Al'Ameth","turnin",{997})
D:Group(g,"timberlings-pickup","Take the overlapping timberling quests","pickup",{918,919})
D:Group(g,"timberlings-loop","Lake loop: timberling seeds and sprouts together","objective",{918,919})
D:Group(g,"timberlings-return","Return both timberling quests","turnin",{918,919})
D:Group(g,"second-water-pickup","Take the next Crown of the Earth vessel and road patrol","pickup",{929,487},{932,490})
D:Group(g,"second-water-loop","Fill the vessel while near the lake","objective",{929})
D:Group(g,"second-water-return","Return the vessel to Dolanaar","turnin",{929})
D:Group(g,"road-patrol-objective","Clear the road's Gnarlpine ambushers","objective",{487})
D:Group(g,"road-patrol-return","Return the road patrol","turnin",{487})
D:Group(g,"banethil-pickup","Take the Ban'ethil relic quest","pickup",{483})
D:Group(g,"sleeping-druid-pickup","Inside Ban'ethil: speak to Oben","pickup",{2541})
D:Group(g,"banethil-loop","Ban'ethil: relics and the shaman charm","objective",{483,2541},nil,
    "Pull carefully inside the barrow. Share a clear or Skip explicitly if the area is unsafe or repeatedly contested.")
D:Group(g,"sleeping-druid-return","Return the charm to Oben inside the barrow","turnin",{2541})
D:Group(g,"claw-pickup","Take Druid of the Claw after Oben's first turn-in","pickup",{2561})
D:Group(g,"claw-objective","Free Rageclaw using Oben's charm","objective",{2561},nil,
    "Follow the quest's current instructions for Rageclaw and the charm. Check the fight before committing; Skip explicitly if unsafe.")
D:Group(g,"claw-return","Return to Oben before leaving Ban'ethil","turnin",{2561})
D:Group(g,"banethil-return","Return the Ban'ethil relics in Dolanaar","turnin",{483},{490,932})
D:Note(g,"teldrassil-optional","Optional remaining nearby quests",
    "If below 10, finish accepted road/Melenas objectives before distant city errands. Do not force Oakenscowl or Ursal solo for a reward; compare any group reward against current gear.")
g.steps[#g.steps].alongside = {D:Task("objective",932,true), D:Task("turnin",932,true),
    D:Task("objective",2499,true), D:Task("turnin",2499,true)}
D:Finish(g,"teldrassil","The next region is normally Darkshore.")

g = D:New("alliance-zephras-01-10", "Zephras Isle 1-10", "Zephras Isle", {"High Order Skyborne"})
g.revision = 2
D:Group(g,"coming-of-age","Thendal Grove: begin Coming of Age","pickup",{92460})
D:Group(g,"rorian-intro","Speak to Rorian the Dayseeker","turnin",{92460})
D:Group(g,"grove-pickup","Take nearby wildlife and cirrusflies","pickup",{92461,92462})
D:Group(g,"grove-loop","Complete the grove's overlapping area objectives","objective",{92461,92462})
D:Group(g,"grove-return","Return both grove quests","turnin",{92461,92462})
D:Trainer(g,"grove-class","Thendal Grove: class introduction and training","Zephras Isle",.420,.234,3)
D:Group(g,"grove-next","Take the queen and Elemental Unrest","pickup",{92463,92464},{92474,94414,92597,93552,92473})
D:Group(g,"cirrusfly-queen","Defeat the cirrusfly queen while heading northeast","objective",{92463},{92597,93552,92473})
D:Group(g,"yala-intro","Deliver Elemental Unrest to Yala","turnin",{92464})
D:Group(g,"agitators-pickup","Take Agitators","pickup",{92465})
D:Group(g,"agitators-loop","Clear the wind and cult objectives together","objective",{92465},{92597,93552,92473})
D:Group(g,"agitators-return","Return to Yala","turnin",{92465})
D:Group(g,"rorian-return-pickup","Take Return to Rorian","pickup",{92469})
D:Group(g,"grove-batch-return","Batch the grove turn-ins","turnin",{92469,92463},{92597,93552,92473,92474,94414})
D:Group(g,"aetheen-pickup","Take Aetheen of the Gales","pickup",{92471})
D:Group(g,"aetheen-intro","Speak to Aetheen beside Rorian","turnin",{92471})
D:Group(g,"matriarch-pickup","Take Foul Matriarch","pickup",{92470},{96638})
D:Group(g,"matriarch-loop","Complete the matriarch objective west of the grove","objective",{92470},{92544},
    "Do not leave the grove storyline early: later offers may depend on this turn-in. Group for a difficult named enemy rather than repeated deaths.")
D:Group(g,"matriarch-return","Return Foul Matriarch","turnin",{92470},{92544})
D:Group(g,"next-step-pickup","Take The Next Step","pickup",{92472},{96638})
D:Group(g,"shendar-arrive","Deliver The Next Step in Shen'dar Village","turnin",{92472},{96638})
D:Group(g,"shendar-welcome-pickup","Take the Alliance village welcome","pickup",{93461})
D:Group(g,"shendar-welcome","Meet the village contacts","objective",{93461})
D:Group(g,"shendar-welcome-return","Return the welcome quest","turnin",{93461})
D:Trainer(g,"shendar-class","Shen'dar: train, vendor and set a useful hearthstone","Zephras Isle",.450,.454,5)
D:Group(g,"shendar-pickup","Take village hunts and the Alliance magical objective","pickup",{92515,92553,94413},{92596,92516,93319})
D:Group(g,"shendar-west-loop","Western village loop: pelts, provisions and magical threats","objective",{92515,92553,94413},{92516,93319,92596},
    "The Problem With Prideclaws rewards a bag. This remains useful across classes even when its equipment reward value would be small.")
D:Group(g,"shendar-west-return","Batch the western village hand-ins","turnin",{92515,92553,94413},{92516,93319,92596})
D:Group(g,"highlands-pickup","Take the criminal and supply objectives","pickup",{92517},{92551,93036,93926})
D:Group(g,"highlands-loop","Highlands: finish bandits and accepted nearby supplies","objective",{92517},{92551})
D:Group(g,"highlands-return","Return the highlands hand-ins","turnin",{92517},{92551})
D:Group(g,"cult-introduction","Speak to Sania Silverstream if Infiltrating the Cult was offered","turnin",{}, {93036},"Complete this village introduction before taking Falaath Village. Next continues if absent.")
g.steps[#g.steps].confirmOnNext = true
D:Group(g,"falaath-pickup","Take Falaath Village if offered","pickup",{}, {92529},"Optional nearby chain. Next continues after taking the delivery, or if it is absent.")
g.steps[#g.steps].confirmOnNext = true
D:Group(g,"falaath-visit","Visit the missionary at Falaath Village if offered","turnin",{}, {92529},"Optional continuation: Next continues if the Falaath delivery is absent.")
g.steps[#g.steps].confirmOnNext = true
D:Group(g,"faithful-pickup","Take Among the Faithful if offered","pickup",{}, {92528},"Take the local follow-up, then return through Shen'dar. Next continues.")
g.steps[#g.steps].confirmOnNext = true
D:Group(g,"faithful-return","Return the missionary report","turnin",{}, {92528},"Next continues after the optional report, or if no report was offered.")
g.steps[#g.steps].confirmOnNext = true
D:Group(g,"valanaar-intro-pickup","Take the Alliance introduction to Valanaar","pickup",{92701},{92550})
D:Group(g,"valanaar-arrive","Deliver To Valanaar","turnin",{92701},{92550})
D:Trainer(g,"valanaar-class","Valanaar: class training and supplies","Zephras Isle",.662,.766,10)
D:Note(g,"zephras-exit-choice","Level 10 island exit choice",
    "If already 10, finish your class milestone and check Alliance transport. You can select a mainland 10-20 guide, or Zephras 10-14 / Exit Choice to continue the later story. Staying until 14 is optional; review nearby quests again around 12. If transport is story-gated, finish its required chain first. Next continues the opening island circuit.")
D:Group(g,"valanaar-pickup","Take the nearby Alliance scholar introduction","pickup",{92699,92727},{93949})
D:Group(g,"magister-visit","Speak to the Supreme Magister","turnin",{92699})
D:Group(g,"windfield-pickup","Take Blood Tithe on the westbound road","pickup",{92679})
D:Group(g,"windfield-arrive","Deliver Blood Tithe to Aamelia","turnin",{92679})
D:Group(g,"windfield-hunts-pickup","Take the overlapping Windfield hunts","pickup",{92682,92683,92684,92685})
D:Group(g,"windfield-loop","Southwestern loop: complete the family's nearby objectives together","objective",{92682,92683,92684,92685},{92698},
    "These objectives share a compact area. Do the accepted tasks together rather than returning for each one.")
D:Group(g,"windfield-return","Batch Windfield hand-ins","turnin",{92682,92683,92684,92685},{92698})
D:Group(g,"windfield-defend-pickup","Take Standing Our Ground","pickup",{92693})
D:Group(g,"windfield-defend","Complete the local defense","objective",{92693})
D:Group(g,"windfield-defend-return","Return the defense quest","turnin",{92693})
D:Group(g,"windfield-news-pickup","Take Deliver the News for the return road","pickup",{92703})
D:Group(g,"scholar-satchel","Find the scholar's satchel west of Valanaar","turnin",{92727})
D:Group(g,"scholar-followup","Take the satchel's follow-up","pickup",{92849})
D:Group(g,"scholar-rescue","Find and help the missing scholar","objective",{92849},{93949})
D:Group(g,"scholar-handoff","Complete the scholar's first handoff","turnin",{92849})
D:Group(g,"scholar-return-pickup","Take the return to Valanaar","pickup",{92850})
D:Group(g,"scholar-return","Return through Alvarion and then Valanaar","turnin",{92703,92850},{93949})
D:Note(g,"zephras-optional","Optional remaining village quests",
    "If below 10, finish accepted local hunts before long western family/cult chains. Alliance-only choices are used here; Horde Windshaper alternatives are excluded.")
D:Finish(g,"zephras","Finish your level-10 class milestone before taking the Alliance onward journey.")
