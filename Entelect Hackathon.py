import json
import os

MAX_PLANTS_PER_TICK = 20

PLANT_INDEX = {
    "Grass": 1,
    "Rose Bush": 2,
    "Dwarf Sunflower": 5,
    "Lavender": 6,
    "Oak Tree": 12,
}

PLANT_PREFERRED_SOIL = {
    "Grass": [0, 1],
    "Rose Bush": [0, 1],
    "Lavender": [0, 1],
    "Dwarf Sunflower": [0, 1],
    "Oak Tree": [0, 1],
}


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, "1.json")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "level1_submission.json")


def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_usable_cells(level):
    usable = []

    for cell in level["cells"]:
        if cell["soil"] in (0, 1) and cell["terrain"] != 2:
            usable.append((cell["col"], cell["row"]))

    return usable


def make_zones(level):
    dirt_cells = [
        (cell["col"], cell["row"])
        for cell in level["cells"]
        if cell["soil"] == 0 and cell["terrain"] != 2
    ]

    mud_cells = [
        (cell["col"], cell["row"])
        for cell in level["cells"]
        if cell["soil"] == 1 and cell["terrain"] != 2
    ]

    dirt_cells.sort(key=lambda xy: (xy[1], xy[0]))
    mud_cells.sort(key=lambda xy: (xy[1], xy[0]))

    # Split dirt between Grass and Dwarf Sunflower
    mid = len(dirt_cells) // 2

    grass_cells = dirt_cells[:mid]
    sunflower_cells = dirt_cells[mid:]

    # Put Oak Trees on the far right of the mud
    if mud_cells:
        mud_col_max = max(col for col, row in mud_cells)

        oak_cells = [
            cell
            for cell in mud_cells
            if cell[0] >= mud_col_max - 2
        ]

        remaining_mud = [
            cell
            for cell in mud_cells
            if cell[0] < mud_col_max - 2
        ]
    else:
        oak_cells = []
        remaining_mud = []

    # Split remaining mud between Rose Bush and Lavender
    rmid = len(remaining_mud) // 2

    rose_cells = remaining_mud[:rmid]
    lavender_cells = remaining_mud[rmid:]

    return {
        "Grass": grass_cells,
        "Dwarf Sunflower": sunflower_cells,
        "Rose Bush": rose_cells,
        "Lavender": lavender_cells,
        "Oak Tree": oak_cells,
    }


def build_actions(zones, level):
    total_ticks = level["ticks"]
    actions = {}

    for plant_name, cells in zones.items():
        current_plant_index = PLANT_INDEX[plant_name]

        for i in range(0, len(cells), MAX_PLANTS_PER_TICK):
            batch = cells[i:i + MAX_PLANTS_PER_TICK]
            tick = i // MAX_PLANTS_PER_TICK

            if tick >= total_ticks:
                break

            actions.setdefault(tick, []).append(
                (current_plant_index, batch)
            )

    tick_entries = []

    for tick in sorted(actions.keys()):
        plants_list = []

        for current_plant_index, batch in actions[tick]:
            for x, y in batch:
                plants_list.append({
                    "plant_index": current_plant_index,
                    "row": y,
                    "col": x
                })

        plants_list = plants_list[:MAX_PLANTS_PER_TICK]

        tick_entries.append({
            "tick": tick,
            "plants": plants_list
        })

    return {
        "actions": tick_entries
    }


def main():
    if not os.path.exists(INPUT_FILE):
        print("ERROR: 1.json not found.")
        print("Expected:", INPUT_FILE)
        return

    level = load_json_file(INPUT_FILE)

    print(
        f"Grid: {level['cols']}x{level['rows']}, "
        f"{level['ticks']} ticks, "
        f"animals_enabled={level['animals_enabled']}"
    )

    usable = get_usable_cells(level)

    print(
        f"Usable cells: {len(usable)} / "
        f"{level['cols'] * level['rows']}"
    )

    zones = make_zones(level)

    print("\nPlant zones:")

    for plant_name, cells in zones.items():
        print(
            f"  {plant_name}: "
            f"index={PLANT_INDEX[plant_name]}, "
            f"cells={len(cells)}"
        )

    submission = build_actions(zones, level)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(submission, file, indent=2)

    print("\nSUCCESS!")
    print("Updated:")
    print(OUTPUT_FILE)

    total_plants = sum(
        len(action["plants"])
        for action in submission["actions"]
    )

    print(f"Total plants scheduled: {total_plants}")
    print(f"Total ticks used: {len(submission['actions'])}")


if __name__ == "__main__":
    main()