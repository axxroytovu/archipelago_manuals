import yaml
import numpy as np
import json

with open("lucubrate.yaml", 'r') as config_file:
    y_data = yaml.safe_load(config_file)

j_items = []
j_locations = []
j_game = []

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
            "category": [task.get("category", "Reading")] + ["Starting"] * task.get("Starting", False),
            "progression": True,
            "count": item_count
        })
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
            "name": f"|Progressive {practice_name}:{item_count}|",
            "category": [task.get("category", "Practice")] + ["Starting"] * task.get("Starting", False),
            "progression": True,
            "count": item_count
        })
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
                "category": [task.get("category", task["name"])] + ["Starting"] * task.get("Starting", False),
                "progression": True,
                "count": cpi
            })
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
            "category": [task.get("category", "Workout")] + ["Starting"] * task.get("Starting", False),
            "count": task["repetitions"],
            "progression": True
        })
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
            "category": [task.get("category", "Projects")] + ["Starting"] * task.get("Starting", False),
            "count": max_checks,
            "progression": True
        })
               
print(json.dumps(j_locations, indent=2))
print(json.dumps(j_items, indent=2)) 
