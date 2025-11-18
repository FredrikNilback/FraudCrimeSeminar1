import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

def parseAgeCell(cell):
    if (pd.isna(cell)):
        return [0]*5, [0]*5

    pairs = re.findall(r"\[(\d*);(\d*)\]", cell)
    suspects = []
    prosecuted = []
    for a, b in pairs:
        suspects.append(int(a) if a else 0)
        prosecuted.append(int(b) if b else 0)
    return suspects, prosecuted

df = pd.read_csv(r"../CSVs/types_of_crime_by_age_2019_2024.csv")

ageGroups = ["15-17", "18-20", "21-29", "30-49", "50+"]
rows = []

for idx, row in df.iterrows():
    year = int(row["year"])

    ageSus = {age: 0 for age in ageGroups}
    agePro = {age: 0 for age in ageGroups}

    for col in df.columns:
        if (col == "year"):
            continue

        suspects, prosecuted = parseAgeCell(row[col])

        for age, s, p in zip(ageGroups, suspects, prosecuted):
            ageSus[age] += s
            agePro[age] += p

    out = {}
    for age in ageGroups:
        out[f"{year}_suspects_{age}"] = ageSus[age]
        out[f"{year}_prosecuted_{age}"] = agePro[age]

    rows.append(out)

dfWide = pd.DataFrame(rows)
years = sorted({int(col.split("_")[0]) for col in dfWide.columns})

suspectsByAge = {age: [] for age in ageGroups}
prosecutedByAge = {age: [] for age in ageGroups}

for age in ageGroups:
    for year in years:
        s_col = f"{year}_suspects_{age}"
        p_col = f"{year}_prosecuted_{age}"

        suspectsByAge[age].append(dfWide[s_col].sum())
        prosecutedByAge[age].append(dfWide[p_col].sum())

maxY = 0
for age in ageGroups:
    maxY = max(maxY, max(suspectsByAge[age]), max(prosecutedByAge[age]))
maxY = int(maxY * 1.1)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

for i, age in enumerate(ageGroups):
    ax = axes[i]
    sus = np.array(suspectsByAge[age])
    pro = np.array(prosecutedByAge[age])
    x = np.arange(len(years))

    ax.bar(x, sus, width=0.6, color="skyblue", label="Suspected")
    ax.bar(x, pro, width=0.6, color="dodgerblue", alpha=0.7, label="Prosecuted")

    for xi, s, p in zip(x, sus, pro):
        pct = p / s * 100 if s else 0
        ax.text(xi, p / 2, f"{pct:.0f}%", ha="center", va="center",
                color="white", fontsize=10)

    ax.set_title(f"Ålder {age}")
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_ylabel("Antal misstänkta (lagförda)")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, maxY)

fig.delaxes(axes[-1])

plt.suptitle("Misstänkta och lagförda efter åldersgrupp")
plt.tight_layout()
plt.savefig("../Plots/total_crimes_age_groups_suspects_vs_convicted", dpi=300)