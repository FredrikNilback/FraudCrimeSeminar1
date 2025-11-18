import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
df.columns = df.columns.str.strip()

ageGroups = ["15-17", "18-20", "21-29", "30-49", "50+"]
categories = [col for col in df.columns if col != "year" and not col.startswith("Ej specificerad")]
cleanCategories = [re.sub(r"\[.*?\]", "", cat).strip() for cat in categories]

totals = {age: {cat: {"sus": 0, "pro": 0, "n": 0} for cat in categories} for age in ageGroups}

for idx, row in df.iterrows():
    for cat in categories:
        suspects, prosecuted = parseAgeCell(row[cat])
        for age, s, p in zip(ageGroups, suspects, prosecuted):
            totals[age][cat]["sus"] += s
            totals[age][cat]["pro"] += p
            totals[age][cat]["n"] += 1

avgSus = {age: [] for age in ageGroups}
avgPro = {age: [] for age in ageGroups}

for age in ageGroups:
    for cat in categories:
        n = totals[age][cat]["n"]
        if (n == 0):
            avgSus[age].append(0)
            avgPro[age].append(0)
        else:
            avgSus[age].append(totals[age][cat]["sus"] / n)
            avgPro[age].append(totals[age][cat]["pro"] / n)

fig, axes = plt.subplots(2, 3, figsize=(22, 12))
axes = axes.flatten()

maxY = max(max(avgSus[age] + avgPro[age]) for age in ageGroups) * 1.15

x = np.arange(len(cleanCategories))
barWidth = 0.6

for i, age in enumerate(ageGroups):
    ax = axes[i]
    sus = np.array(avgSus[age])
    pro = np.array(avgPro[age])
    ax.bar(x, sus, width=barWidth, color="skyblue", label="Suspected")
    ax.bar(x, pro, width=barWidth, color="dodgerblue", alpha=0.7, label="Prosecuted")

    for xi, s, p in zip(x, sus, pro):
        pct = (p / s * 100) if s else 0
        ax.text(xi, p / 2, f"{pct:.0f}%", ha="center", va="center", color="white", fontsize=9)

    ax.set_title(f"Ålder {age}")
    ax.set_xticks(x)
    ax.set_xticklabels(cleanCategories, rotation=60, ha="right")
    ax.set_ylim(0, maxY)
    ax.grid(axis="y", alpha=0.3)

fig.delaxes(axes[-1])

plt.tight_layout()
plt.suptitle(
    "Medelvärde per kategori (misstänkta & lagförda) för varje åldersgrupp",
    y=1.03, fontsize=16
)
plt.savefig("../Plots/crime_categories_age_groups.png", dpi=300)
