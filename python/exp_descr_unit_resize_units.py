import re
import os

# ---------------------------------------------------------------------
# CONFIG: SMALL (EDU) unit sizes
# ---------------------------------------------------------------------
# Vanilla M2TW multipliers (for reference):
# Small = base, Normal = base*1.25, Large = base*1.875, Huge = base*2.5
SIZE_RULES = {
    ("infantry", "light"): 88,
    ("infantry", "heavy"): 72,
    ("infantry", "missile"): 64,
    ("infantry", "spearmen"): 96,
    ("cavalry", "light"): 40,
    ("cavalry", "heavy"): 32,
    ("cavalry", "missile"): 36,
    ("siege", "missile"): 20,  # fallback for generic artillery
    ("siege", "light"): 40,
}

# Attribute-based overrides (higher priority than category/class)
ATTRIBUTE_RULES = {
    "can_run_amok": 12,    # elephants
    "guncavalry": 32,       # mounted gunpowder
    "gunpowder_unit": 40,   # musket/arquebus infantry
}

MAX_EDU_SIZE = 250  # Engine hard limit

# ---------------------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------------------
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
EDU_PATH = os.path.join(BASE_PATH, "..", "data", "export_descr_unit.txt")
OUT_PATH = os.path.join(BASE_PATH, "..", "data", "export_descr_unit_NEW.txt")

# ---------------------------------------------------------------------
# MAIN PROCESSING
# ---------------------------------------------------------------------
with open(EDU_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Split unit blocks by "type"
parts = re.split(r"(^type\s+)", content, flags=re.MULTILINE)
rebuilt = parts[:1]

# Counters
units_processed = 0
units_skipped = 0
units_no_rule = 0
units_attribute_override = 0

# Regex pattern for soldier line (handles apostrophes, spaces, etc.)
soldier_pattern = r"(\s*soldier\s+[^,]+,\s*)(\d+)"

for i in range(1, len(parts), 2):
    type_header = parts[i]
    unit_block = parts[i + 1]
    full_unit = type_header + unit_block

    # Extract unit name from 'dictionary' field
    dict_match = re.search(r"dictionary\s+([^\s]+)", full_unit)
    unit_name = dict_match.group(1) if dict_match else "UNKNOWN"

    # Extract category, class
    cat_match = re.search(r"category\s+(\w+)", full_unit)
    cls_match = re.search(r"class\s+(\w+)", full_unit)

    # Extract soldier line
    sol_match = re.search(soldier_pattern, full_unit)

    if not (cat_match and cls_match and sol_match):
        print(f"[SKIP] Unit '{unit_name}': missing category/class/soldier line.")
        rebuilt.append(full_unit)
        units_skipped += 1
        continue

    category = cat_match.group(1).lower()
    unit_class = cls_match.group(1).lower()
    old_soldier = int(sol_match.group(2))

    # Extract attributes
    attr_match = re.search(r"attributes\s+(.+)", full_unit, re.IGNORECASE)
    unit_attributes = attr_match.group(1).lower() if attr_match else ""

    # --- Determine new SMALL value ---
    new_small = None

    # 1. Check attribute-based overrides first
    for attr, size in ATTRIBUTE_RULES.items():
        if attr in unit_attributes:
            new_small = min(size, MAX_EDU_SIZE)
            units_attribute_override += 1
            break

    # 2. Fallback to category/class rules
    if new_small is None:
        rule_key = (category, unit_class)
        if rule_key in SIZE_RULES:
            new_small = min(SIZE_RULES[rule_key], MAX_EDU_SIZE)
        else:
            new_small = None

    # --- Apply replacement or skip ---
    if new_small is not None:
        try:
            new_unit = re.sub(
                soldier_pattern,
                lambda m: f"{m.group(1)}{new_small}",
                full_unit
            )
            #print(f"[UPDATE] Unit '{unit_name}': {category}/{unit_class} | "
            #      f"old SMALL={old_soldier} → new SMALL={new_small}")
            rebuilt.append(new_unit)
            units_processed += 1
        except re.error as e:
            print(f"[ERROR] Unit '{unit_name}': regex replacement failed: {e}")
            rebuilt.append(full_unit)
            units_skipped += 1
    else:
        print(f"[NO RULE] Unit '{unit_name}': {category}/{unit_class} not in SIZE_RULES and no attribute override")
        rebuilt.append(full_unit)
        units_no_rule += 1

# --- Write output ---
with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write("".join(rebuilt))

# --- Summary ---
print("\n=== SUMMARY ===")
print(f"Units processed (updated)     : {units_processed}")
print(f"Units skipped (errors)        : {units_skipped}")
print(f"Units with no rule            : {units_no_rule}")
print(f"Units overridden by attribute : {units_attribute_override}")
print("Output written to:", OUT_PATH)
