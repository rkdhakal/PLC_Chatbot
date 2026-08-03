"""
Dataset Builder — Rebuilds clean dataset from all 3 raw source files.
Sources: Modbus, PtP, USS
Output:  final_preprocessed_v2.csv + data_quality_audit.csv
"""

import pandas as pd
import re
from datetime import datetime, timezone

RAW_SOURCES = {
    "modbus": "../../Data/siemens_error_messages -modbus.csv",
    "ptp":    "../../Data/siemens_error_messages -PtP.csv",
    "uss":    "../../Data/siemens_error_messages-USS.csv",
}
OUTPUT_PATH = "final_preprocessed_v2.csv"
AUDIT_PATH  = "data_quality_audit.csv"

audit = []
now   = datetime.now(timezone.utc).isoformat()


def log(action, row_index, field, before, after, reason):
    audit.append({
        "timestamp": now,
        "action":    action,
        "row_index": row_index,
        "field":     field,
        "before":    str(before),
        "after":     str(after),
        "reason":    reason,
    })


def clean_error_code(code):
    code = str(code).strip()
    code = re.sub(r'\s*1\)$', '', code)
    code = code.strip()
    return code.upper()


def clean_text(text):
    if pd.isna(text) or str(text).strip() in ('', '-', '‑', '–'):
        return ''
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def load_source(path, source_name):
    df = pd.read_csv(path)
    # Normalise column names
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    rename = {
        'error_code': 'error_code',
        'error code': 'error_code',
        'category':   'category',
        'description':'description',
        'remedy':     'remedy',
        'error_type': 'error_type',
        'error type': 'error_type',
    }
    df = df.rename(columns={c: rename.get(c, c) for c in df.columns})

    # Forward-fill category (scraped tables have merged category cells)
    if 'category' in df.columns:
        df['category'] = df['category'].ffill()
    else:
        df['category'] = source_name.upper()

    df['source_file'] = source_name
    df['ingested_at'] = now
    print(f"  Loaded {len(df)} rows from {source_name}")
    return df


# ── 1. Load all sources ───────────────────────────────────────────────────────
print("[1/5] Loading raw sources...")
frames = []
for name, path in RAW_SOURCES.items():
    df = load_source(path, name)
    frames.append(df)

combined = pd.concat(frames, ignore_index=True)
print(f"  Combined: {len(combined)} rows total")
log("LOAD", "all", "source", "3 files", f"{len(combined)} rows", "Initial load from Modbus, PtP, USS sources")

# ── 2. Drop rows with no error code ──────────────────────────────────────────
print("[2/5] Dropping rows with no error code...")
before = len(combined)
combined = combined[combined['error_code'].notna()].copy()
dropped = before - len(combined)
if dropped:
    log("DROP_NO_CODE", "multiple", "error_code", f"{before} rows", f"{len(combined)} rows", f"Removed {dropped} rows with null error_code")
print(f"  Dropped {dropped} rows with no error code → {len(combined)} remaining")

# ── 3. Clean error codes ──────────────────────────────────────────────────────
print("[3/5] Cleaning error codes...")
dirty_mask = combined['error_code'].astype(str).str.contains(r'\s|\)', regex=True, na=False)
for idx in combined[dirty_mask].index:
    original = combined.at[idx, 'error_code']
    fixed    = clean_error_code(original)
    combined.at[idx, 'error_code'] = fixed
    log("FIX_ERROR_CODE", idx, "error_code", original, fixed, "Removed trailing ' 1)' suffix and normalised case")

combined['error_code'] = combined['error_code'].apply(clean_error_code)
print(f"  Fixed {dirty_mask.sum()} dirty error codes")

# ── 4. Clean text fields ──────────────────────────────────────────────────────
print("[4/5] Cleaning text fields...")
for col in ['description', 'remedy', 'category']:
    if col in combined.columns:
        combined[col] = combined[col].apply(clean_text)

# ── 5. Deduplicate ────────────────────────────────────────────────────────────
print("[5/5] Deduplicating...")
before = len(combined)
dup_codes = combined[combined.duplicated(subset=['error_code'], keep=False)]['error_code'].unique()
print(f"  {len(dup_codes)} error codes appear in multiple rows — merging...")

clean_rows = []
for code in combined['error_code'].unique():
    group = combined[combined['error_code'] == code]

    if len(group) == 1:
        row = group.iloc[0].to_dict()
    else:
        base = group.iloc[0].to_dict()
        # Merge unique categories, descriptions, remedies
        cats  = " | ".join(g for g in group['category'].unique()   if g)
        descs = " | ".join(g for g in group['description'].unique() if g)
        rems  = " | ".join(g for g in group['remedy'].unique()      if g)
        etypes= " | ".join(g for g in group['error_type'].unique()  if g)
        srcs  = " | ".join(g for g in group['source_file'].unique() if g)

        base['category']    = cats
        base['description'] = descs
        base['remedy']      = rems
        base['error_type']  = etypes
        base['source_file'] = srcs

        log("MERGE_DUPLICATES", str(group.index.tolist()), "error_code",
            f"{len(group)} rows", "1 merged row",
            f"'{code}' appeared in {len(group)} rows across categories")
        row = base

    # Build rich content column for embedding
    row['content'] = (
        f"error_code: {row['error_code']}\n"
        f"category: {row.get('category','')}\n"
        f"error_type: {row.get('error_type','')}\n"
        f"description: {row.get('description','')}\n"
        f"remedy: {row.get('remedy','')}"
    ).strip()

    clean_rows.append(row)

clean_df = pd.DataFrame(clean_rows).reset_index(drop=True)
print(f"  Deduplicated: {before} → {len(clean_df)} records")

# ── Final validation ──────────────────────────────────────────────────────────
for col in ['error_code', 'description', 'remedy']:
    nulls = (clean_df[col] == '') | clean_df[col].isna()
    if nulls.sum():
        log("WARN_EMPTY", "multiple", col, f"{nulls.sum()} empty", "unfilled", "Manual review recommended")
        print(f"  [WARN] {nulls.sum()} empty values in '{col}'")

# Keep only needed columns in clean order
cols = ['error_code', 'category', 'description', 'remedy', 'error_type', 'source_file', 'ingested_at', 'content']
clean_df = clean_df[[c for c in cols if c in clean_df.columns]]

# ── Save ──────────────────────────────────────────────────────────────────────
clean_df.to_csv(OUTPUT_PATH, index=False)
audit_df = pd.DataFrame(audit)
audit_df.to_csv(AUDIT_PATH, index=False)

print(f"\n{'='*55}")
print("  DATASET BUILD REPORT")
print(f"{'='*55}")
print(f"  Source files       : {len(RAW_SOURCES)} (Modbus, PtP, USS)")
print(f"  Raw rows loaded    : {before}")
print(f"  Clean records      : {len(clean_df)}")
print(f"  Unique error codes : {clean_df['error_code'].nunique()}")
print(f"  Error types        : {sorted(clean_df['error_type'].dropna().unique())}")
print(f"  Audit entries      : {len(audit_df)}")
print(f"  Output             : {OUTPUT_PATH}")
print(f"  Audit log          : {AUDIT_PATH}")
print(f"{'='*55}")
