import json
from collections import defaultdict

# ========== CHANGE THESE TO MATCH YOUR LOCAL FILES ==========
INPUT_FILE = "1.json"                       # your level file
OUTPUT_FILE = "level1_submission.json"      # file you will submit
# ============================================================


def load_level():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def find_valid_locations(level):
    """
    Plantable cells:
    - terrain == 0  (ground)
    - soil in (0, 1)  (Dirt or Mud – preferred by starting plants)
    """
    locations = []
    for cell in level.get("cells", []):
        if cell.get("terrain") != 0:
            continue
        if cell.get("soil") not in (0, 1):
            continue
        locations.append({
            "row": cell["row"],
            "col": cell["col"]
        })
    return locations


def create_submission(level):
    locations = find_valid_locations(level)
    print(f"Found {len(locations)} valid locations")

    # Only these 5 plants are unlocked at the start
    plant_indexes = [1, 2, 5, 6, 12]
    # 1 = Grass
    # 2 = Rose Bush
    # 5 = Dwarf Sunflower
    # 6 = Lavender
    # 12 = Oak Tree

    ticks = level.get("ticks", 500)
    max_plants_per_tick = 20

    actions_by_tick = defaultdict(list)

    # CRITICAL: nutrients start at 100 and drop 1 per tick.
    # After ~100 ticks the plant dies.
    # Score is calculated only on the FINAL tick.
    # So we plant late so the plants are still alive at the end.