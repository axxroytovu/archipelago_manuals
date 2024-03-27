import yaml
import json
import sys
from pathlib import Path


class item:
    short_game = {
        "Manual_Ironsworn_Axxroy": "Core",
        "Pokemon Red and Blue": "Pkmn R/B",
        "Manual_FFXIV_Silasary": "FFXIV",
        "The Legend of Zelda": "TLoZ",
        "Stardew Valley": "Stardew",
        "Manual_PLA_Miro": "Pkmn LA",
        "Manual_MHRiseHub_Axxroy": "MH Rise"
    }
    
    def __init__(self, name, category=[], count="1", game="Starting", progression=False,
                 useful=False, filler=False, trap=False, yamlmode=False, description="",
                 mode=None):
        self.category = list(category)
        self.count = int(count)
        self.game = game
        if progression:
            self.mode = "progression"
        elif useful:
            self.mode = "useful"
        elif trap:
            self.mode = "trap"
        else:
            self.mode = "filler"
        self.description = description
            
        if not yamlmode:
            if len({"Asset", "Trap"}.intersection(self.category)):
                if "Starting" in self.category:
                    self.name = name
                else:
                    self.name, _, self.description = name.split(" - ")
            elif len({"Dungeon", "Items", "Relic"}.intersection(self.category)):
                _, self.name = name.split(" - ")
            elif "Quest" in self.category:
                self.name = name.split(" ")[-1]
            else:
                self.name = name
        else:
            self.name = name
            self.mode = mode
                
    def full_name(self):
        sg = self.short_game.get(self.game, self.game)
        if len({"Asset", "Trap"}.intersection(self.category)):
            if "Starting" in self.category:
                return self.name
            else:
                return f"{self.name} - {sg} - {self.description}"
        elif len({"Dungeon", "Items", "Relic"}.intersection(self.category)):
            return f"{sg} - {self.name}"
        elif "Quest" in self.category:
            return f"{sg} Quest {self.name}"
        else:
            return self.name
    
    def as_dict(self):
        output = {
            "name": self.full_name(),
            "category": self.category,
            "count": str(self.count),
            self.mode: True
        }
        if self.game != "Starting":
            output["game"] = self.game
        return output
        
    def as_yaml(self):
        if self.description:
            output = {"name": self.name, "description": self.description}
        else:
            output = self.name
        if self.category:
            mode = self.category[-1] if self.category[0] == "Starting" else self.category[0]
        else:
            mode = "None"
        return mode, self.game, output
    
    def sortval(self):
        mode = self.category[-1] if self.category[0] == "Starting" else self.category[0]
        return (mode, self.game, self.name, self.description)
        

def load_json(file):
    with open(file, 'r') as json_file:
        data = json.load(json_file)
    return [item(**content) for content in data]

def load_yaml(file):
    modedict = {
        "Asset": "useful",
        "Dungeon": "progression",
        "Items": "filler", 
        "Quest": "progression",
        "Relic": "useful",
        "Trap": "trap"
    }
    with open(file, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)
    item_list = []
    if file.stem == "Quest":
        for game, quest_count in data.items():
            for i in range(quest_count):
                item_list.append(item(
                    yamlmode=True,
                    count=1,
                    category=["Quest"],
                    mode="progression",
                    game=game,
                    name=str(i+1)
                ))
        return item_list
    for game, item_set in data.items():
        for itm in item_set:
            if game == "Starting":
                category = [file.stem, "Starting"]
            else:
                category = [file.stem]
            if isinstance(itm, dict):
                item_list.append(item(
                    yamlmode=True,
                    count=1, 
                    category=category,
                    mode=modedict[file.stem],
                    game=game,
                    **itm
                ))
            else:
                item_list.append(item(
                    yamlmode=True,
                    count=1, 
                    category=category,
                    mode=modedict[file.stem],
                    game=game,
                    name=itm
                ))
    return item_list

if __name__ == "__main__":
    if "-i" in sys.argv:
        item_list = load_json("Items.json")
        yaml_outputs = {}
        for i in item_list:
            m, g, val = i.as_yaml()
            if m not in yaml_outputs:
                yaml_outputs[m] = {}
            if g not in yaml_outputs[m]:
                yaml_outputs[m][g] = []
            yaml_outputs[m][g].append(val)
        for mode, content in yaml_outputs.items():
            if mode in ["None", "Upgrade"]:
                continue
            with open(f"items/{mode}.yaml", "w") as y_file:
                yaml.dump(content, y_file)
    else:
        files = Path("items/").glob("*.yaml")
        item_list = [
            item(name="Asset Upgrade", category=["Upgrade"], count="6", useful=True),
            item(name="Shard of Reality", count="10", progression=True, category=["Victory"])
        ]
        for f in files:
            item_list.extend(load_yaml(f))
        for i in item_list:
            print(i.as_dict())
        item_list.sort(key=lambda x: x.sortval())
        content = [i.as_dict() for i in item_list]
        with open("Items.json", "w") as jfile:
            json.dump(content, jfile, indent=2)
        