import random
import json
import shutil
import sys
import os
import yaml
from pathlib import Path

seed = random.randrange(sys.maxsize)
rng = random.Random(seed)

with open("data/locations.yaml", 'r') as locations_json:
    locations = yaml.safe_load(locations_json)

duration = float(input("How long do you want your game to last (hours):"))
while duration < 2:
    print("Sudoku is not recommended for sessions of less than 2 hours")
    duration = float(input("How long do you want your game to last (hours):"))
minutes = duration*60
if duration >= 3.5:
    challenge = True
    minutes -= 30
else:
    challenge = False
    minutes -= 10

total_puzzles = round(minutes/10)
total_regions = min([6, int(total_puzzles/5)])
print(f"Generating {total_puzzles} puzzles over {total_regions} regions")

valid_regions = ["Positional Sudoku", "Summation Sudoku", "Parity Sudoku", "Variant Sudoku"]
random.shuffle(valid_regions)
valid_regions = ["Classic Sudoku"] + valid_regions + ["Multi-Rule Sudoku"]

regions = {r: {"count": int(total_puzzles/total_regions)} for r in valid_regions[:total_regions]}
while sum([r['count'] for r in regions.values()]) < total_puzzles:
    i = random.choice(list(regions.keys()))
    if regions[i]['count'] == min([r['count'] for r in regions.values()]):
        regions[i]['count'] += 1

for i in range(total_regions):
    if i == 0:
        regions[valid_regions[i]]['requires'] = []
        regions[valid_regions[i]]['connects_to'] = [valid_regions[i+1]]
    elif i < total_regions-1:
        key_name = valid_regions[i].split(" ")[0] + " Key"
        regions[valid_regions[i]]['requires'] = f"|{key_name}|"
        regions[valid_regions[i]]['connects_to'] = [valid_regions[i+1]]
    else:
        key_name = valid_regions[i].split(" ")[0] + " Key"
        regions[valid_regions[i]]['requires'] = f"|{key_name}|"
        regions[valid_regions[i]]['connects_to'] = []

regions["Classic Sudoku"]["starting"] = True

random.shuffle(locations)

final_locations = []
for loc in locations:
    if loc['region'] in regions and regions[loc["region"]]['count']:
        regions[loc['region']]['count'] -= 1
        final_locations.append(loc)

for i in range(len(final_locations)):
    final_locations[i]['category'] = [final_locations[i]['region']]

if len(final_locations) != total_puzzles:
    raise ValueError(f"Improper number of puzzles: {len(final_locations)} vs {total_puzzles}")

total_keys = round(total_puzzles/9)*3
req_keys = round(total_keys*2/3)

final_locations.append({
    "name": "Victory",
    "region": valid_regions[total_regions-1],
    "victory": True,
    "category": ["Victory"],
    "requires": f"|Victory Key:{req_keys}|"
})

traps = round(total_puzzles/10)

final_items = [{
    "count": total_keys,
    "name": "Victory Key",
    "category": ["Key"],
    "progression": True
}]
for r in regions.values():
    if r['requires']:
        final_items.append({
            "count": 1,
            "name": r['requires'][1:-1],
            "category": ["Key"],
            "progression": True
        })
for i in range(traps):
    p = random.choice(locations)
    while p in final_locations:
        p = random.choice(locations)
    final_items.append({
        "count": 1,
        "name": f"Extra Puzzle: {p['name']}",
        "category": ["Trap"],
        "trap": True
    })
filler = int((total_puzzles - sum([i['count'] for i in final_items]))/4)
final_items.append({
    "name": "Puzzle Skip",
    "count": filler,
    "category": ["Boon"],
    "useful": True
})
final_items.append({
    "name": "Reveal Puzzle Times",
    "count": filler*2,
    "category": ["Boon"],
    "useful": True
})

game_name = f"Manual_CTCSudoku{seed%10000}_Axxroy"
folder_name = game_name.lower()

shutil.copytree("manual_ctcsudoku_axxroy", folder_name)

target_folder = Path(folder_name) / "data/"
target_folder.mkdir(parents=True, exist_ok=True)

with open(target_folder / "items.json", 'w') as items_file:
    json.dump(final_items, items_file)
with open(target_folder / "regions.json", 'w') as regions_file:
    json.dump(regions, regions_file)
with open(target_folder / "locations.json", 'w') as locations_file:
    json.dump(final_locations, locations_file)
with open(target_folder / "game.json", 'w') as game_file:
    json.dump({
        "game": f"CTCSudoku{seed%10000}",
        "creator": "Axxroy",
        "filler_item_name": "Party Hat"
    }, game_file)

shutil.make_archive(folder_name, 'zip', "./", folder_name)
os.rename(folder_name+".zip", folder_name+".apworld")
shutil.rmtree(folder_name)

if challenge:
    victory = next(x for x in locations if x['region'] == 'Victory')['name']
else:
    victory = next(x for x in locations if x['region'] == 'Multi-Rule Sudoku')['name']

ydata = {
    "game": game_name,
    "name": "",
    game_name: {
        "progression_balancing": 50,
        "accessibility": "items"
    }
}
with open(game_name+".yaml", 'w') as yout:
    yaml.dump(ydata, yout)
    yout.write("# Your target:\n")
    yout.write(f"# Collect {req_keys} Victory Keys, then\n")
    yout.write(f"# Complete the puzzle {victory} to win\n")

print(f"Successfully Generated {game_name}")
