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
    """Load a JSON file and return its contents as a Python object."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data


def get_usable_cells(level):
    usable = []
    for cell in level["cells"]:
        if cell["soil"] in (0, 1) and cell["terrain"] != 2:
            usable.append((cell["col"], cell["row"]))
    return usable


def make_zones(level):
    """Assign each starter plant to real soil, grouped so Oak Tree's
    shade never reaches the shade-sensitive species (Grass, Dwarf
    Sunflower). Uses the level's real soil data, not a guessed
    rectangle."""
    dirt_cells = [(c["col"], c["row"]) for c in level["cells"]
                  if c["soil"] == 0 and c["terrain"] != 2]
    mud_cells = [(c["col"], c["row"]) for c in level["cells"]
                 if c["soil"] == 1 and c["terrain"] != 2]

    dirt_cells.sort(key=lambda xy: (xy[1], xy[0]))
    mud_cells.sort(key=lambda xy: (xy[1], xy[0]))

    mid = len(dirt_cells) // 2
    grass_cells = dirt_cells[:mid]
    sunflower_cells = dirt_cells[mid:]

    mud_col_max = max(c[0] for c in mud_cells)
    oak_cells = [c for c in mud_cells if c[0] >= mud_col_max - 2]
    remaining_mud = [c for c in mud_cells if c[0] < mud_col_max - 2]

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
    actions = {}  # tick -> list of (plant_index, batch of cells)

    for plant_name, cells in zones.items():
        index = plant_index[plant_name]
        for i in range(0, len(cells), max_plants_per_tick):
            batch = cells[i:i + max_plants_per_tick]
            tick = i // max_plants_per_tick
            if tick >= total_ticks:
                break
            actions.setdefault(tick, []).append((index, batch))

    tick_entries = []
    for tick in sorted(actions.keys()):
        plants_list = []
        for index, batch in actions[tick]:
            for (x, y) in batch:
                plants_list.append({"index": index, "row": y, "col": x})
        plants_list = plants_list[:max_plants_per_tick]
        tick_entries.append({"tick": tick, "plants": plants_list})

    return {"actions": tick_entries}


def build_grid(level, zones):
    grid = [[0 for _ in range(level["cols"])] for _ in range(level["rows"])]
    for plant_name, cells in zones.items():
        index = plant_index[plant_name]
        for (x, y) in cells:
            grid[y][x] = index
    return grid


def print_grid(grid):
    width = max(len(str(cell)) for row in grid for cell in row)
    for row in grid:
        print(" ".join(str(cell).rjust(width) for cell in row))


def print_legend():
    print()
    print("Plant Index Legend:")
    for plant_name, index in plant_index.items():
        print(f"  {index}: {plant_name}")


if __name__ == "__main__":
    level = load_json_file("1.json")

    print(f"Grid: {level['cols']}x{level['rows']}, {level['ticks']} ticks, "
          f"animals_enabled={level['animals_enabled']}")
    usable = get_usable_cells(level)
    print(f"Usable (Dirt/Mud) cells: {len(usable)} out of "
          f"{level['cols'] * level['rows']} total grid cells")

    zones = make_zones(level)
    submission = build_actions(zones, level)

    with open("level1_submission.json", "w") as f:
        json.dump(submission, f, indent=2)

    grid = build_grid(level, zones)
    print_grid(grid)
    print_legend()