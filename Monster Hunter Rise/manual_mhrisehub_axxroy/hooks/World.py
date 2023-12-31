# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld
import itertools as itr
import random

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation
from .Options import Victory

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value



########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. set_rules - Creates rules for accessing regions and locations
##    3. generate_basic - Creates the item pool and runs any place_item options
##    4. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################



# Called before regions and locations are created. Not clear why you'd want this, but it's here.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    regions_to_remove = []
    locations_to_keep = []
    victory = get_option_value(multiworld, player, "victory_condition")
    postgame = get_option_value(multiworld, player, "shuffle_postgame") or False
    
    if victory == Victory.option_master_rank:
        if not postgame: 
            regions_to_remove = ["Master 6 Star Quests"]
            locations_to_keep = ["The Devil's Reincarnation"]
    elif victory == Victory.option_high_rank:
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
            locations_to_keep = ["The Allmother"]
    elif victory == Victory.option_low_rank:
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
            locations_to_keep = ["Blue, Round, and Cute"]
    for region in multiworld.regions:
        if region.player == player and region.name in regions_to_remove:
            for location in list(region.locations):
                if location.name not in locations_to_keep:
                    region.locations.remove(location)
    if hasattr(multiworld, "clear_location_cache"):
        multiworld.clear_location_cache()

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def before_generate_basic(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    items_to_remove = []
    
    victory = get_option_value(multiworld, player, "victory_condition")
    upgrades = [i for i, v in world.item_name_to_item.items() if "Equipment" in v.get('category', [])]
    upgrades_weapon = [i for i, v in world.item_name_to_item.items() if "Weapon" in v.get('category', [])]
    arenas = [i for i, v in world.item_name_to_item.items() if "Region" in v.get('category', [])]
    victory_item = next(i for i in item_pool if i.name == "Victory")
    if victory == Victory.option_master_rank:
        victory_location_name = "The Devil's Reincarnation"
        dango = [name for name, item in world.item_name_to_item.items() if "Dango" in item.get('category', [])]
        multiworld.random.shuffle(dango)
        starting_dango = next(i for i in item_pool if i.name == dango[0])
        multiworld.push_precollected(starting_dango)
        item_pool.remove(starting_dango)
    elif victory == Victory.option_high_rank:
        victory_location_name = "The Allmother"
        items_to_remove += upgrades * 3
        items_to_remove += arenas
        items_to_remove += ["Jungle", "Citadel"] * 2
        items_to_remove += ["Master Rank Star"] * 6
        multiworld.random.shuffle(upgrades_weapon)
        for itm, cnt in zip(upgrades_weapon, [5, 5, 4, 4, 3, 2]):
            items_to_remove += [itm] * cnt
    elif victory == Victory.option_low_rank:
        victory_location_name = "Blue, Round, and Cute"
        items_to_remove += upgrades * 7
        items_to_remove += arenas * 2
        items_to_remove += ["Jungle", "Citadel"] * 1
        items_to_remove.remove("Shrine Ruins")
        items_to_remove += ["Master Rank Star"] * 6
        items_to_remove += ["Quest Rank Star"] * 3
        if get_option_value(multiworld, player, "shuffle_postgame") or False:
            items_to_remove.remove("Frost Islands")
            items_to_remove.remove("Rampage & Arena")
    # print(len(items_to_remove), len(item_pool))
    for item_name in items_to_remove:
        item = next(i for i in item_pool if i.name == item_name)
        item_pool.remove(item)
    # print(len(item_pool))
    
    location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == victory_location_name)
    location.place_locked_item(victory_item)
    item_pool.remove(victory_item)
    
    location_count = len(multiworld.get_unfilled_locations(player=player))
    multiworld.random.shuffle(item_pool)
    while len(item_pool) > location_count - 1:
        item = next(i for i in item_pool if world.item_name_to_item[i.name].get('filler', False))
        item_pool.remove(item)
    
    world.add_filler_items(item_pool, [])
    
    return item_pool

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is called before the victory location has the victory event placed and locked
def before_pre_fill(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is called after the victory location has the victory event placed and locked
def after_pre_fill(world: World, multiworld: MultiWorld, player: int):
    pass

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data