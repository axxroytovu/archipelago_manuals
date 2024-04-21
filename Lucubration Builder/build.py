import yaml
import numpy as np
import json
import zipfile
import os
import shutil

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

with open("tasks.yaml", 'r') as config_file:
    y_data = yaml.safe_load(config_file)

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
            for i in range(cpi):
                req = i//2 + 1
                j_locations.append({
                    "name": f"{i_name} {i+1}",
                    "category": [task.get("category", task["name"])],
                    "requires": f"|Progressive {i_name}:{req}|"
                })
            j_items.append({
                "name": f"Progressive {i_name}",
                "category": [task.get("category", task["name"])],
                "progression": True,
                "count": cpi
            })
            if task.get("starting", False):
                starting_items.append(f"Progressive {i_name}")
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
            breakpoints = np.linspace(1, max_checks, project["checks"], dtype="int")
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
    "progression": True
})

gamename = f"Manual_Tasks_{y_data['meta']['player_name']}"

ofile = next(f for f in os.listdir(".") if ".apworld" in f and "stable" in f)
ofolder = ofile.split(".")[0]

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

os.rename(ofolder, gamename.lower())

with zipfile.ZipFile(gamename.lower()+".apworld", "w", zipfile.ZIP_DEFLATED) as zipf:
    zipdir(gamename.lower()+"/", zipf)

shutil.rmtree(gamename.lower())

with open(gamename+".yaml", "w") as yfile:
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
