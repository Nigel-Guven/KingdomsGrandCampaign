import re
import os
import sys

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

            # New unit starts
            if line.startswith("type"):
                if current_unit:
                    units.append(current_unit)
                current_unit = {"type": line[len("type"):].strip()}

            # Ownership line
            match = ownership_pattern.match(line)
            if match:
                factions = [f.strip().lower() for f in match.group(1).split(",")]
                current_unit["ownership"] = factions

    # Add final unit
    if current_unit:
        units.append(current_unit)

    return units


def list_units_for_faction(units, faction):
    """
    Returns a list of units owned by the given faction.
    """
    faction = faction.lower()
    owned_units = []

    for u in units:
        owners = u.get("ownership", [])
        if faction in owners:
            owned_units.append(u["type"])

    return owned_units


if __name__ == "__main__":
    # Make sure user provided a faction name
    if len(sys.argv) < 2:
        print("Usage: python list_units.py <faction_name>")
        sys.exit(1)

    faction = sys.argv[1]

    base_dir = os.path.dirname(os.path.abspath(__file__))
    edu_path = os.path.join(base_dir, "..", "data", "export_descr_unit.txt")
    edu_path = os.path.normpath(edu_path)

    if not os.path.exists(edu_path):
        raise FileNotFoundError(f"Could not find {edu_path}")

    # Parse EDU
    units = parse_units(edu_path)

    # Get units for that faction
    results = list_units_for_faction(units, faction)

    print(f"\nUnits for faction: {faction}")
    print(f"Total: {len(results)}\n")
    for unit in results:
        print(unit)
