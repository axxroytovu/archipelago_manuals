import yaml
import numpy as np
import json
import zipfile
import os
import shutil
from pathlib import Path

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

for file in Path(".").glob("*.yaml"):
    with open(file, 'r') as config_file:
        y_data = yaml.safe_load(config_file)
    if 'meta' not in y_data or 'game_modes' not in y_data:
        continue
    
    j_items = []
    j_locations = []
    j_game = []
    starting_items = []
    

    c_name = y_data['meta'].get("character_name", "Character")
    
    # build each game type
    for mode in y_data["game_modes"]:
        if "type" not in mode:
            raise ValueError(f"Game Mode {mode['name']} does not have an associated type")
        elif mode["type"] == "character-based":
            j_items.append({
                "name": mode["name"],
                "category": ["Game Modes"],
                "progression": True,
                "count": 1
            })
            if mode.get("starting", False):
                starting_items.append({"items": [mode["name"]]})
                if "characters" in mode:
                    if "starting_characters" in mode:
                        if isinstance(mode["starting_characters"], list):
                            starting_items.append({
                                "items": [f"{mode['name']} - {char}" for char in mode['starting_characters']]
                            })
                        elif isinstance(mode["starting_characters"], int):
                            starting_items.append({
                                "item_categories": [f"{mode['name']} {c_name}"],
                                "random": mode['starting_characters']
                            })
                    else:
                        starting_items.append({
                            "item_categories": [f"{mode['name']} {c_name}"],
                            "random": 1
                        })
                            
            match_name = mode.get("match_name", "match")
            if "characters" in mode:
                characters = [f"{mode['name']} - {char}" for char in mode['characters']]
                for char in characters:
                    j_items.append({
                        "name": char,
                        "category": [f"{mode['name']} {c_name}"],
                        "progression": True,
                        "count": 1
                    })
            elif "characters" in y_data:
                characters = y_data['characters']
            else:
                raise ValueError(f"Character set not defined for mode {mode['name']}")
            for char in characters:
                for i in range(mode.get("victory_count", 1)):
                    j_locations.append({
                        "name": f"{char} {match_name} {i+1}",
                        "category": [mode['name']],
                        "requires": f"|{mode['name']}| AND |{char}|"
                    })
        elif mode["type"] == "score-based":
            j_items.append({
                "name": mode["name"],
                "category": ["Game Modes"],
                "progression": True,
                "count": 1
            })
            if mode.get("starting", False):
                starting_items.append({"items": [mode["name"]]})
            bp = mode.get("breakpoint", 1)
            for score in range(0, mode["max_score"], bp):
                percent = int(100 * score/mode["max_score"])
                if "characters" in y_data and percent:
                    j_locations.append({
                        "name": f"{mode['name']} - Reach score {score+bp}",
                        "category": [mode['name']],
                        "requires": f"|{mode['name']}| AND |@{c_name}:{percent}%|"
                    })
                else:
                    j_locations.append({
                        "name": f"{mode['name']} - Reach score {score+bp}",
                        "category": [mode['name']],
                        "requires": f"|{mode['name']}|"
                    })
        else:
            raise ValueError(f"Game Mode {mode['name']} uses an invalid mode type")
    if "characters" in y_data:
        for char in y_data["characters"]:
            j_items.append({
                "name": char,
                "category": [c_name],
                "progression": True,
                "count": 1
            })
        if "starting_characters" in y_data["meta"]:
            if isinstance(y_data["meta"]["starting_characters"], list):
                starting_items.append({"items": y_data["meta"]["starting_characters"]})
            elif isinstance(y_data["meta"]["starting_characters"], int): 
                starting_items.append({
                    "item_categories": [c_name],
                    "random": y_data["meta"]["starting_characters"]
                })
        else:
            starting_items.append({
                "item_categories": [c_name],
                "random": 1
            })
                   
    location_count = len(j_locations)
    item_count = sum([i.get("count", 1) for i in j_items]) 
    print(location_count, item_count)
    
    victory_count = int(location_count - item_count)//2
    macguffin_name = y_data["meta"].get("victory_macguffin_name", "Trophy")
    j_locations.append({
        "name": "Victory",
        "category": ["Victory"],
        "requires": "|Victory|",
        "victory": True
    })
    j_locations.append({
        "name": f"Collect {victory_count} {macguffin_name}",
        "category": ["Victory"],
        "requires": f"|{macguffin_name}:{victory_count}|",
        "place_item": ["Victory"]
    })
    j_items.append({
        "name": "Victory",
        "category": ["Victory"],
        "count": 1,
        "progression": True
    })
    j_items.append({
        "name": macguffin_name,
        "category": ["Victory"],
        "count": victory_count,
        "progression": True
    })
    
    gamename = f"Manual_{y_data['meta']['game_name']}_{y_data['meta']['player_name']}"
    
    ofile = next(f for f in os.listdir(".") if ".apworld" in f and "stable" in f)
    ofolder = ofile.split(".")[0]
    
    #print(json.dumps(j_items, indent=2))
    #print(json.dumps(j_locations, indent=2))
    
    with zipfile.ZipFile(ofile, "r") as zfile:
        zfile.extractall("")
    
    with open(ofolder+"/data/items.json", "w") as item_file:
        json.dump(j_items, item_file, indent=2)
    
    with open(ofolder+"/data/locations.json", "w") as location_file:
        json.dump(j_locations, location_file, indent=2)
    
    with open(ofolder+"/data/regions.json", "w") as region_file:
        json.dump(dict(), region_file)
    
    with open(ofolder+"/data/game.json", "w") as game_file:
        json.dump({
            "game": y_data['meta']['game_name'],
            "creator": y_data["meta"]["player_name"],
            "filler_item_name": y_data["meta"].get("filler_name", "Nothing"),
            "starting_items": starting_items
        }, game_file, indent=2)
    
    os.rename(ofolder, gamename.lower())
    
    with zipfile.ZipFile(gamename.lower()+".apworld", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipdir(gamename.lower()+"/", zipf)
    
    shutil.rmtree(gamename.lower())
    
    with open(gamename+".yaml", "w") as yfile:
        yaml.dump({
            "name": y_data['meta']['player_name'],
            "description": "Built with Axxroy's Fighting Game Builder",
            "game": gamename,
            gamename: {
                "progression_balancing": 0,
                "accessibility": "items"
            }
        },
        yfile)
