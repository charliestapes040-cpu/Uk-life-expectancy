import sqlite3
import pandas as pd
from pathlib import Path
Path("outputs").mkdir(exist_ok=True)
df = pd.read_csv("data/processed/life_tables_long.csv")
con = sqlite3.connect("data/processed/life_tables.db")
df.to_sql("life_tables", con, if_exists="replace", index=False)

FIRST, LATEST = "1980-1982", "2022-2024"   # check these match your sheet names

queries = {
    "Life expectancy at birth and at 65": """
        SELECT period, sex, age, ROUND(ex, 1) AS ex
        FROM life_tables
        WHERE age IN (0, 65)
        ORDER BY start_year, sex, age;
    """,
    "Female-male gap at birth": """
        SELECT period,
               ROUND(MAX(CASE WHEN sex = 'Female' THEN ex END)
                   - MAX(CASE WHEN sex = 'Male' THEN ex END), 1) AS gap_years
        FROM life_tables
        WHERE age = 0
        GROUP BY period, start_year
        ORDER BY start_year;
    """,
    "Gain since the first period": f"""
        SELECT a.sex, a.age,
               ROUND(a.ex, 1) AS ex_first,
               ROUND(b.ex, 1) AS ex_latest,
               ROUND(b.ex - a.ex, 1) AS gain_years
        FROM life_tables AS a
        JOIN life_tables AS b
          ON a.sex = b.sex AND a.age = b.age
        WHERE a.period = '{FIRST}' AND b.period = '{LATEST}'
          AND a.age IN (0, 65, 85)
        ORDER BY a.sex, a.age;
    """,
}

for title, sql in queries.items():
    print(f"\n=== {title} ===")
    print(pd.read_sql(sql, con).to_string(index=False))

con.close()