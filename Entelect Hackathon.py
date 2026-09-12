import json



def load_json_file(file_path):
    """Load a JSON file and return its contents as a Python object."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data
def display_json_data(data):
    """Display the contents of a JSON object in a readable format."""
    print(json.dumps(data, indent=4))


GRID_WIDTH=50
GRID_HEIGHT=50
TOTAL_TICKS=200
MAX_PLANTS_PER_TICK=50

plant_index={
    "Grass": 1,
    "Rose Bush": 2,
    "Dwarf Sunflower": 5,
    "Lavender": 6,
    "Oak Tree": 12,

}

def make_zones(width, height):
    mid_x = width // 2
    mid_y = height // 3
 
    zones = {
        # Oak Tree gets its own corner, away from Grass/Sunflower
        "Oak Tree":        [(x, y) for x in range(0, mid_x) for y in range(0, mid_y)],
        "Rose Bush":        [(x, y) for x in range(mid_x, width) for y in range(0, mid_y)],
        "Lavender":         [(x, y) for x in range(0, mid_x) for y in range(mid_y, 2 * mid_y)],
        "Dwarf Sunflower":  [(x, y) for x in range(mid_x, width) for y in range(mid_y, 2 * mid_y)],
        "Grass":            [(x, y) for x in range(0, width) for y in range(2 * mid_y, height)],
    }
    return zones
def build_actions(zones):
    actions = {}  # tick -> list of plant actions
 
    for plant_name, cells in zones.items():
        index = plant_index[plant_name]
        # plant this zone in batches of MAX_PLANTS_PER_TICK, one batch per tick,
        # starting at tick 0
        for i in range(0, len(cells), MAX_PLANTS_PER_TICK):
            batch = cells[i:i + MAX_PLANTS_PER_TICK]
            tick = i // MAX_PLANTS_PER_TICK  # tick 0, 1, 2, ...
            if tick >= TOTAL_TICKS:
                break
            actions.setdefault(tick, []).append((index, batch))
 
    # convert to the submission format
    tick_entries = []
    for tick in sorted(actions.keys()):
        plants_list = []
        for index, batch in actions[tick]:
            for (x, y) in batch:
                plants_list.append({
                    "plant_index": index,
                    "row": y,
                    "col": x,
                })
        # respect the 20-per-tick cap across ALL plants in that tick
        plants_list = plants_list[:MAX_PLANTS_PER_TICK]
        tick_entries.append({"tick": tick, "plants": plants_list})
 
    return {"actions": tick_entries}
def build_grid():
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    zones = make_zones(GRID_WIDTH, GRID_HEIGHT)
 
    for plant_name, cells in zones.items():
        index = plant_index[plant_name]
        for (x, y) in cells:
            grid[y][x] = index
 
    return grid

def print_grid(grid):
    for row in grid:
        print(" ".join(str(cell) for cell in row))

def print_legend():
    print("Plant Index Legend:")
    for plant_name, index in plant_index.items():
        print(f"{index}: {plant_name}")
    print("Legend:")
 
if __name__ == "__main__":
    animaldb = load_json_file('animals.json')
    plantdb = load_json_file('plant_dataset.json')
    plant_unlock_conditions = load_json_file('plant_unlock_conditions.json')
    classifications = load_json_file('classifications.json')

    zones = make_zones(GRID_WIDTH, GRID_HEIGHT)
    submission = build_actions(zones)
 
    with open("level1_submission.json", "w") as f:
        json.dump(submission, f, indent=2)

grid = build_grid()
print_grid(grid)
print_legend()
