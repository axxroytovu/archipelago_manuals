import json
import tkinter as tk
from tkinter import filedialog
import numpy as np

def open_file():
    """Opens a file dialog and returns the selected file path."""
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename()  # Open the file dialog
    return file_path
    if file_path:
        print("Selected file:", file_path)
    else:
        print("No file selected")

class Region():
    def __init__(self, name):
        self.name = name
        self.sections = []
        self.x = []
        self.y = []
        self.map = ""
    
    def add_loc(self, location, main=False):
        self.sections.append(location["name"])
        if location.get("map_link", False):
            return
        if main:
            self.x.append(location["main_coord"][0])
            self.y.append(location["main_coord"][1])
            self.map = "world_map"
        else:
            self.x.append(location["local_coord"][0])
            self.y.append(location["local_coord"][1])
            self.map = location["map"]
    
    def toJSON(self):
        return {
            "name": self.name,
            "sections": [{"name": s} for s in self.sections],
            "map_locations": [
                {
                    "map": self.map,
                    "x": int(np.mean(self.x)),
                    "y": int(np.mean(self.y))
                }
            ]
        }

class Locations():
    def __init__(self):
        self.regions = {}
    
    def add_loc(self, location):
        if ("map" not in location) and ("map_link" not in location):
            return
        categories = set(location.get("category", []))
        categories -= {"Hobson's Notes", "Gordos", "Treasure Pods"}
        main_map_region = categories.pop()
        if main_map_region not in self.regions:
            self.regions[main_map_region] = Region(main_map_region)
        self.regions[main_map_region].add_loc(location, main=True)
        if location.get("map_link", False):
            if location["map_link"] not in self.regions:
                self.regions[location["map_link"]] = Region(location["map_link"])
            self.regions[location["map_link"]].add_loc(location)
        else:
            if location["name"] not in self.regions:
                self.regions[location["name"]] = Region(location["name"])
            self.regions[location["name"]].add_loc(location)
    
    def toJSON(self):
        return {
            "name": "World Map",
            "children": [r.toJSON() for r in self.regions.values()]
        }

locations_file = open_file()

with open(locations_file, 'r') as locfile:
    data = json.load(locfile)

if isinstance(data, dict):
    data = data["data"]

locat_database = Locations()

for loc in data:
    locat_database.add_loc(loc)

with open("locations.json", "w") as outfile:
    json.dump([locat_database.toJSON()], outfile, indent=4)
