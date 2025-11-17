import re
import os
from collections import defaultdict

def parse_units(file_path):
    """
    Parses EDU and returns a list of units with their category and ownership.
    """
    units = []
    current_unit = {}
    ownership_pattern = re.compile(r"ownership\s+(.+)")

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Start of new unit
            if line.startswith("type"):
                if current_unit:
                    units.append(current_unit)
                current_unit = {"type": line[len("type"):].strip()}

            # Category
            elif line.startswith("category"):
                current_unit["category"] = line[len("category"):].strip()

            # Ownership / factions
            match = ownership_pattern.match(line)
            if match:
                # Split by comma and strip spaces
                factions = [f.strip() for f in match.group(1).split(",")]
                current_unit["ownership"] = factions

    # Append last unit
    if current_unit:
        units.append(current_unit)

    return units

def count_units_by_faction(units):
    """
    Counts land and naval units per faction.
    """
    faction_counts = defaultdict(lambda: {"land": 0, "naval": 0})

    for unit in units:
        factions = unit.get("ownership", [])
        category = unit.get("category", "").lower()

        for f in factions:
            if category == "ship":
                faction_counts[f]["naval"] += 1
            else:
                faction_counts[f]["land"] += 1

    return faction_counts

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    edu_path = os.path.join(base_dir, "..", "data", "export_descr_unit.txt")
    edu_path = os.path.normpath(edu_path)

    if not os.path.exists(edu_path):
        raise FileNotFoundError(f"Could not find {edu_path}")

    units = parse_units(edu_path)
    faction_counts = count_units_by_faction(units)

    # Sort factions by total units (land + naval), descending
    sorted_factions = sorted(faction_counts.items(),
                             key=lambda x: x[1]['land'] + x[1]['naval'],
                             reverse=True)

    # Print total number of factions
    print(f"🔹 Total factions encountered: {len(faction_counts)}\n")

    # Print counts
    print("Faction unit counts (Land vs Naval):")
    for faction, counts in sorted_factions:
        total = counts['land'] + counts['naval']
        print(f"Faction: {faction}, Land: {counts['land']}, Naval: {counts['naval']}, Total: {total}")
