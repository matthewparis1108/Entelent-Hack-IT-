import json
from collections import defaultdict

# --- change these two lines to match your actual file names ---
INPUT_FILE = "1.json"                    # or "level1.json", whatever the input is called
OUTPUT_FILE = "level1_submission.json"   # the file you will submit
# --------------------------------------------------------------

def load_level():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def find_valid_locations(level):
    """Find cells that are plantable: terrain != 2 and soil in (0, 1)."""
    locations = []
    for cell in level.get("cells", []):
        terrain = cell.get("terrain")
        soil = cell.get("soil")
        if terrain == 2:          # uninhabitable
            continue
        if soil not in (0, 1):    # preferred soil for starting plants
            continue
        locations.append({
            "row": cell["row"],
            "col": cell["col"]
        })
    return locations


def create_submission(level):
    locations = find_valid_locations(level)
    print(f"Found {len(locations)} valid locations")

    # Only these plants are unlocked at the start
    plant_indexes = [1, 2, 5, 6, 12]   # Grass, Rose Bush, Dwarf Sunflower, Lavender, Oak Tree

    ticks = level.get("ticks", 500)
    max_plants_per_tick = 20

    actions_by_tick = defaultdict(list)

    # Plant up to 200 plants early so they have time to grow/spread
    num_to_plant = min(len(locations), 200)
    for i, location in enumerate(locations[:num_to_plant]):
        tick = i // max_plants_per_tick
        if tick >= ticks - 1:
            break
        plant_index = plant_indexes[i % len(plant_indexes)]
        actions_by_tick[tick].append({
            "plant_index": plant_index,
            "row": location["row"],
            "col": location["col"]
        })

    # Build the required format
    actions = []
    for tick in sorted(actions_by_tick.keys()):
        plants = actions_by_tick[tick][:max_plants_per_tick]
        actions.append({
            "tick": tick,
            "plants": plants
        })

    return {"actions": actions}


if __name__ == "__main__":
    level = load_level()
    submission = create_submission(level)

    total_plants = sum(len(a["plants"]) for a in submission["actions"])
    print(f"Created submission with {len(submission['actions'])} tick entries, "
          f"{total_plants} total plant actions")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(submission, file, indent=2)
    print(f"Wrote {OUTPUT_FILE}")