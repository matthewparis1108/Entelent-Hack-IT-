import json

INPUT_FILE = "1.json"
OUTPUT_FILE = "level1_submission 3.json"


def load_level():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def find_valid_locations(level):
    locations = []

    grid = level.get("grid", level.get("map", []))

    for row_index, row in enumerate(grid):
        for col_index, cell in enumerate(row):
            if not isinstance(cell, dict):
                continue

            if cell.get("terrain") == 2:
                continue

            if cell.get("soil") not in (0, 1):
                continue

            locations.append({
                "row": row_index,
                "col": col_index
            })

    return locations


def create_submission(level):
    locations = find_valid_locations(level)

    actions = []
    plant_indexes = [0, 1, 2, 3, 4]

    for tick, location in enumerate(locations):
        actions.append({
            "tick": tick,
            "plant_index": plant_indexes[tick % len(plant_indexes)],
            "row": location["row"],
            "col": location["col"]
        })

    return {
        "actions": actions
    }


with open(INPUT_FILE, "r", encoding="utf-8") as file:
    level = json.load(file)

submission = create_submission(level)

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    json.dump(submission, file, indent=2)