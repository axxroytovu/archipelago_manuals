import json
import logging
import sys
import shutil
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

import yaml

root = tk.Tk()
root.withdraw()

CURRENT_VERSION = 1
scriptdir = Path(filedialog.askdirectory(title="Directory to output files"))
tempfolder = scriptdir / '.temp'
system_encoding = sys.getdefaultencoding()


logger = logging.getLogger(scriptdir.name)
logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
shutil.rmtree(tempfolder, ignore_errors=True)

logger.info("Generating Manual AP Worlds:")

file = Path(filedialog.askopenfilename(filetypes=[("YAML", "*.yaml")], title="YAML input option file"))
with open(file, 'r', encoding=system_encoding) as config_file:
    y_data = yaml.safe_load(config_file)
# explicit compatibility check
if 'template_version' not in y_data or y_data['template_version'] < CURRENT_VERSION:
    # expected skips
    logger.debug("Skipping %s...", file.name)
    quit()
# malformed yaml root check, unexpected skips
if not all(key in y_data for key in ['meta', 'game_modes']):
    raise ValueError(f"Missing/unsupported root keys in {file.name}")
logger.info("Processing %s...", file.name)

j_items = []
j_locations = []
j_game = []
starting_items = []

game_meta = y_data['meta']
game_name = game_meta["game_name"]
character_alias = game_meta.get("character_alias", "Character")
char_global = {*y_data.get('characters', set())}

start_char_global = game_meta.get("starting_characters", None)
if isinstance(start_char_global, int):
    starting_items.append({
        "item_categories": [character_alias],
        "random": start_char_global
    })
elif isinstance(start_char_global, list):
    start_char_global = set(start_char_global)
    char_global |= start_char_global
    starting_items.append({
        "items": list(start_char_global)
    })
    # parse for global characters
for char in char_global:
    j_items.append({
        "name": char,
        "category": [character_alias],
        "progression": True,
        "count": 1
    })
# build each game type
for mode in y_data["game_modes"]:
    mode_name = mode.get('name')
    mode_type = mode.get('type', None)
    if not mode_type:
        raise ValueError(f"Game Mode {mode_name} does not have an associated type")

    if mode_type == "character-based":
        j_items.append({
            "name": mode_name,
            "category": ["Game Modes"],
            "progression": True,
            "count": 1
            })
        sub_character_alias = mode.get("character_alias", character_alias)
        # if mode is set to starting, add either the specified or a random # of characters to starting
        if mode.get("starting", False):
            start_char_mode = mode.get('starting_characters', None)
            if isinstance(start_char_mode, int):
                starting_items.append({
                "item_categories": [f"{mode_name} {sub_character_alias}"],
                    "random": start_char_mode
                })
            elif isinstance(start_char_mode, list):
                starting_items.append({
                    "items": [f"{mode_name} - {playable}" for playable in set(start_char_mode)]
                })
            elif "starting_characters" not in game_meta:
                if "characters" in mode:
                    starting_items.append({
                        "item_categories": [f"{mode_name} {sub_character_alias}"],
                        "random": 5
                    })
                else:
                    starting_items.append({
                        "item_categories": [character_alias],
                        "random": 5
                    })
            starting_items.append({"items": [mode_name]})

        match_name = mode.get("match_name", "Match")
        # if there are mode specific characters
        mode_characters = {*mode.get("characters", set())}
        # remove duplicates from global characters
        if mode_characters:
            specific_mode_characters = mode_characters - char_global
            global_mode_characters = mode_characters - specific_mode_characters
            char_items = [(char, f"{mode_name} - {char}") for char in specific_mode_characters] +\
                [(char, char) for char in global_mode_characters]
            for char in specific_mode_characters:
                j_items.append({
                    "name": f"{mode_name} - {char}",
                    "category": [f"{mode_name} {sub_character_alias}"],
                    "progression": True,
                    "count": 1
                })
        else:
            char_items = [(char, char) for char in char_global]
        for char, item in char_items:
            for i in range(mode.get("victory_count", 1)):
                j_locations.append({
                    "name": f"{mode_name} {char} {match_name} {i+1}",
                    "category": [mode_name],
                    "requires": f"|{mode_name}| AND |{item}|"
                })
    elif mode_type == "score-based":
        j_items.append({
            "name": mode_name,
            "category": ["Game Modes"],
            "progression": True,
            "count": 1
            })
        if mode.get("starting", False):
            starting_items.append({"items": [mode_name]})
        bp = mode.get("breakpoint", 1)
        max_score = mode["max_score"]
        for score in range(0, max_score, bp):
            percent = int(100 * score/max_score)
            j_locations.append({
                "name": f"{mode_name} - Reach score {min(score+bp, max_score)}",
                "category": [mode_name],
                "requires": f"|{mode_name}|{f' AND |@{character_alias}:{percent}%|' if char_global and percent else ''}"
            })
    elif mode_type == "run-based":
        run_alias = mode.get("run_alias", "Run")
        run_count = mode.get("run_count", 5)
        cpr = mode.get("checks_per_run", 1)
        j_items.append({
            "name": f"One {mode_name} {run_alias}",
            "category": ["Game Modes"],
            "progression": True,
            "count": run_count
            })
        if mode.get("starting", False):
            starting_items.append({"items": [f"One {mode_name} {run_alias}"], "random": min(5, run_count)})
        for run in range(run_count):
            for check in range(cpr):
                j_locations.append({
                    "name": f"{mode_name} - {run_alias} {run+1} - {check+1}",
                    "category": [mode_name],
                    "requires": f"|One {mode_name} {run_alias}:{run+1}|"
                })
    elif mode_type == "story-based":
        chapter_alias = mode.get("chapter_alias", "Chapter")
        chapter_count = mode.get("chapter_count", 5)
        cpc = mode.get("checks_per_chapter", 1)
        j_items.append({
            "name": f"Progressive {mode_name} {chapter_alias}",
            "category": ["Game Modes"],
            "progression": True,
            "count": chapter_count
            })
        if mode.get("starting", False):
            starting_items.append({"items": [f"Progressive {mode_name} {chapter_alias}"], "random": min(5, chapter_count)})
        for chapter in range(chapter_count):
            for check in range(cpc):
                j_locations.append({
                    "name": f"{mode_name} - {chapter_alias} {chapter+1} - {check+1}",
                    "category": [mode_name],
                    "requires": f"|Progressive {mode_name} {chapter_alias}:{chapter+1}|"
                })
    else:
        raise ValueError(f"Game Mode {mode_name} uses an invalid mode type")


location_count = len(j_locations)
item_count = sum([i.get("count", 1) for i in j_items])

victory_count = int(location_count - item_count)//4
macguffin_name = game_meta.get("victory_macguffin_name", "Trophy")
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
    "progression_skip_balancing": True
})

gamename = f"Manual_{game_meta['game_name']}_{game_meta['player_name']}"
ofile = Path(filedialog.askopenfilename(initialfile="*stable*.apworld", filetypes=[("APworld", "*.apworld")], title="Stable APWorld"))
ofolder = tempfolder / ofile.stem

logger.debug(json.dumps(j_items, indent=2))
logger.debug(json.dumps(j_locations, indent=2))

with zipfile.ZipFile(ofile, "r") as zfile:
    zfile.extractall(tempfolder)

with open(ofolder/'data'/'items.json', "w", encoding=system_encoding) as item_file:
    json.dump(j_items, item_file, indent=2, sort_keys=False)

with open(ofolder/'data'/'locations.json', "w", encoding=system_encoding) as location_file:
    json.dump(j_locations, location_file, indent=2, sort_keys=False)

with open(ofolder/'data'/'regions.json', "w", encoding=system_encoding) as region_file:
    json.dump(dict(), region_file)

with open(ofolder/'data'/'game.json', "w", encoding=system_encoding) as game_file:
    json.dump({
        "game": game_meta['game_name'],
        "creator": game_meta["player_name"],
        "filler_item_name": game_meta.get("filler_name", "Nothing"),
        "starting_items": starting_items,
        "death_link": True
    }, game_file, indent=2, sort_keys=False)

finalpath = tempfolder / Path(gamename.lower()+'.apworld')
shutil.move(tempfolder / ofile.stem, tempfolder / finalpath.stem)
shutil.make_archive(str(finalpath), 'zip', root_dir= tempfolder, base_dir= finalpath.stem)
shutil.move(finalpath.with_suffix(finalpath.suffix + '.zip'), scriptdir / finalpath.name)
shutil.rmtree(tempfolder / finalpath.stem)

with open(scriptdir / Path(gamename).with_suffix(".yaml"), "w", encoding=system_encoding) as yfile:
    yaml.dump({
        "name": game_meta['player_name']+"{number}",
        "description": "Built with Axxroy's Fighting Game Builder",
        "game": gamename,
        gamename: {
            "progression_balancing": 0,
            "accessibility": "items",
            "death_link": True
        }
    },
    yfile, sort_keys=False)
logger.info("%s completed with %d locations and %d items.",gamename, location_count, item_count)
shutil.rmtree(tempfolder, ignore_errors=True)
logger.info("All valid files completed.")
