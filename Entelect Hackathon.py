import json
from pathlib import Path

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


def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Could not find level file: {path.resolve()}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_usable_cells(level):
    """Return usable cells as (column, row) tuples."""
    return [
        (cell["col"], cell["row"])
        for cell in level.get("cells", [])
        if cell.get("soil") in (0, 1) and cell.get("terrain") != 2
    ]


def make_zones(level):
    """
    Divide usable cells between the starter plants.

    Grass and Dwarf Sunflower use dirt cells.
    Rose Bush, Lavender, and Oak Tree use mud cells.
    Oak Tree is placed on the right side of the mud area so that
    its shade is less likely to affect the other starter plants.
    """
    dirt_cells = sorted(
        [
            (cell["col"], cell["row"])
            for cell in level.get("cells", [])
            if cell.get("soil") == 0 and cell.get("terrain") != 2
        ],
        key=lambda position: (position[1], position[0]),
    )

    mud_cells = sorted(
        [
            (cell["col"], cell["row"])
            for cell in level.get("cells", [])
            if cell.get("soil") == 1 and cell.get("terrain") != 2
        ],
        key=lambda position: (position[1], position[0]),
    )

    # Split dirt cells between Grass and Dwarf Sunflower.
    dirt_midpoint = len(dirt_cells) // 2
    grass_cells = dirt_cells[:dirt_midpoint]
    sunflower_cells = dirt_cells[dirt_midpoint:]

    # Safely handle levels that contain no mud cells.
    if not mud_cells:
        return {
            "Grass": grass_cells,
            "Dwarf Sunflower": sunflower_cells,
            "Rose Bush": [],
            "Lavender": [],
            "Oak Tree": [],
        }

    # Place Oak Tree on the rightmost section of the mud cells.
    mud_col_max = max(column for column, _ in mud_cells)
    oak_cells = [
        position
        for position in mud_cells
        if position[0] >= mud_col_max - 2
    ]
    remaining_mud = [
        position
        for position in mud_cells
        if position[0] < mud_col_max - 2
    ]

    # If the selected Oak Tree area used all mud cells, retain a safe
    # fallback so the other plants can still be assigned cells.
    if not remaining_mud:
        oak_cells = mud_cells
        remaining_mud = []

    mud_midpoint = len(remaining_mud) // 2
    rose_cells = remaining_mud[:mud_midpoint]
    lavender_cells = remaining_mud[mud_midpoint:]

    return {
        "Grass": grass_cells,
        "Dwarf Sunflower": sunflower_cells,
        "Rose Bush": rose_cells,
        "Lavender": lavender_cells,
        "Oak Tree": oak_cells,
    }


def build_actions(zones, level):
    """
    Convert plant zones into actions grouped by tick.

    Each tick contains at most MAX_PLANTS_PER_TICK plants.
    Plants that cannot fit within the available number of ticks
    are reported rather than silently discarded.
    """
    total_ticks = int(level.get("ticks", 0))

    if total_ticks <= 0:
        raise ValueError("The level must contain at least one tick.")

    actions = {tick: [] for tick in range(total_ticks)}
    planned_plants = 0
    skipped_plants = 0

    # Flatten all planned plants into a single list.
    plants_to_place = []

    for plant_name, cells in zones.items():
        if plant_name not in PLANT_INDEX:
            raise KeyError(f"Unknown plant: {plant_name}")

        plant_index = PLANT_INDEX[plant_name]

        for column, row in cells:
            plants_to_place.append(
                {
                    "plant_index": plant_index,
                    "row": row,
                    "col": column,
                }
            )

    planned_plants = len(plants_to_place)

    # Spread plants over the available ticks.
    for position, plant in enumerate(plants_to_place):
        tick = position // MAX_PLANTS_PER_TICK

        if tick >= total_ticks:
            skipped_plants += 1
            continue

        actions[tick].append(plant)

    submission = {
        "actions": [
            {"tick": tick, "plants": actions[tick]}
            for tick in range(total_ticks)
            if actions[tick]
        ]
    }

    if skipped_plants:
        print(
            f"Warning: {skipped_plants} of {planned_plants} plants "
            f"could not be scheduled within {total_ticks} ticks."
        )

    return submission


def build_grid(level, zones):
    """Build a printable grid containing plant indexes."""
    rows = int(level["rows"])
    cols = int(level["cols"])
    grid = [[0 for _ in range(cols)] for _ in range(rows)]

    for plant_name, cells in zones.items():
        plant_index = PLANT_INDEX[plant_name]

        for column, row in cells:
            if not (0 <= row < rows and 0 <= column < cols):
                raise ValueError(
                    f"Cell ({column}, {row}) is outside the grid."
                )

            if grid[row][column] != 0:
                raise ValueError(
                    f"Cell ({column}, {row}) was assigned more than once."
                )

            grid[row][column] = plant_index

    return grid


def print_grid(grid):
    """Print the grid in a readable format."""
    if not grid or not grid[0]:
        print("Grid is empty.")
        return

    width = max(len(str(cell)) for row in grid for cell in row)

    for row in grid:
        print(" ".join(str(cell).rjust(width) for cell in row))


def print_legend():
    """Print the plant index legend."""
    print("\nPlant Index Legend:")

    for plant_name, index in PLANT_INDEX.items():
        print(f"  {index}: {plant_name}")


def main():
    # Keep 1.json beside this Python script.
    script_directory = Path(__file__).resolve().parent
    level_path = script_directory / "1.json"

    level = load_json_file(level_path)

    required_fields = ("cols", "rows", "ticks", "cells")
    missing_fields = [
        field for field in required_fields
        if field not in level
    ]

    if missing_fields:
        raise ValueError(
            "The level file is missing required fields: "
            + ", ".join(missing_fields)
        )

    print(
        f"Grid: {level['cols']}x{level['rows']}, "
        f"{level['ticks']} ticks, "
        f"animals_enabled={level.get('animals_enabled', False)}"
    )

    usable = get_usable_cells(level)
    total_cells = level["cols"] * level["rows"]

    print(
        f"Usable (Dirt/Mud) cells: {len(usable)} "
        f"out of {total_cells} total grid cells"
    )

    zones = make_zones(level)
    submission = build_actions(zones, level)

    output_path = script_directory / "level1_submission.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(submission, file, indent=2)

    print(f"\nSubmission saved to: {output_path}")

    grid = build_grid(level, zones)
    print_grid(grid)
    print_legend()


if __name__ == "__main__":
    main()
