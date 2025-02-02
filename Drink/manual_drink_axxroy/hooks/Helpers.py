from typing import Optional, TYPE_CHECKING
from BaseClasses import MultiWorld, Item, Location

if TYPE_CHECKING:
    from ..Items import ManualItem
    from ..Locations import ManualLocation

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the category, False to disable it, or None to use the default behavior
def before_is_category_enabled(multiworld: MultiWorld, player: int, category_name: str) -> Optional[bool]:
    return None

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the item, False to disable it, or None to use the default behavior
def before_is_item_enabled(multiworld: MultiWorld, player: int, item: "ManualItem") -> Optional[bool]:
    valid_items = multiworld.worlds[player].options.ingredients.value
    valid_process = multiworld.worlds[player].options.processes.value
    valid_items.union(valid_process)
    valid_items.union(["Hydrate!", "Shot!", "Straight"])
    print(valid_items)
    return item["name"] in valid_items

# Use this if you want to override the default behavior of is_option_enabled
# Return True to enable the location, False to disable it, or None to use the default behavior
def before_is_location_enabled(multiworld: MultiWorld, player: int, location: "ManualLocation") -> Optional[bool]:
    valid_items = multiworld.worlds[player].options.ingredients.value
    valid_process = multiworld.worlds[player].options.processes.value
    valid_items.union(valid_process)
    valid_items.union(["Straight"])
    print(valid_items)
    return all([item in valid_items for item in location.get("itemset", {})])
