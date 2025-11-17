import re
import os

def parse_units(file_path):
    """
    Parses EDU and returns a list of units with type and ownership.
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

            # Ownership / factions
            match = ownership_pattern.match(line)
            if match:
                factions = [f.strip() for f in match.group(1).split(",")]
                current_unit["ownership"] = factions

    # Append last unit
    if current_unit:
        units.append(current_unit)

    return units

def count_factions_per_unit(units):
    """
    Returns a dictionary of units and how many factions own each unit.
    """
    unit_usage = {}

    for unit in units:
        unit_type = unit.get("type", "UNKNOWN")
        ownership = unit.get("ownership", [])
        unit_usage[unit_type] = len(ownership)

    return unit_usage

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    edu_path = os.path.join(base_dir, "..", "data", "export_descr_unit.txt")
    edu_path = os.path.normpath(edu_path)

    if not os.path.exists(edu_path):
        raise FileNotFoundError(f"Could not find {edu_path}")

    units = parse_units(edu_path)
    unit_usage = count_factions_per_unit(units)

    # Sort by number of factions using the unit (descending)
    sorted_units = sorted(unit_usage.items(), key=lambda x: x[1], reverse=True)

    print(f"🔹 Total unit types encountered: {len(unit_usage)}\n")
    print("Unit usage (number of factions that own each unit):")
    for unit_type, faction_count in sorted_units:
        print(f"Unit: {unit_type}, Factions: {faction_count}")
