"""
Best practical Level-1 solution for PlantSim (Greenhouse)
=========================================================
"""

import json
from collections import defaultdict

# ========== CHANGE THESE IF NEEDED ==========
INPUT_FILE = "1(1).json"
OUTPUT_FILE = "level1_best_submission.json"
# ============================================


def load_level():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_valid_locations(level):
    locs = []
    for cell in level.get("cells", []):
        if cell.get("terrain") == 0 and cell.get("soil") in (0, 1):
            locs.append({"row": cell["row"], "col": cell["col"]})
    return locs


def create_submission(level):
    locations = find_valid_locations(level)
    print(f"Valid plantable cells: {len(locations)}")

    ticks = level.get("ticks", 500)
    max_per_tick = 20

    GRASS, ROSE, SUNFLOWER, LAVENDER, OAK = 1, 2, 5, 6, 12

    actions_by_tick = defaultdict(list)

    def add(tick, plant, row, col):
        if 0 <= tick < ticks - 1:
            actions_by_tick[tick].append({
                "plant_index": plant,
                "row": row,
                "col": col
            })

    n = len(locations)

    # ----- PHASE 1: Early Grass flood -----
    for i in range(min(n, 200)):
        tick = i // max_per_tick
        loc = locations[i]
        add(tick, GRASS, loc["row"], loc["col"])

    # ----- PHASE 2: Establish the other mid-game plants -----
    mid_plants = [LAVENDER, ROSE, SUNFLOWER, LAVENDER, ROSE]
    for i in range(min(n, 150)):
        tick = 50 + (i // max_per_tick)
        loc = locations[(i * 7) % n]
        add(tick, mid_plants[i % len(mid_plants)], loc["row"], loc["col"])

    # ----- PHASE 3: Late balanced reinforcement (most important) -----
    # Rough target ratios on the final grid:
    # Grass ~35 %, Lavender ~25 %, Rose ~20 %, Sunflower ~15 %, Oak ~5 %
    late_mix = (
        [GRASS] * 7 +
        [LAVENDER] * 5 +
        [ROSE] * 4 +
        [SUNFLOWER] * 3 +
        [OAK] * 1
    )

    start_late = max(0, ticks - 100)
    for i in range(min(n, 400)):
        tick = start_late + (i // max_per_tick)
        if tick >= ticks - 1:
            break
        loc = locations[(i * 13) % n]
        plant = late_mix[i % len(late_mix)]
        add(tick, plant, loc["row"], loc["col"])

    # Build submission
    actions = []
    for tick in sorted(actions_by_tick.keys()):
        plants = actions_by_tick[tick][:max_per_tick]
        if plants:
            actions.append({"tick": tick, "plants": plants})

    return {"actions": actions}


if __name__ == "__main__":
    level = load_level()
    submission = create_submission(level)

    total = sum(len(a["plants"]) for a in submission["actions"])
    print(f"Total plant actions: {total}")
    print(f"Ticks used: {[a['tick'] for a in submission['actions']]}")

    from collections import Counter
    cnt = Counter()
    for a in submission["actions"]:
        for p in a["plants"]:
            cnt[p["plant_index"]] += 1
    print("Plant counts in submission:", dict(sorted(cnt.items())))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(submission, f, indent=2)
    print(f"Wrote {OUTPUT_FILE}")