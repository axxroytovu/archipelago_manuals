# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld
import random
from copy import copy

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

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
    pass

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def before_generate_basic(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # print(item_pool)

    game_duration = get_option_value(multiworld, player, "game_duration") or 4

    if game_duration < 2 or game_duration > 10:
        game_duration = 4
    minutes = game_duration * 60
    
    if game_duration > 3.5:
        challenge = True
        minutes -= 30
    else:
        challenge = False
        minutes -= 10
    
    total_puzzles = round(minutes/10)
    world.location_count = total_puzzles
    total_regions = min([7, int(total_puzzles/5)])
    # print(total_puzzles, total_regions)

    required_keys = round(total_puzzles/10) * 2
    total_keys = round((100+(get_option_value(multiworld, player, "extra_keys") or 50)) * required_keys / 100)
    
    victory_key = next(i for i in item_pool if i.name == "Victory Key")
    puzzle_skip = next(i for i in item_pool if i.name == "Puzzle Skip")
    reveal_time = next(i for i in item_pool if i.name == "Reveal Puzzle Times")
    for i in range(1, total_keys):
        item_pool.append(copy(victory_key))

    regions_order = ["Positional Sudoku", "Comparison Sudoku", "Parity Sudoku", "Summation Sudoku", "Variant Sudoku", "Multi-Rule Sudoku"]
    random.shuffle(regions_order)
    regions_order = ["Classic Sudoku"] + regions_order
    
    items_to_remove = []
    
    for i in range(total_regions, 6):
        key_name = regions_order[i].split(" ")[0]+" Key"
        items_to_remove.append(next(i for i in item_pool if i.name == key_name))
    
    traps = int(total_puzzles/10)
    for item in item_pool:
        if "Extra Puzzle" in item.name:
            if int(item.name.split(" ")[2]) > traps:
                items_to_remove.append(item)
        
    for i in items_to_remove:
        item_pool.remove(i)
    
    filler = int((total_puzzles - len(item_pool) - 3)/4)
    
    regions = {r: {"count": (int(total_puzzles/total_regions) if i < total_regions else 0)} for i, r in enumerate(regions_order)}
    cur_rgn = 0
    while sum([r['count'] for r in regions.values()]) < total_puzzles:
        regions[regions_order[cur_rgn]]['count'] += 1
        cur_rgn += 1
        cur_rgn %= total_regions
    #"place_item": ["Key X"]
    
    for i, region in enumerate(multiworld.regions):
        if region.player != player:
            continue
        if region.name == "Victory":
            # print(region.locations)
            locations_to_keep = ["__Manual Game Complete__", f"Required Keys: {required_keys}"]
            possible_victories = [l.name for l in region.locations if "GAS Leak" in l.name]
            victory_puzzle = random.choice(possible_victories)
            locations_to_keep.append(victory_puzzle)
        else:
            loc_names = [l.name for l in region.locations]
            random.shuffle(loc_names)
            try:
                locations_to_keep = loc_names[:regions[region.name]['count']]
            except:
                continue
        for location in list(region.locations):
            if location.name not in locations_to_keep:
                region.locations.remove(location)
        # print(region.locations)
    victory1_item = next(i for i in item_pool if i.name == "Victory 1")
    victory1_location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == f"Required Keys: {required_keys}")
    victory1_location.place_locked_item(victory1_item)
    victory2_item = next(i for i in item_pool if i.name == "Victory 2")
    victory2_location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == victory_puzzle)
    victory2_location.place_locked_item(victory2_item)
    item_pool.remove(victory1_item)
    item_pool.remove(victory2_item)
    
    total_locations = sum([len(r.locations) for r in multiworld.regions if r.player == player])
    while len(item_pool) + 3 >= total_locations:
        item = next(i for i in item_pool if i.classification == 0b0010)
        item_pool.remove(item)
    filler = int((total_locations - len(item_pool) - 3) / 4)
    for i in range(1, filler):
        if len(item_pool) + 3 < total_locations:
            item_pool.append(copy(puzzle_skip))
    for i in range(1, filler*2):
        if len(item_pool) + 3 < total_locations:
            item_pool.append(copy(reveal_time))

    # # shuffle the character item names and pull a subset with a maximum for the option we provided
    # character_names = [name for name in world.item_names]
    # random.shuffle(character_names)
    # character_names = character_names[0:total_characters]

    # # remove any items that have been added that don't have those item names
    # item_pool = [item for item in item_pool if item.name in character_names]
    
    # # remove any locations that have been added that aren't for those items
    # world.location_id_to_name = {id: name for (id, name) in world.location_id_to_name.items() if name.replace("Beat the Game - ", "") in character_names}
    # world.location_name_to_id = {name: id for (id, name) in world.location_id_to_name.items()}
    # world.location_names = world.location_name_to_id.keys()

    # # remove the locations above from the multiworld as well
    # multiworld.clear_location_cache()
    
    # for region in multiworld.regions:
    #     locations_to_remove_from_region = []

    #     for location in region.locations:
    #         if location.name.replace("Beat the Game - ", "") not in character_names and location.player == player:
    #             locations_to_remove_from_region.append(location)

    #     for location in locations_to_remove_from_region:
    #         egion.locations.remove(location)
                
    # # modify the victory requirements to only include items that are in the item names list
    # victory_location = multiworld.get_location("__Manual Game Complete__", player)
    # victory_location.access_rule = lambda state, items=character_names, p=player: state.has_all(items, p)

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