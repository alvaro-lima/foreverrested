local _, F = ...
-- Installed Forever QuestieDB items 15883/15882 and objects 177792/177790.
-- The joined pendant is made at Tajarri's Shrine of Remulos (NPC 11799).
F.QuestObjectiveLocations={
    [272]={
        {zone="Darkshore",x=.4887,y=.1132,name="Strange Lockbox: Half Pendant of Aquatic Agility",actionTitle="Collect Half Pendant of Aquatic Agility",itemID=15883,role="requirement",approximate=true},
        {zone="Westfall",x=.1794,y=.3318,name="Strange Lockbox: Half Pendant of Aquatic Endurance",actionTitle="Collect Half Pendant of Aquatic Endurance",itemID=15882,role="requirement",approximate=true},
        {zone="Moonglade",x=.3652,y=.401,name="Shrine of Remulos: combine the pendant halves",actionTitle="Combine the pendant halves at the Shrine of Remulos",resultItemID=15885,role="requirement",approximate=true},
    },
    [5061]={{zone="Darnassus",x=.3537,y=.084,name="Mathrengyl Bearwalker",role="requirement",approximate=true}},
}
for id,locations in pairs(F.QuestObjectiveLocations) do
    local record=F.ClassicQuestPolicy and F.ClassicQuestPolicy.records[id]
    if record then for _,point in ipairs(locations) do record.locations[#record.locations+1]=point end end
end
-- Explicit loot-source mappings belong in data, not UI or inferred item names.
-- Verified 2026-10-01 against Forever quest 95212 and item 267414:
-- https://www.wowhead.com/forever/quest=95212/never-saddle-on-quality
-- https://www.wowhead.com/forever/item=267414/pristine-leopard-pelt
F.QuestTargets = {
    -- Installed QuestieDB Forever item 5808 lists these normal loot sources.
    [1134] = {title="Pridewings of Stonetalon",
        -- QuestieDB Forever NPC 4011, Stonetalon spawn reference (60.54,48.72).
        location={zone="Stonetalon Mountains",x=.6054,y=.4872,
            label="Pridewing hunting area",approximate=true},
        locations={
            {zone="Stonetalon Mountains",x=0.6054,y=0.4872,label="Pridewing hunting area",approximate=true},
            {zone="Stonetalon Mountains",x=0.7767,y=0.5409,label="Pridewing hunting area",approximate=true},
            {zone="Stonetalon Mountains",x=0.7747,y=0.4385,label="Pridewing hunting area",approximate=true},
            {zone="Stonetalon Mountains",x=0.6201,y=0.6428,label="Pridewing hunting area",approximate=true},
            {zone="Stonetalon Mountains",x=0.4616,y=0.4687,label="Pridewing hunting area",approximate=true},
            {zone="Stonetalon Mountains",x=0.5534,y=0.4182,label="Pridewing hunting area",approximate=true},
            {zone="Stonetalon Mountains",x=0.4288,y=0.3849,label="Pridewing hunting area",approximate=true},
        },
        objectives={
        {index=1,itemID=5808,item="Pridewing Venom Sac",mob="Young Pridewing"},
        {index=1,itemID=5808,item="Pridewing Venom Sac",mob="Pridewing Wyvern"},
        {index=1,itemID=5808,item="Pridewing Venom Sac",mob="Pridewing Skyhunter"},
        {index=1,itemID=5808,item="Pridewing Venom Sac",mob="Pridewing Consort"},
    }},
    [95212] = {
        title = "Never Saddle on Quality",
        -- Approximate hunting area, not the exact position of a moving creature.
        -- Public route reference and installed Forever route agree on this point:
        -- https://www.foreverwisp.com/guides/wow-forever-dwarf-gnome-leveling-guide
        location = {mapID = 1426, zone = "Dun Morogh", x = .764, y = .614,
            label = "Elder Snow Leopard hunting area", approximate = true},
        objectives = {
            {index = 1, itemID = 267414, item = "Pristine Leopard Pelt", mob = "Elder Snow Leopard"},
        },
    },
}
-- Additional shared loot objectives, using the installed Forever QuestieDB
-- sources recorded in Alliance_HuntingLocations.lua. Keep ingredients separate.
local grouped = {
    {11,"Riverpaw Gnoll Bounty",{{782,"Painted Gnoll Armband",{"Riverpaw Outrunner","Riverpaw Runt"}}}},
    {47,"Gold Dust Exchange",{{773,"Gold Dust",{"Kobold Miner","Kobold Tunneler","Kobold Geomancer","Goldtooth"}}}},
    {60,"Kobold Candles",{{772,"Large Candle",{"Kobold Miner","Kobold Tunneler","Kobold Geomancer","Goldtooth"}}}},
    {156,"Gather Rot Blossoms",{{1598,"Rot Blossom",{"Skeletal Fiend","Skeletal Horror"}}}},
    {297,"Gathering Idols",{{2636,"Carved Stone Idol",{"Stonesplinter Digger","Stonesplinter Geomancer","Berserk Trogg"}}}},
    {313,"The Grizzled Den",{{2671,"Wendigo Mane",{"Wendigo","Young Wendigo","Elder Wendigo","Wendigo Shaman","Edan the Howler","Old Icebeard"}}}},
    {416,"Rat Catching",{{3110,"Tunnel Rat Ear",{"Tunnel Rat Digger","Tunnel Rat Forager","Tunnel Rat Geomancer","Tunnel Rat Kobold","Tunnel Rat Scout","Tunnel Rat Surveyor","Tunnel Rat Vermin"}}}},
    {418,"Thelsamar Blood Sausages",{
        {3172,"Boar Intestines",{"Mountain Boar","Elder Mountain Boar","Mangy Mountain Boar"}},
        {3173,"Bear Meat",{"Black Bear Patriarch","Elder Black Bear","Grizzled Black Bear","Ol' Sooty"}},
        {3174,"Spider Ichor",{"Cliff Lurker","Forest Lurker","Wood Lurker","Shanda the Spinner"}},
    }},
    {459,"The Woodland Protector",{{3297,"Fel Moss",{"Grell","Grellkin"}}}},
    {470,"Digging Through the Ooze",{{3349,"Sida's Bag",{"Black Ooze","Crimson Ooze","Monstrous Ooze"}}}},
}
for _,quest in ipairs(grouped) do
    local record={title=quest[2],objectives={}}
    for index,item in ipairs(quest[3]) do
        for _,mob in ipairs(item[3]) do
            record.objectives[#record.objectives+1]={index=index,itemID=item[1],item=item[2],mob=mob}
        end
    end
    F.QuestTargets[quest[1]]=record
end
