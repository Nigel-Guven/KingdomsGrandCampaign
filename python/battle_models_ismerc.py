import os
import re
import sys

MODELDB_NAME = "battle_models.modeldb"

MODELDB_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
    "..", "data", "unit_models", MODELDB_NAME)
)


def is_unit_start(lines, i):
    """Return unit_name if this is the start of a unit block, else None."""
    if i + 1 >= len(lines):
        return None

    line = lines[i].strip()
    next_line = lines[i+1].strip()

    m = re.match(r"^(\d+)\s+([A-Za-z0-9_]+)$", line)
    if not m:
        return None

    if next_line != "1 4":
        return None

    return m.group(2)


def parse_modeldb(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [line.rstrip("\n") for line in f]

    units = []
    current = None
    i = 0

    while i < len(lines):
        unit_name = is_unit_start(lines, i)

        if unit_name:
            if current:
                units.append(current)

            current = {
                "unit": unit_name,
                "skins": [],
                "has_merc_skin": False
            }

            i += 2
            continue

        if current:
            if lines[i].strip().startswith("4 merc"):
                current["skins"].append("merc")
                current["has_merc_skin"] = True

            m = re.match(r"^\d+\s+([a-zA-Z0-9_]+)$", lines[i])
            if m:
                faction = m.group(1)
                if faction not in ("None", "Horse", "Camel", "Elephant") and not faction.isdigit():
                    current["skins"].append(faction)

        i += 1

    if current:
        units.append(current)

    return units


def parse_args():
    """
    Supports:
      merc=true
      merc=false
    """
    show_merc = None

    for arg in sys.argv[1:]:
        arg = arg.lower().strip()

        if arg == "merc=true":
            show_merc = True
        elif arg == "merc=false":
            show_merc = False

    return show_merc


if __name__ == "__main__":
    print(f"📄 Parsing: {MODELDB_PATH}")

    if not os.path.exists(MODELDB_PATH):
        print("❌ File missing")
        exit(1)

    filter_merc = parse_args()
    units = parse_modeldb(MODELDB_PATH)

    print(f"✔ Found {len(units)} units in ModelDB")

    if filter_merc is True:
        print("🔍 Showing ONLY units with merc skins:\n")
        units = [u for u in units if u["has_merc_skin"]]

    elif filter_merc is False:
        print("🔍 Showing ONLY units WITHOUT merc skins:\n")
        units = [u for u in units if not u["has_merc_skin"]]

    else:
        print("\n(No merc=true/merc=false filter used)\n")

    for u in units:
        print(f"{u['unit']}: skins={u['skins']} merc={u['has_merc_skin']}")
