import re
import os

def parse_edu(file_path):
    units = []
    current_unit = {}
    soldier_pattern = re.compile(r"soldier\s+([^,]+),\s*(\d+)")

    with open(file_path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()

            # Start of new unit
            if line.startswith("type"):
                if current_unit:
                    units.append(current_unit)
                current_unit = {"type": line[len("type"):].strip(), "line_no": line_no}

            # Category
            elif line.startswith("category"):
                current_unit["category"] = line[len("category"):].strip()

            # Class
            elif line.startswith("class"):
                current_unit["class"] = line[len("class"):].strip()

            # Soldier line
            match = soldier_pattern.match(line)
            if match:
                model = match.group(1)
                number = int(match.group(2))
                current_unit["soldier_model"] = model
                current_unit["soldier_number"] = number

    # Append last unit
    if current_unit:
        units.append(current_unit)

    return units

def validate_units(units):
    total_units = len(units)
    print(f"✅ Total units parsed: {total_units}\n")

    errors = []

    for unit in units:
        missing = []
        if "soldier_model" not in unit:
            missing.append("soldier_model")
        if "soldier_number" not in unit:
            missing.append("soldier_number")
        if "category" not in unit:
            missing.append("category")
        if "class" not in unit:
            missing.append("class")

        if missing:
            errors.append((unit.get("type", "UNKNOWN"), unit.get("line_no", "?"), missing))

    if errors:
        print("⚠️ Units with missing fields:")
        for utype, line_no, fields in errors:
            print(f" - Line {line_no}: {utype}, missing {fields}")
    else:
        print("✅ All units have soldier, category, and class defined.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    edu_path = os.path.join(base_dir, "..", "data", "export_descr_unit.txt")
    edu_path = os.path.normpath(edu_path)

    if not os.path.exists(edu_path):
        raise FileNotFoundError(f"Could not find {edu_path}")

    print(f"🔍 Reading file: {edu_path}")
    units = parse_edu(edu_path)

    # Validate
    validate_units(units)

    # Optional: print units
    for u in units:
        print(f"Unit: {u.get('type')}, Category: {u.get('category')}, Class: {u.get('class')}, "
              f"Soldier: {u.get('soldier_model')}, Number: {u.get('soldier_number')}")
