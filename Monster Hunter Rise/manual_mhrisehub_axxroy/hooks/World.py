# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation
from .Options import Victory, QuestDensity

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value



########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################



# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    if hasattr(multiworld, "re_gen_passthrough"):
        return

    regions_to_remove = []
    locations_to_keep = []
    victory = get_option_value(multiworld, player, "victory_condition")
    postgame = get_option_value(multiworld, player, "shuffle_postgame") or False
    questdensity = get_option_value(multiworld, player, "quest_density")
    
    if victory == Victory.option_master_rank:
        locations_to_keep = ["The Devil's Reincarnation - 1", "The Devil's Reincarnation - 2"]
        if not postgame: 
            regions_to_remove = ["Master 6 Star Quests"]
        #print("locations master rank", victory, player)
    elif victory == Victory.option_high_rank:
        locations_to_keep = ["The Allmother - 1", "The Allmother - 2"]
        if postgame:
            regions_to_remove = [
                "Master 1 Star Quests", "Master 2 Star Quests", "Master 3 Star Quests", 
                "Master 4 Star Quests", "Master 5 Star Quests", "Master 6 Star Quests"
            ]
        else:
            regions_to_remove = [
                "Master 1 Star Quests", "Master 2 Star Quests", "Master 3 Star Quests", 
                "Master 4 Star Quests", "Master 5 Star Quests", "Master 6 Star Quests",
                "7 Star Quests"
            ]
        #print("locations high rank", victory, player)
    elif victory == Victory.option_low_rank:
        locations_to_keep = ["Blue, Round, and Cute - 1", "Blue, Round, and Cute - 2"]
        if postgame:
            regions_to_remove = [
                "Master 1 Star Quests", "Master 2 Star Quests", "Master 3 Star Quests", 
                "Master 4 Star Quests", "Master 5 Star Quests", "Master 6 Star Quests",
                "7 Star Quests", "6 Star Quests", "5 Star Quests"
            ]
        else:
            regions_to_remove = [
                "Master 1 Star Quests", "Master 2 Star Quests", "Master 3 Star Quests", 
                "Master 4 Star Quests", "Master 5 Star Quests", "Master 6 Star Quests",
                "7 Star Quests", "6 Star Quests", "5 Star Quests", "4 Star Quests"
            ]
        #print("locations low rank", victory, player)
    for region in multiworld.regions:
        if region.player != player or region.name in ["Manual", "Menu"]:
            continue
        #print(region.name)
        if region.name in regions_to_remove:
            #print("region removed")
            for location in list(region.locations):
                if location.name not in locations_to_keep:
                    region.locations.remove(location)
            #print(list(region.locations))
        else:
            quest_names = {loc.name[:-4] for loc in region.locations if "Relic:" not in loc.name}
            #print(quest_names)
            if questdensity == QuestDensity.option_reduced:
                if locations_to_keep[0][:-4] in quest_names:
                    quest_names.remove(locations_to_keep[0][:-4])
                    quests_to_keep = set(multiworld.random.sample(sorted(quest_names), 4))
                    quests_to_keep.add(locations_to_keep[0][:-4])
                else:
                    quests_to_keep = set(multiworld.random.sample(sorted(quest_names), 5))
            elif questdensity == QuestDensity.option_normal:
                if len(quest_names) < 10:
                    quests_to_keep = quest_names
                else:
                    if locations_to_keep[0][:-4] in quest_names:
                        quest_names.remove(locations_to_keep[0][:-4])
                        quests_to_keep = set(multiworld.random.sample(sorted(quest_names), 9))
                        quests_to_keep.add(locations_to_keep[0][:-4])
                    else:
                        quests_to_keep = set(multiworld.random.sample(sorted(quest_names), 10))
            else:
                quests_to_keep = set()
            if quests_to_keep:
                for location in list(region.locations):
                    if "Relic:" not in location.name and location.name[:-4] not in quests_to_keep:
                        region.locations.remove(location)
    if hasattr(multiworld, "clear_location_cache"):
        multiworld.clear_location_cache()

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    items_to_remove = []
    
    victory = get_option_value(multiworld, player, "victory_condition")
    upgrades = [i for i, v in world.item_name_to_item.items() if "Equipment" in v.get('category', [])]
    upgrades_weapon = [i for i, v in world.item_name_to_item.items() if "Weapon" in v.get('category', [])]
    arenas = [i for i, v in world.item_name_to_item.items() if "Region" in v.get('category', [])]
    victory_item = next(i for i in item_pool if i.name == "Victory")
    if victory == Victory.option_master_rank:
        victory_location_name = "The Devil's Reincarnation - 1"
        #print("items master rank", victory, player)
        upgrade_levels = 10
    elif victory == Victory.option_high_rank:
        victory_location_name = "The Allmother - 1"
        items_to_remove += upgrades * 3
        items_to_remove += arenas
        items_to_remove += ["Jungle", "Citadel"] * 2
        items_to_remove += ["Quest Rank Star"] * 6
        #print("items high rank", victory, player)
        upgrade_levels = 7
    elif victory == Victory.option_low_rank:
        victory_location_name = "Blue, Round, and Cute - 1"
        items_to_remove += upgrades * 7
        items_to_remove += arenas * 2
        items_to_remove += ["Jungle", "Citadel"] * 1
        items_to_remove.remove("Shrine Ruins")
        items_to_remove += ["Quest Rank Star"] * 9
        if get_option_value(multiworld, player, "shuffle_postgame") or False:
            items_to_remove.remove("Frost Islands")
            items_to_remove.remove("Rampage & Arena")
        #print("items low rank", victory, player)
        upgrade_levels = 3
    # print(len(items_to_remove), len(item_pool))
    for item_name in items_to_remove:
        item = next(i for i in item_pool if i.name == item_name)
        item_pool.remove(item)
    # print(len(item_pool))
    try:
        location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == victory_location_name)
    except StopIteration:
        print("could not find location", victory_location_name)
        raise StopIteration()
    location.place_locked_item(victory_item)
    item_pool.remove(victory_item)
    
    location_count = len(multiworld.get_unfilled_locations(player=player))
    multiworld.random.shuffle(item_pool)
    while len(item_pool) > location_count - 1:
        try:
            item = next(i for i in item_pool if world.item_name_to_item[i.name].get('filler', False))
        except StopIteration:
            break
        item_pool.remove(item)
    i = 1
    angle = 10/upgrade_levels
    idx = 0
    multiworld.random.shuffle(upgrades_weapon)
    while len(item_pool) > location_count - 1:
        check = i - idx / angle
        if check < 0:
            i += 1
            idx = 0
        item_name = upgrades_weapon[idx]
        if idx == 13:
            print("PROBLEM!!!")
        #print(item_name)
        try:
            item = next(i for i in item_pool if i.name == item_name)
            item_pool.remove(item)
        except StopIteration:
            pass
        idx += 1
    #print([len([i for i in item_pool if i.name == n]) for n in upgrades_weapon])

    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int) -> list:
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass
