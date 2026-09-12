import json

max_plants_per_tick = 20

plant_index = {
    "Grass": 1,
    "Rose Bush": 2,
    "Dwarf Sunflower": 5,
    "Lavender": 6,
    "Oak Tree": 12,
}

plant_preferred_soil = {
    "Grass": [0, 1],
    "Rose Bush": [0, 1],
    "Lavender": [0, 1],
    "Dwarf Sunflower": [0, 1],
    "Oak Tree": [0, 1],
}


def load_json_file(file_path):
    with open(file_path, "r") as file:
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
            cell for cell in mud_cells
            if cell[0] >= mud_col_max - 2
        ]

        remaining_mud = [
            cell for cell in mud_cells
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

        # Get the actual numeric plant index
        current_plant_index = plant_index[plant_name]

        for i in range(0, len(cells), max_plants_per_tick):

            batch = cells[i:i + max_plants_per_tick]
            tick = i // max_plants_per_tick

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

        plants_list = plants_list[:max_plants_per_tick]

        tick_entries.append({
            "tick": tick,
            "plants": plants_list
        })

    return {
        "actions": tick_entries
    }


def print_zones(zones):
    print("\nPlant zones:")

    for plant_name, cells in zones.items():
        print(
            f"{plant_name}: "
            f"index={plant_index[plant_name]}, "
            f"cells={len(cells)}"
        )


def main():
    level = load_json_file("1.json")

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

    print_zones(zones)

    submission = build_actions(zones, level)

    with open("level1_submission.json", "w") as file:
        json.dump(submission, file, indent=2)

    print("\nSaved: level1_submission.json")

    for action in submission["actions"]:
        print(
            f"Tick {action['tick']}: "
            f"{len(action['plants'])} plants"
        )


if __name__ == "__main__":
    main()