import re
from collections import defaultdict
from pathlib import Path

# --- PATH SETUP ---
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent  # kgcm/
MERC_FILE = ROOT_DIR / "data/world/maps/campaign/imperial_campaign/descr_mercenaries.txt"

# --- PARSING STATE ---
pool_name = None
pool_units = defaultdict(list)
unit_locations = defaultdict(list)

unit_regex = re.compile(r'^\s*unit\s+([^,\t]+)', re.IGNORECASE)
pool_regex = re.compile(r'^\s*pool\s+(.+)', re.IGNORECASE)

# --- READ FILE ---
with MERC_FILE.open(encoding="utf-8", errors="ignore") as f:
    for lineno, line in enumerate(f, 1):
        line = line.strip()

        if not line or line.startswith(";"):
            continue

        pool_match = pool_regex.match(line)
        if pool_match:
            pool_name = pool_match.group(1).strip()
            continue

        unit_match = unit_regex.match(line)
        if unit_match and pool_name:
            unit_name = unit_match.group(1).strip()
            pool_units[pool_name].append(unit_name)
            unit_locations[unit_name].append(pool_name)

# --- REPORT ---
print("\n=== DUPLICATES WITHIN THE SAME POOL (CTD RISK) ===\n")
found = False
for pool, units in pool_units.items():
    seen = set()
    duplicates = set()

    for u in units:
        if u in seen:
            duplicates.add(u)
        seen.add(u)

    if duplicates:
        found = True
        print(f"Pool: {pool}")
        for u in sorted(duplicates):
            print(f"  - {u}")
        print()

if not found:
    print("None found.\n")

print("\n=== UNITS APPEARING IN MULTIPLE POOLS ===\n")
for unit, pools in sorted(unit_locations.items()):
    unique_pools = sorted(set(pools))
