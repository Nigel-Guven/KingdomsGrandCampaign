import re
import os

# ---------------------------------------------
# FILE PATHS FOR KGCM
# ---------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # kgcm/python/

EDU_FILE = os.path.join(BASE_DIR, "..", "data", "export_descr_unit.txt")
EDB_FILE = os.path.join(BASE_DIR, "..", "data", "export_descr_buildings.txt")
print(os.path.abspath(EDU_FILE))
# Regex patterns
UNIT_TYPE_RE = re.compile(r"^type\s+(.+)$")
RECRUIT_POOL_RE = re.compile(r'recruit_pool\s+"([^"]+)"')

# ---------------------------------------------
# Read EDU units
# ---------------------------------------------
edu_units = set()

with open(EDU_FILE, "r", encoding="cp1252") as f:
    for line in f:
        m = UNIT_TYPE_RE.match(line.strip())
        if m:
            unit_name = m.group(1).strip()
            edu_units.add(unit_name)

print(f"[INFO] Units found in EDU: {len(edu_units)}")

# ---------------------------------------------
# Read EDB recruit_pool entries
# ---------------------------------------------
edb_units = set()

with open(EDB_FILE, "r", encoding="utf-8") as f:
    for line in f:
        m = RECRUIT_POOL_RE.search(line)
        if m:
            unit_name = m.group(1).strip()
            edb_units.add(unit_name)

print(f"[INFO] Units found in EDB recruit_pool: {len(edb_units)}")

# ---------------------------------------------
# Find units NOT in EDB recruitment
# ---------------------------------------------
missing = sorted(edu_units - edb_units)

print("\n========== MISSING RECRUITMENT ENTRIES ==========")
if not missing:
    print("All EDU units appear in EDB recruitment pools!")
else:
    for u in missing:
        print(u)
print("=================================================\n")

# ---------------------------------------------
# OPTIONAL: Units that appear in EDB but not in EDU
# ---------------------------------------------
extra = sorted(edb_units - edu_units)

if extra:
    print("========== UNITS IN EDB BUT NOT IN EDU ==========")
    for u in extra:
        print(u)
    print("=================================================\n")
