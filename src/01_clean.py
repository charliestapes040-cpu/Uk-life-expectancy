import re
import pandas as pd
from pathlib import Path
Path("data/processed").mkdir(parents=True, exist_ok=True)
RAW = "data/raw/nltuk198020223.xlsx"   # your downloaded file
OUT = "data/processed/life_tables_long.csv"

sheets = pd.read_excel(RAW, sheet_name=None, header=None)
print("Sheets found:", list(sheets))

frames = []
for name, raw in sheets.items():
    # Keep only the period sheets, e.g. "2022-2024"
    if not re.fullmatch(r"\d{4}\s*[-–]\s*\d{4}", name.strip()):
        continue

    # Find the heading row: the row containing the word "age"
    is_age = raw.apply(lambda col: col.astype(str).str.strip().str.lower() == "age")
    header_row = is_age.any(axis=1).idxmax()
    age_cols = [i for i, hit in enumerate(is_age.loc[header_row]) if hit]

    # Males are the first block of six columns, females the second
    for sex, start in zip(["Male", "Female"], age_cols):
        block = raw.iloc[header_row + 1:, start:start + 6].copy()
        block.columns = ["age", "mx", "qx", "lx", "dx", "ex"]
        block = block.apply(pd.to_numeric, errors="coerce").dropna()
        block["sex"] = sex
        block["period"] = name.strip()
        block["start_year"] = int(name.strip()[:4])
        frames.append(block)

df = pd.concat(frames, ignore_index=True)
df["age"] = df["age"].astype(int)

# --- Quality checks: stop if anything looks wrong ---
assert df["qx"].between(0, 1).all(), "qx outside 0-1"
assert (df.loc[df["age"] == 0, "lx"] == 100000).all(), "lx at age 0 should be 100,000"
assert df.groupby(["period", "sex"]).size().eq(101).all(), "expected ages 0-100"

df.to_csv(OUT, index=False)
print(f"Saved {len(df):,} rows covering {df['period'].nunique()} periods")
print(df[(df.age == 0) & (df.start_year == df.start_year.max())][["period", "sex", "ex"]])