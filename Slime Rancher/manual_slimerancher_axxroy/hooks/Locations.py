from itertools import combinations
# called after the locations.json has been imported, but before ids, etc. have been assigned
# if you need access to the locations after processing to add ids, etc., you should use the hooks in World.py
def before_location_table_processed(location_table: list) -> list:
    for a, b in combinations(["pink", "tabby", "phosphor", "honey", "hunter", "quantum", "dervish", "tangle", "rock", "rad", "boom", "crystal", "mosaic"]):
        location_table.append({
            "name": f"Ranch a {a}-{b} largo",
            "category": ["Ranchsanity"],
            "requires": f"{{slime({a})}} AND {{slime({b})}}"
        })
    for a in ["puddle", "fire"]:
        location_table.append({
            "name": f"Ranch a {a} slime",
            "category": ["Ranchsanity"],
            "requires": f"{{slime({a})}}"
        })
    return location_table
