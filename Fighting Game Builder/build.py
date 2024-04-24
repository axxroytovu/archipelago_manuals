import json
import logging
import os
import sys
import shutil
import zipfile
from pathlib import Path

import yaml

CURRENT_VERSION = 1
scriptdir = Path(__file__).parent
tempfolder = scriptdir / '.temp'
system_encoding = sys.getdefaultencoding()

logger = logging.getLogger(scriptdir.name)
logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
if os.path.exists(tempfolder):
    shutil.rmtree(tempfolder)


logger.info("Generating Manual AP Worlds:")

for file in scriptdir.glob("*.yaml"):
    with open(file, 'r', encoding=system_encoding) as config_file:
        y_data = yaml.safe_load(config_file)
    # explicit compatibility check
    if 'template_version' not in y_data or y_data['template_version'] < CURRENT_VERSION:
        # expected skips
        logger.debug("Skipping %s...", file.name)
        continue
    # malformed yaml root check, unexpected skips
    if not all(key in y_data for key in ['meta', 'game_modes']):
        raise ValueError(f"Missing/unsupported root keys in {file.name}")
    logger.info("Processing %s...", file.name)

    j_items = []
    j_locations = []
    j_game = []
    starting_items = []

    c_name = y_data['meta'].get("character_name", "Character")

    # build each game type
    for mode in y_data["game_modes"]:
        mode_name = mode.get('name', 'All')
        if "type" not in mode:
            raise ValueError(f"Game Mode {mode_name} does not have an associated type")
        elif mode["type"] == "character-based":
            j_items.append({
                "name": mode_name,
                "category": ["Game Modes"],
                "progression": True,
                "count": 1
            })
            if mode.get("starting", False):
                starting_items.append({"items": [mode_name]})
                if "characters" in mode:
                    if "starting_characters" in mode:
                        if isinstance(mode["starting_characters"], list):
                            starting_items.append({
                                "items": [f"{mode_name} - {char}" for char in mode['starting_characters']]
                            })
                        elif isinstance(mode["starting_characters"], int):
                            starting_items.append({
                                "item_categories": [f"{mode_name} {c_name}"],
                                "random": mode['starting_characters']
                            })
                    else:
                        starting_items.append({
                            "item_categories": [f"{mode_name} {c_name}"],
                            "random": 1
                        })

            match_name = mode.get("match_name", "match")
            if "characters" in mode:
                characters = [f"{mode_name} - {char}" for char in mode['characters']]
                for char in characters:
                    j_items.append({
                        "name": char,
                        "category": [f"{mode_name} {c_name}"],
                        "progression": True,
                        "count": 1
                    })
            elif "characters" in y_data:
                characters = y_data['characters']
            else:
                raise ValueError(f"Character set not defined for mode {mode_name}")
            for char in characters:
                for i in range(mode.get("victory_count", 1)):
                    j_locations.append({
                        "name": f"{char} {match_name} {i+1}",
                        "category": [mode_name],
                        "requires": f"|{mode_name}| AND |{char}|"
                    })
        elif mode["type"] == "score-based":
            j_items.append({
                "name": mode_name,
                "category": ["Game Modes"],
                "progression": True,
                "count": 1
            })
            if mode.get("starting", False):
                starting_items.append({"items": [mode_name]})
            bp = mode.get("breakpoint", 1)
            for score in range(0, mode["max_score"], bp):
                percent = int(100 * score/mode["max_score"])
                if "characters" in y_data and percent:
                    j_locations.append({
                        "name": f"{mode_name} - Reach score {score+bp}",
                        "category": [mode_name],
                        "requires": f"|{mode_name}| AND |@{c_name}:{percent}%|"
                    })
                else:
                    j_locations.append({
                        "name": f"{mode_name} - Reach score {score+bp}",
                        "category": [mode_name],
                        "requires": f"|{mode_name}|"
                    })
        else:
            raise ValueError(f"Game Mode {mode_name} uses an invalid mode type")
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
    ofile = next(scriptdir.glob("*stable*.apworld"))
    ofolder = tempfolder / ofile.stem

    logger.debug(json.dumps(j_items, indent=2))
    logger.debug(json.dumps(j_locations, indent=2))

    with zipfile.ZipFile(ofile, "r") as zfile:
        zfile.extractall(tempfolder)

    with open(ofolder/'data'/'items.json', "w", encoding=system_encoding) as item_file:
        json.dump(j_items, item_file, indent=2)

    with open(ofolder/'data'/'locations.json', "w", encoding=system_encoding) as location_file:
        json.dump(j_locations, location_file, indent=2)

    with open(ofolder/'data'/'regions.json', "w", encoding=system_encoding) as region_file:
        json.dump(dict(), region_file)

    with open(ofolder/'data'/'game.json', "w", encoding=system_encoding) as game_file:
        json.dump({
            "game": y_data['meta']['game_name'],
            "creator": y_data["meta"]["player_name"],
            "filler_item_name": y_data["meta"].get("filler_name", "Nothing"),
            "starting_items": starting_items
        }, game_file, indent=2)

    finalpath = tempfolder / Path(gamename.lower()+'.apworld')

    shutil.make_archive(finalpath, 'zip', root_dir=tempfolder)
    shutil.move(finalpath.with_suffix(finalpath.suffix + '.zip'), scriptdir / finalpath.name)
    shutil.rmtree(tempfolder / ofile.stem)

    with open(gamename+".yaml", "w", encoding=system_encoding) as yfile:
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
    logger.info("%s completed with %d locations and %d items.",gamename, location_count, item_count)
logger.info("All valid files completed.")
