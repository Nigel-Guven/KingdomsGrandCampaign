import os


def get_mercenary_unit_names(filepath):
    mercenary_units = []

    current_type = None
    is_mercenary = False

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            # Start of a new unit
            if line.startswith("type "):
                # Save previous unit if it was mercenary
                if current_type and is_mercenary:
                    mercenary_units.append(current_type)

                current_type = line.split("type", 1)[1].strip()
                is_mercenary = False

            # Check attributes
            elif line.startswith("attributes") and current_type:
                if "mercenary_unit" in line:
                    is_mercenary = True

        # Handle last unit in file
        if current_type and is_mercenary:
            mercenary_units.append(current_type)

    return mercenary_units


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    edu_path = os.path.normpath(
        os.path.join(base_dir, "..", "data", "export_descr_unit.txt")
    )

    if not os.path.exists(edu_path):
        raise FileNotFoundError(f"Could not find {edu_path}")

    print(f"🔍 Reading file: {edu_path}\n")

    merc_units = get_mercenary_unit_names(edu_path)

    print("🪙 Mercenary Units:")
    for name in merc_units:
        print(f"- {name}")

    print(f"\nTotal: {len(merc_units)}")
