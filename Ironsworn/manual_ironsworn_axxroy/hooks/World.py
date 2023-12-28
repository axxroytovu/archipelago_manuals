# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld

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
    valid_games = get_option_value(multiworld, player, "games_override") or set()
    override = "Everything" not in valid_games
    valid_games.add("NONE")
    if valid_games == {"NONE"}:
        for w in multiworld.worlds.values():
            valid_games.add(w.game)
    # print(valid_games)
    valid_games.add("Manual_Ironsworn_Axxroy")
    items_to_remove = []
    assets = []
    current_assets = [i.name for i in multiworld.precollected_items[player]]
    traps = []
    quests = []
    items = []
    dungeons = []
    relics = []
    for i in item_pool:
        idata = world.item_name_to_item[i.name]
        #print(idata)
        if "Starting" in idata.get("category", []):
            items_to_remove.append(i)
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
    world.random.shuffle(traps)
    world.random.shuffle(quests)
    world.random.shuffle(items)
    world.random.shuffle(relics)
    world.random.shuffle(dungeons)
    asset_index = 0
    while len(current_assets) < 6:
        if assets[asset_index].name.split(" - ")[0] in current_assets:
            asset_index += 1
        else:
            asset = assets.pop(asset_index)
            current_assets.append(asset.name.split(" - ")[0])
    items_to_remove += assets
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
        multiworld.clear_location_cache()
    
    for i in items_to_remove:
        item_pool.remove(i)

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