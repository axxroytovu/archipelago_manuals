import json
from ..Helpers import load_data_file

# called after the game.json file has been loaded
def after_load_game_file(game_table: dict) -> dict:
    return game_table
# called after the items.json file has been loaded, before any item loading or processing has occurred
# if you need access to the items after processing to add ids, etc., you should use the hooks in World.py
def after_load_item_file(item_table: list) -> list:
    recipes = load_data_file("recipes.json")
    starting_items = set()
    valid_items = set()
    methods = set()
    for recipe in recipes.values():
        valid_items = valid_items.union(recipe["ingredients"])
        methods.add(recipe["preparation"])
        if recipe["preparation"] == "Straight":
            starting_items.add(recipe["ingredients"][0])
    for item_name in sorted(list(valid_items)):
        item_table.append({
            "name": item_name,
            "category": ["Ingredients"] + (["Starting"] if item_name in starting_items else []),
            "progression": True
        })
    for method in sorted(list(methods)):
        item_table.append({
            "name": method,
            "category": ["Preparations"],
            "progression": True
        })
    return item_table

# NOTE: Progressive items are not currently supported in Manual. Once they are,
#       this hook will provide the ability to meaningfully change those.
def after_load_progressive_item_file(progressive_item_table: list) -> list:
    return progressive_item_table

# called after the locations.json file has been loaded, before any location loading or processing has occurred
# if you need access to the locations after processing to add ids, etc., you should use the hooks in World.py
def after_load_location_file(location_table: list) -> list:
    recipes = load_data_file("recipes.json")
    for loc_name, loc_data in recipes.items():
        location_table.append({
            "name": loc_name + " - 0",
            "category": [loc_data["preparation"]],
            "requires": f"|{loc_data['preparation']}| and |" + "| and |".join(loc_data["ingredients"]) + "|",
            "itemset": [loc_data["preparation"]] + loc_data["ingredients"]
        })
        location_table.append({
            "name": loc_name + " - 1",
            "category": [loc_data["preparation"]],
            "requires": f"|{loc_data['preparation']}| and |" + "| and |".join(loc_data["ingredients"]) + "|",
            "itemset": [loc_data["preparation"]] + loc_data["ingredients"]
        })
    return location_table

# called after the locations.json file has been loaded, before any location loading or processing has occurred
# if you need access to the locations after processing to add ids, etc., you should use the hooks in World.py
def after_load_region_file(region_table: dict) -> dict:
    return region_table

# called after the categories.json file has been loaded
def after_load_category_file(category_table: dict) -> dict:
    return category_table

# called after the categories.json file has been loaded
def after_load_option_file(option_table: dict) -> dict:
    # option_table["core"] is the dictionary of modification of existing options
    # option_table["user"] is the dictionary of custom options
    return option_table

# called after the meta.json file has been loaded and just before the properties of the apworld are defined. You can use this hook to change what is displayed on the webhost
# for more info check https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/world%20api.md#webworld-class
def after_load_meta_file(meta_table: dict) -> dict:
    return meta_table

# called when an external tool (eg Universal Tracker) ask for slot data to be read
# use this if you want to restore more data
# return True if you want to trigger a regeneration if you changed anything
def hook_interpret_slot_data(world, player: int, slot_data: dict[str, any]) -> dict | bool:
    return False
