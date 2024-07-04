# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState

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
    # Use this hook to remove locations from the world
    locationNamesToRemove = [] # List of location names

    # Add your code here to calculate which locations to remove

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)
    if hasattr(multiworld, "clear_location_cache"):
        multiworld.clear_location_cache()

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    valid_games = get_option_value(multiworld, player, "games_override") or set()
    override = "Everything" not in valid_games
    valid_games.add("NONE")
    if valid_games == {"NONE"}:
        for w in multiworld.worlds.values():
            valid_games.add(w.game)
    # print(valid_games)
    valid_games.add("Manual_Ironsworn_Axxroy")
    
    duplicate_games = {
        "Manual_PLAlpha_Miro": "Manual_PLA_Miro",
        "TUNIC": "Tunic"
    }
    
    for k, v in duplicate_games.items():
        if k in valid_games:
            valid_games.add(v)

    group_items = set()
    for group in multiworld.groups.values():
        if player not in group["players"]:
            continue
        for item in multiworld.itempool:
            if item.name in group["item_pool"] and item.player in group["players"]:
                group_items.add(item.name)
    
    items_to_remove = []
    assets = []
    current_assets = []
    traps = []
    quests = []
    items = []
    dungeons = []
    relics = []
    starting = []
    for i in item_pool:
        idata = world.item_name_to_item[i.name]
        #print(idata)
        if "Starting" in idata.get("category", []):
            starting.append(i)
        elif override and idata.get("game", "NONE") not in valid_games:
            items_to_remove.append(i)
        elif "Asset" in idata.get("category", []):
            assets.append(i)
        elif "Trap" in idata.get("category", []):
            traps.append(i)
        elif "Quest" in idata.get("category", []):
            quests.append(i)
        elif "Items" in idata.get("category", []):
            items.append(i)
        elif "Dungeon" in idata.get("category", []):
            dungeons.append(i)
        elif "Relic" in idata.get("category", []):
            relics.append(i)
    
    world.random.shuffle(assets)
    assets.sort(key=lambda i: i.name not in group_items)
    world.random.shuffle(traps)
    traps.sort(key=lambda i: i.name not in group_items)
    world.random.shuffle(quests)
    quests.sort(key=lambda i: i.name not in group_items)
    world.random.shuffle(items)
    items.sort(key=lambda i: i.name not in group_items)
    world.random.shuffle(relics)
    relics.sort(key=lambda i: i.name not in group_items)
    world.random.shuffle(dungeons)
    dungeons.sort(key=lambda i: i.name not in group_items)
    world.random.shuffle(starting)
    starting.sort(key=lambda i: i.name not in group_items)
    asset_index = 0
    while len(current_assets) < 3:
        if assets[asset_index].name.split(" - ")[0] in current_assets:
            asset_index += 1
        else:
            asset = assets.pop(asset_index)
            current_assets.append(asset.name.split(" - ")[0])
    starting_index = 0
    while len(current_assets) < 6:
        if starting[starting_index].name not in current_assets:
            multiworld.push_precollected(starting[starting_index])
            current_assets.append(starting[starting_index].name)
        starting_index += 1
    items_to_remove += assets
    items_to_remove += starting
    items_to_remove += traps[3:]
    items_to_remove += quests[5:]
    multiworld.push_precollected(quests[-1])
    items_to_remove += items[10:]
    # print(items_to_remove)
    
    if get_option_value(multiworld, player, "delve") or False:
        items_to_remove += dungeons[4:]
        items_to_remove += relics[4:]
    else:
        items_to_remove += dungeons
        items_to_remove += relics
        for region in multiworld.regions:
            if region.player != player:
                continue
            for location in list(region.locations):
                if "Dungeon" in world.location_name_to_location[location.name].get("category", []):
                    region.locations.remove(location)
        if hasattr(multiworld, "clear_location_cache"):
            multiworld.clear_location_cache()
    
    for i in items_to_remove:
        item_pool.remove(i)
    
    def gfin():
        return multiworld.random.choice([i.name for i in items if i in items_to_remove])

    world.get_filler_item_name = gfin

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # item_pool.remove(item_to_place)

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
