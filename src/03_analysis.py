import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/life_tables_long.csv")
df["mid_year"] = df["start_year"] + 1   # centre of each 3-year period
FIRST = df.loc[df["start_year"].idxmin(), "period"]
LATEST = df.loc[df["start_year"].idxmax(), "period"]

def save(fig, name):
    fig.savefig(f"outputs/{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

# Chart 1: life expectancy at birth and at 65 over time
fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharex=True)
for ax, age in zip(axes, [0, 65]):
    for sex, g in df[df.age == age].groupby("sex"):
        ax.plot(g.mid_year, g.ex, label=sex)
    ax.set(title=f"Life expectancy at {'birth' if age == 0 else 'age 65'}",
           xlabel="Middle year of 3-year period", ylabel="Years")
axes[0].legend()
save(fig, "01_life_expectancy_trend")

# Chart 2: female-male gap at birth
gap = (df[df.age == 0].pivot(index="mid_year", columns="sex", values="ex")
       .eval("Female - Male"))
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(gap.index, gap.values)
ax.set(title="Female minus male life expectancy at birth",
       xlabel="Middle year of 3-year period", ylabel="Gap (years)")
save(fig, "02_sex_gap")

# Chart 3: the mortality curve, first vs latest period, log scale
fig, ax = plt.subplots(figsize=(7, 4.5))
for period, style in [(FIRST, "--"), (LATEST, "-")]:
    for sex, g in df[df.period == period].groupby("sex"):
        ax.plot(g.age, g.qx, style, color="tab:blue" if sex == "Female" else "tab:orange", label=f"{sex} {period}")
ax.set_yscale("log")
ax.set(title="Probability of dying within a year, by age",
       xlabel="Age", ylabel="qx (log scale)")
ax.legend()
save(fig, "03_mortality_curve")

# Gompertz fit: log(mx) = a + b * age, ages 40-90
print(f"Gompertz fit, {LATEST}, ages 40-90")
sub = df[(df.period == LATEST) & df.age.between(40, 90)]
for sex, g in sub.groupby("sex"):
    b, a = np.polyfit(g.age, np.log(g.mx), 1)
    print(f"  {sex}: b = {b:.4f}, mortality doubles every {np.log(2) / b:.1f} years")