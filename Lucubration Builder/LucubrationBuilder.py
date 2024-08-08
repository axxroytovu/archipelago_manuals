import yaml
import json
import zipfile
import logging
import shutil
import math
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import sys

root = tk.Tk()
root.withdraw()

CURRENT_VERSION = 1
scriptdir = Path(filedialog.askdirectory(title="Directory to output files"))
tempfolder = scriptdir / ".temp"
system_encoding = sys.getdefaultencoding()

logger = logging.getLogger(scriptdir.name)
logging.basicConfig(level=logging.INFO, format="%(name)s - %(message)s")
shutil.rmtree(tempfolder, ignore_errors=True)

logger.info("Generating Manual AP Worlds:")

file = Path(filedialog.askopenfilename(filetypes=[("YAML", "*.yaml")], title="YAML input option file"))
with open(file, 'r', encoding=system_encoding) as config_file:
    y_data = yaml.safe_load(config_file)

if 'template_version' not in y_data or y_data['template_version'] < CURRENT_VERSION:
    # expected skips
    logger.debug("Skipping %s. Incompatible template version.", file.name)
    quit()

if not all(key in y_data for key in ["tasks", "meta"]):
    raise ValueError(f"Missing/unsupported root keys in {file.name}")
logger.info("Processing %s...", file.name)

j_items = []
j_locations = []
j_game = []
starting_items = []

# build each project type
for task in y_data["tasks"]:
    if "type" not in task:
        raise Exception("Task does not have an associated type")
    if task["type"] == "book":
        start = task.get("start_chapter", 1)
        item_count = 0
        book_name = task["name"]
        for i in range(start, task["end_chapter"] + 1):
            if (i-start) % 2 == 0:
                item_count += 1
            j_locations.append({
                "name": f"{book_name} Chapter {i}",
                "category": [task.get("category", "Reading")],
                "requires": f"|Progressive {book_name}:{item_count}|"
            })
        j_items.append({
            "name": f"Progressive {book_name}",
            "category": [task.get("category", "Reading")],
            "progression": True,
            "count": item_count
        })
        if task.get("starting", False):
            starting_items.append(f"Progressive {book_name}")
    elif task["type"] == "practice-general":
        if "hours" in task:
            checks = task["hours"] * y_data["meta"]["checks_per_hour"]
        else:
            checks = task["checks"]
        item_count = 0
        practice_name = task["name"]
        for i in range(checks):
            if i%2 == 0:
                item_count += 1
            j_locations.append({
                "name": f"{practice_name} Practice {i+1}",
                "category": [task.get("category", "Practice")],
                "requires": f"|Progressive {practice_name}:{item_count}|"
            })
        j_items.append({
            "name": f"Progressive {practice_name}",
            "category": [task.get("category", "Practice")],
            "progression": True,
            "count": item_count
        })
        if task.get("starting", False):
            starting_items.append(f"Progressive {practice_name}")
    elif task["type"] == "practice-specific":
        if "hours_per_item" in task:
            cpi = task["hours_per_item"] * y_data["meta"]["checks_per_hour"]
        else:
            cpi = task["checks_per_item"]
        for i_name in task["items"]:
            if math.ceil(cpi/2) == 1:
                final_name = i_name
            else:
                final_name = f"Progressive {i_name}"
            for i in range(cpi):
                req = math.ceil((i+1)/2)
                j_locations.append({
                    "name": f"{i_name} {i+1}",
                    "category": [task.get("category", task["name"])],
                    "requires": f"|{final_name}:{req}|"
                })
            
            j_items.append({
                "name": final_name,
                "category": [task.get("category", task["name"])],
                "progression": True,
                "count": math.ceil(cpi/2)
            })
            if task.get("starting", False):
                starting_items.append(final_name)
    elif task["type"] == "workout":
        w_name = task["name"]
        for i in range(task["repetitions"]):
            for set_name in task["sets"]:
                j_locations.append({
                    "name": f"{w_name} {i+1} - {set_name}",
                    "category": [task.get("category", "Workout")],
                    "requires": f"|Progressive {w_name}:{i+1}|"
                })
        j_items.append({
            "name": f"Progressive {w_name}",
            "category": [task.get("category", "Workout")],
            "count": task["repetitions"],
            "progression": True
        })
        if task.get("starting", False):
            starting_items.append(f"Progressive {w_name}")
    elif task["type"] == "tied-projects":
        max_checks = 0
        item_name = task["name"]
        for i in range(len(task["projects"])):
            if "hours" in task["projects"][i]:
                checks = task["projects"][i]["hours"] * y_data["meta"]["checks_per_hour"]
                task["projects"][i]["checks"] = checks
                max_checks = max(max_checks, checks)
            else:
                max_checks = max(max_checks, task["projects"][i]["checks"])
        for project in task["projects"]:
            p_name = project["name"]
            breakpoints = range(1, max_checks+1, max_checks//project["checks"])
            for i in range(project["checks"]):
                j_locations.append({
                    "name": f"{p_name} {i+1}",
                    "category": [task.get("category", "Projects")],
                    "requires": f"|Progressive {item_name}:{breakpoints[i]}|"
                })
        j_items.append({
            "name": f"Progressive {item_name}",
            "category": [task.get("category", "Projects")],
            "count": max_checks,
            "progression": True
        })
        if task.get("starting", False):
            starting_items.append(f"Progressive {item_name}")
               
location_count = len(j_locations)
item_count = sum([i.get("count", 1) for i in j_items]) 
#print(location_count, item_count)
starting_items_count = sum([i.get("count", 1) for i in j_items if i["name"] in starting_items])
if starting_items_count == 0:
    starting_items = [i["name"] for i in j_items]
elif starting_items_count < 5:
    raise ValueError("Not enough starting items defined")

victory_count = int(location_count - item_count)//2
j_locations.append({
    "name": "Victory",
    "category": ["Victory"],
    "requires": "|Victory|",
    "victory": True
})
j_locations.append({
    "name": f"Collect {victory_count} Productivity",
    "category": ["Victory"],
    "requires": f"|Productivity:{victory_count}|",
    "place_item": ["Victory"]
})
j_items.append({
    "name": "Victory",
    "category": ["Victory"],
    "count": 1,
    "progression": True
})
j_items.append({
    "name": "Productivity",
    "category": ["Victory"],
    "count": victory_count,
    "progression_skip_balancing": True
})

gamename = f"Manual_Tasks_{y_data['meta']['player_name']}"

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
        "game": "Tasks",
        "creator": y_data["meta"]["player_name"],
        "filler_item_name": "Extrinsic Motivation",
        "starting_items": [
            {
                "items": starting_items,
                "random": 5
            }
        ]
    }, game_file, indent=2)

finalpath = tempfolder / Path(gamename.lower()+'.apworld')
shutil.move(tempfolder / ofile.stem, tempfolder / finalpath.stem)
shutil.make_archive(str(finalpath), 'zip', root_dir= tempfolder, base_dir= finalpath.stem)
shutil.move(finalpath.with_suffix(finalpath.suffix + '.zip'), scriptdir / finalpath.name)
shutil.rmtree(tempfolder / finalpath.stem)

with open(scriptdir / Path(gamename).with_suffix(".yaml"), "w", encoding=system_encoding) as yfile:
    yaml.dump({
        "name": y_data['meta']['player_name'],
        "description": "Built with Axxroy's Lucubration Builder",
        "game": gamename,
        gamename: {
            "progression_balancing": 0,
            "accessibility": "items"
        }
    },
    yfile)
logger.info("%s completed with %d locations and %d items.",gamename, location_count, item_count)
shutil.rmtree(tempfolder, ignore_errors=True)
logger.info("All valid files completed.")
