"""
Level 1 – balanced starters, minimal Oak
"""

import json
from collections import defaultdict

# ========== CHANGE THESE ==========
INPUT_FILE = "1(1).json"                 # or "1(1).json"
OUTPUT_FILE = "level1_submission.json"
# ==================================


def load_level():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_valid_locations(level):
    locations = []
    for cell in level.get("cells", []):
        if cell.get("terrain") == 0 and cell.get("soil") in (0, 1):
            locations.append({"row": cell["row"], "col": cell["col"]})
    return locations


def create_submission(level):
    locations = find_valid_locations(level)
    print(f"Found {len(locations)} locations")

    ticks = level.get("ticks", 500)
    max_per = 20
    n = len(locations)

    G, R, S, L, O = 1, 2, 5, 6, 12

    by_tick = defaultdict(list)

    def plant(tick, idx, row, col):
        if 0 <= tick < ticks - 1:
            by_tick[tick].append({
                "plant_index": idx,
                "row": row,
                "col": col
            })

    # PHASE 1 (0-30): Grass heavy + Rose/Lavender/Sunflower
    for i in range(min(300, n)):
        t = i // max_per
        if t > 30:
            break
        loc = locations[i % n]
        choice = i % 20
        if choice < 12:
            p = G
        elif choice < 15:
            p = R
        elif choice < 18:
            p = L
        else:
            p = S
        plant(t, p, loc["row"], loc["col"])

    # PHASE 2 (50-120): establish all non-Oak starters
    for i in range(min(300, n)):
        t = 50 + (i // max_per)
        if t > 120:
            break
        loc = locations[(i * 7) % n]
        choice = i % 20
        if choice < 7:
            p = G
        elif choice < 12:
            p = L
        elif choice < 16:
            p = R
        else:
            p = S
        plant(t, p, loc["row"], loc["col"])

    # PHASE 3 (400-490): FINAL balance – almost no Oak
    # 19/20 are G/L/R/S, only 1/20 is Oak
    final_mix = [G, L, R, S, G, L, R, S, G, L, R, S, G, L, R, S, G, L, R, O]
    for i in range(min(500, n * 2)):
        t = 400 + (i // max_per)
        if t >= ticks - 1:
            break
        loc = locations[i % n]
        plant(t, final_mix[i % len(final_mix)], loc["row"], loc["col"])

    actions = []
    for tick in sorted(by_tick.keys()):
        plants = by_tick[tick][:max_per]
        if plants:
            actions.append({"tick": tick, "plants": plants})

    return {"actions": actions}


if __name__ == "__main__":
    level = load_level()
    submission = create_submission(level)

    total = sum(len(a["plants"]) for a in submission["actions"])
    print(f"Total plant actions: {total}")
    print(f"Tick groups: {len(submission['actions'])}")

    from collections import Counter
    cnt = Counter()
    for a in submission["actions"]:
        for p in a["plants"]:
            cnt[p["plant_index"]] += 1
    print("Plant counts:", dict(sorted(cnt.items())))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(submission, f, indent=2)
    print(f"Wrote {OUTPUT_FILE}")