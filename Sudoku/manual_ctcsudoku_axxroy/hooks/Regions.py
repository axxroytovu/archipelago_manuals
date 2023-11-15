import random

# called after the regions.json has been imported, but before ids, etc. have been assigned
# if you need access to the locations after processing to add ids, etc., you should use the hooks in World.py
def before_region_table_processed(region_table: dict) -> dict:
    valid_regions = ["Positional Sudoku", "Summation Sudoku", "Parity Sudoku", "Variant Sudoku", "Multi-Rule Sudoku"]
    random.shuffle(valid_regions)
    valid_regions = ["Classic Sudoku"] + valid_regions

    for i in range(5):
        region_table[valid_regions[i]]['connects_to'] = [valid_regions[i+1]]
    return region_table
