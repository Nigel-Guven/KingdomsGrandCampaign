import re
import os

def parse_unit_blocks(file_path):
    """Split EDU file into separate unit entries by 'type' keyword."""
    units = []
    current = []
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith("type"):
                if current:
                    units.append(current)
                current = [line.strip()]
            elif current:
                current.append(line.strip())
        if current:
            units.append(current)
    return units


def validate_unit(unit_lines):
    name = unit_lines[0].split("type", 1)[1].strip()
    ownership = None
    era_lines = []
    errors = []

    for line in unit_lines:
        if line.startswith("ownership"):
            if ownership is not None:
                errors.append(f"Multiple ownership lines found in '{name}'")
            ownership = line
            if line.endswith(","):
                errors.append(f"Trailing comma in ownership line of '{name}'")
        elif line.startswith("era"):
            era_lines.append(line)
            # Validate era number
            m = re.match(r"era\s+(\d+)", line)
            if not m or m.group(1) not in {"0", "1", "2"}:
                errors.append(f"Invalid era number in '{name}': {line}")
            if line.endswith(","):
                errors.append(f"Trailing comma in {line.split()[0]} line of '{name}'")

    # --- Structural checks ---
    if ownership is None:
        errors.append(f"Missing ownership line in '{name}'")

    # --- Faction consistency check ---
    if ownership and era_lines:
        own_factions = [f.strip() for f in ownership.split(None, 1)[1].split(",") if f.strip()]
        own_factions = [f for f in own_factions if f != "slave"]

        for era_line in era_lines:
            parts = era_line.split(None, 2)
            if len(parts) < 3:
                errors.append(f"Missing faction list in {era_line} of '{name}'")
                continue
            factions = [f.strip() for f in parts[2].split(",") if f.strip()]
            missing = [f for f in own_factions if f not in factions]
            if missing:
                errors.append(f"Factions missing from {parts[0]} {parts[1]} in '{name}': {', '.join(missing)}")

    return errors


def validate_edu(file_path):
    units = parse_unit_blocks(file_path)
    errors = []
    for unit in units:
        errors.extend(validate_unit(unit))

    if errors:
        print("❌ Validation errors found:")
        for e in errors:
            print(" -", e)
    else:
        print("✅ No ownership/era errors detected! File looks consistent.")
    print(f"\n📊 Scanned {len(units)} units, found {len(errors)} issues.")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    edu_path = os.path.join(base_dir, "..", "data", "export_descr_unit.txt")
    edu_path = os.path.normpath(edu_path)

    print(f"🔍 Validating file: {edu_path}")
    validate_edu(edu_path)
