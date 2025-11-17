import re
import os

# --- REGEX for main recruit_pool structure ---
# This allows optional conditional clauses at the end.
recruit_pool_pattern = re.compile(
    r'^recruit_pool\s+"[^"]+"\s+'       # recruit_pool "Unit Name"
    r'\d+\s+'                           # pool max
    r'[\d.]+\s+'                        # replenish rate
    r'\d+\s+'                           # starting amount
    r'\d+'                              # experience or turns
    r'(?:\s+.+)?$'                      # anything else allowed (validated later)
)

# --- Clause regexes for detailed validation ---
CLAUSE_PATTERNS = {
    "requires_factions": re.compile(r'requires\s+factions\s+\{[^\}]*\}'),
    "hidden_resource": re.compile(r'(?:and\s+)?hidden_resource\s+\w+'),
    "region_religion": re.compile(r'(?:and\s+)?region_religion\s+\w+\s+\d+'),
    "event_counter": re.compile(r'(?:and\s+)?event_counter\s+\w+(?:\s+\d+)?'),
    "not_event_counter": re.compile(r'(?:and\s+)?not_event_counter\s+\w+(?:\s+\d+)?'),
}


def validate_faction_block(line):
    """Check for missing commas or braces inside faction lists."""
    errors = []
    m = re.search(r'requires\s+factions\s+\{([^\}]*)\}', line)
    if not m:
        errors.append("Missing closing '}' in faction list.")
        return errors

    faction_block = m.group(1).strip()

    # Check for missing commas (word followed by word with no comma)
    tokens = [t.strip() for t in faction_block.split()]
    for i in range(len(tokens) - 1):
        if "," not in tokens[i] and not tokens[i].endswith(","):
            # Only flag if both are word-like tokens
            if re.match(r'^[a-z_]+$', tokens[i]) and re.match(r'^[a-z_]+$', tokens[i + 1]):
                errors.append("Missing comma between factions in list.")
                break

    return errors


def validate_recruit_pool_line(line, line_num):
    errors = []

    # 1️⃣ Base format
    if not recruit_pool_pattern.match(line):
        errors.append("Invalid base recruit_pool format.")
        return errors

    # 2️⃣ Faction list checks
    if "requires factions" in line:
        errors.extend(validate_faction_block(line))

    # 3️⃣ Check all clause types
    remaining = line
    # Remove known base fields so we only check clauses
    remaining = re.sub(r'^recruit_pool\s+"[^"]+"\s+\d+\s+[\d.]+\s+\d+\s+\d+', "", remaining).strip()

    if remaining:
        clauses = remaining.split("  ")
        for clause in clauses:
            c = clause.strip()
            if not c:
                continue
            valid = any(p.match(c) for p in CLAUSE_PATTERNS.values())
            if not valid:
                errors.append(f"Unrecognized or malformed clause: '{c}'")

    return errors


def validate_edb(file_path):
    errors = []
    braces = 0

    with open(file_path, encoding="utf-8") as f:
        for line_num, raw_line in enumerate(f, 1):
            line = raw_line.strip()
            if not line or line.startswith(";"):
                continue

            braces += line.count("{")
            braces -= line.count("}")

            if line.startswith("recruit_pool"):
                for err in validate_recruit_pool_line(line, line_num):
                    errors.append(f"Line {line_num}: {err}\n  {line}")

    if braces != 0:
        errors.append(f"Brace mismatch detected: {braces:+d} unclosed braces total.")

    # Output summary
    if errors:
        print("❌ Validation errors found:")
        for e in errors:
            print(" -", e)
    else:
        print("✅ No syntax errors detected. File looks structurally valid!")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    edb_path = os.path.join(base_dir, "..", "data", "export_descr_buildings.txt")
    edb_path = os.path.normpath(edb_path)

    print(f"🔍 Validating file: {edb_path}")
    validate_edb(edb_path)
