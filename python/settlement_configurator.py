#!/usr/bin/env python3
"""
apply_settlement_configurations.py

Safe, brace-aware replacement of settlement blocks in descr_strat.txt
- Matches 'settlement { ... }' and 'settlement castle { ... }' blocks (handles nested braces)
- Replaces whole blocks using templates from settlement_configurations/
- Creates a timestamped backup of the original descr_strat.txt
- Produces descr_strat_modified.txt (does not overwrite original)
- Detailed logging to console and apply_settlement_configurations.log

Folder assumptions (relative to this script):
- settlement_configurations/
    - settlement_configurations.csv
    - <template>.txt files (templates may be full blocks or inner fragments)
- ../data/world/maps/campaign/imperial_campaign/descr_strat.txt
"""

import csv
import os
import re
import logging
import datetime
import shutil

# ---------------------------
# Setup paths & logging
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "settlement_configurations")
CSV_PATH = os.path.join(CONFIG_DIR, "settlement_configurations.csv")

DESCR_STRAT_PATH = os.path.join(
    BASE_DIR,
    "..", "data", "world", "maps", "campaign", "imperial_campaign",
    "descr_strat.txt"
)
OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "..", "data", "world", "maps", "campaign", "imperial_campaign",
    "descr_strat_modified.txt"
)

LOG_PATH = os.path.join(BASE_DIR, "apply_settlement_configurations.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, mode="w", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logging.info("=== Starting Settlement Configuration Script ===")
logging.info(f"BASE_DIR: {BASE_DIR}")
logging.info(f"CONFIG_DIR: {CONFIG_DIR}")
logging.info(f"CSV_PATH: {CSV_PATH}")
logging.info(f"DESCR_STRAT_PATH: {DESCR_STRAT_PATH}")

# ---------------------------
# Utility: find matching brace (handles nested braces)
# ---------------------------
def find_matching_brace(text: str, open_pos: int) -> int:
    """
    Given text and the index of an opening brace '{', return the index of the matching closing brace '}'.
    Returns -1 if no matching brace is found.
    """
    depth = 0
    for i in range(open_pos, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
    return -1

# ---------------------------
# Load CSV mappings (with duplicate detection)
# ---------------------------
region_to_template = {}
duplicates = []
csv_count = 0

if not os.path.isfile(CSV_PATH):
    logging.error(f"CSV mapping file not found: {CSV_PATH}")
    raise SystemExit(1)

with open(CSV_PATH, "r", encoding="utf-8", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for row_no, row in enumerate(reader, start=1):
        # skip empty / malformed rows
        if not row or len(row) < 2:
            logging.debug(f"[CSV] Skipping empty/malformed row {row_no}: {row}")
            continue
        region = row[0].strip()
        templ = row[1].strip()
        if region == "" or templ == "":
            logging.debug(f"[CSV] Skipping empty-region/template at row {row_no}")
            continue
        template_filename = templ + ".txt"
        csv_count += 1
        if region in region_to_template:
            duplicates.append(region)
            logging.warning(f"[CSV DUPLICATE] Region '{region}' appears multiple times; last will be used (row {row_no})")
        region_to_template[region] = template_filename

logging.info(f"Loaded {len(region_to_template)} unique region->template mappings from CSV (rows processed: {csv_count})")
if duplicates:
    logging.info(f"CSV duplicates detected for {len(duplicates)} regions (examples): {duplicates[:10]}")

# ---------------------------
# Load templates
# ---------------------------
templates = {}
if not os.path.isdir(CONFIG_DIR):
    logging.error(f"Configuration directory not found: {CONFIG_DIR}")
    raise SystemExit(1)

for fn in os.listdir(CONFIG_DIR):
    if not fn.lower().endswith(".txt"):
        continue
    if fn == os.path.basename(CSV_PATH):
        continue
    full = os.path.join(CONFIG_DIR, fn)
    try:
        with open(full, "r", encoding="utf-8") as fh:
            templates[fn] = fh.read()
    except Exception as e:
        logging.error(f"Error reading template {fn}: {e}")

logging.info(f"Loaded {len(templates)} template files from {CONFIG_DIR}")

# ---------------------------
# Load original descr_strat.txt & backup
# ---------------------------
if not os.path.isfile(DESCR_STRAT_PATH):
    logging.error(f"descr_strat.txt not found: {DESCR_STRAT_PATH}")
    raise SystemExit(1)

# create a timestamped backup
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = os.path.join(BASE_DIR, f"descr_strat_backup_{timestamp}.txt")
shutil.copy2(DESCR_STRAT_PATH, backup_path)
logging.info(f"Backup of original descr_strat.txt saved to: {backup_path}")

with open(DESCR_STRAT_PATH, "r", encoding="utf-8") as f:
    original_text = f.read()

# ---------------------------
# Find settlement blocks (settlement { ... } and settlement castle { ... })
# We must find the position of the 'settlement' keyword then the opening brace and balance braces.
# ---------------------------
blocks = []  # list of dicts: {start, end, block_text, region, block_type}
pattern = re.compile(r"\bsettlement(?:\s+castle)?\s*\{", flags=re.IGNORECASE)

for m in pattern.finditer(original_text):
    start_keyword = m.start()  # start of 'settlement'
    open_brace_pos = original_text.find("{", m.end() - 1)
    if open_brace_pos == -1:
        logging.warning(f"Found 'settlement' at index {start_keyword} but could not find opening brace.")
        continue
    close_brace_pos = find_matching_brace(original_text, open_brace_pos)
    if close_brace_pos == -1:
        logging.warning(f"No matching closing brace for settlement starting at index {start_keyword}. Skipping.")
        continue
    block_text = original_text[start_keyword:close_brace_pos + 1]
    # extract region name (allow letters, numbers, underscore, hyphen)
    region_match = re.search(r"region\s+([A-Za-z0-9_\-]+)", block_text, flags=re.IGNORECASE)
    region_name = region_match.group(1) if region_match else None
    block_type = "settlement castle" if re.match(r"\bsettlement\s+castle\b", block_text, flags=re.IGNORECASE) else "settlement"
    blocks.append({
        "start": start_keyword,
        "end": close_brace_pos + 1,
        "text": block_text,
        "region": region_name,
        "type": block_type
    })

logging.info(f"Detected {len(blocks)} settlement blocks in descr_strat.txt")

# Build lookup of regions found and detect duplicates in descr_strat
region_occurrences = {}
for b in blocks:
    r = b["region"]
    if r:
        region_occurrences.setdefault(r, []).append(b)
    else:
        logging.warning("A settlement block without a region was found (will be left unchanged).")

# ---------------------------
# Plan replacements
# ---------------------------
replacements = []   # list of (start, end, new_text)
applied = []
skipped = []
missing_templates = []
for b in blocks:
    region = b["region"]
    if not region:
        skipped.append((None, "no_region", b))
        continue

    if region not in region_to_template:
        logging.warning(f"[SKIP] No CSV mapping found for region: {region}")
        skipped.append((region, "no_csv", b))
        continue

    template_filename = region_to_template[region]
    if template_filename not in templates:
        logging.warning(f"[SKIP] Template file '{template_filename}' referenced for region {region} but file not present in {CONFIG_DIR}")
        missing_templates.append((region, template_filename))
        skipped.append((region, "no_template", b))
        continue

    template_text = templates[template_filename]
    # Ensure template is a full settlement block. If not, wrap it using the block type found in the original.
    # Heuristic: treat as full block if it starts with 'settlement' (case-insensitive) and contains braces.
    trimmed = template_text.strip()
    is_full_block = bool(re.match(r"(?i)^\s*settlement(?:\s+castle)?\b", trimmed) and "{" in trimmed and "}" in trimmed)
    if not is_full_block:
        # wrap
        header = b["type"]  # either 'settlement' or 'settlement castle'
        wrapped = f"{header}\n{{\n{template_text.rstrip()}\n}}\n"
        new_block = wrapped.replace("INSERT_PROVINCE", region)
        logging.info(f"[WRAP] Template '{template_filename}' for region {region} did not contain a full block — wrapped using '{header}'")
    else:
        new_block = template_text.replace("INSERT_PROVINCE", region)

    # ensure the new_block has balanced braces (quick sanity check)
    open_count = new_block.count("{")
    close_count = new_block.count("}")
    if open_count != close_count:
        logging.error(f"[ERROR] Template replacement for region {region} would produce unbalanced braces (opens={open_count}, closes={close_count}). Skipping this region.")
        skipped.append((region, "unbalanced_template", b))
        continue

    replacements.append((b["start"], b["end"], new_block))
    applied.append((region, template_filename))

# ---------------------------
# Warn about CSV entries that didn't match any region in descr_strat
# ---------------------------
csv_regions_not_found = [r for r in region_to_template.keys() if r not in region_occurrences]
if csv_regions_not_found:
    logging.warning(f"{len(csv_regions_not_found)} regions listed in CSV were not found in descr_strat.txt (examples: {csv_regions_not_found[:10]})")

# ---------------------------
# Perform replacements (build output by slicing — safe against index shifts)
# ---------------------------
# sort replacements by start index
replacements_sorted = sorted(replacements, key=lambda x: x[0])

if replacements_sorted:
    output_parts = []
    last_pos = 0
    for start, end, new_text in replacements_sorted:
        # append original chunk before this block
        output_parts.append(original_text[last_pos:start])
        # append new replacement block
        output_parts.append(new_text)
        last_pos = end
    # append remainder of file
    output_parts.append(original_text[last_pos:])
    modified_text = "".join(output_parts)
else:
    logging.info("No replacements to perform. Writing original file to modified path unchanged.")
    modified_text = original_text

# ---------------------------
# Write output file
# ---------------------------
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(modified_text)

logging.info(f"Modified descr_strat saved to: {OUTPUT_PATH}")

# ---------------------------
# Summary logging
# ---------------------------
logging.info("=== Summary ===")
logging.info(f"Total settlement blocks detected: {len(blocks)}")
logging.info(f"Total unique regions in descr_strat: {len(region_occurrences)}")
logging.info(f"Total mappings in CSV: {len(region_to_template)}")
logging.info(f"Total templates available: {len(templates)}")
logging.info(f"Total applied replacements: {len(applied)}")
logging.info(f"Total skipped: {len(skipped)}")
if missing_templates:
    logging.info(f"Missing template files referenced: {len(missing_templates)} (examples: {missing_templates[:10]})")
if csv_regions_not_found:
    logging.info(f"CSV regions not found in descr_strat: {len(csv_regions_not_found)} (examples: {csv_regions_not_found[:10]})")
if duplicates:
    logging.info(f"CSV duplicates detected (count example): {len(duplicates)} (examples: {duplicates[:10]})")

logging.info("=== Finished ===")
