import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

df = pd.read_csv(r"../CSVs/types_of_crime_by_gender_2019_2024.csv")

def parseCell(cell):
    if (pd.isna(cell)):
        return (0, 0, 0, 0, 0, 0, 0, 0)

    cell = cell.strip()
    cell = cell.strip("[]")

    menStr, womenStr = cell.split("]:[")
    menStr = menStr.replace("[", "").replace("]", "")
    womenStr = womenStr.replace("[", "").replace("]", "")
    menVals = []
    womenVals = []

    for val in menStr.split(";"):
        menVals.append(0 if val == "NaN" else int(val))
    for val in womenStr.split(";"):
        womenVals.append(0 if val == "NaN" else int(val))

    while (len(menVals) < 4):
        menVals.append(0)
    while (len(womenVals) < 4):
        womenVals.append(0)

    return (
        menVals[0], menVals[1], menVals[2], menVals[3],
        womenVals[0], womenVals[1], womenVals[2], womenVals[3],
    )

categories = [col for col in df.columns if col != "year"]

avgMenConv = []
avgWomenConv = []

for col in categories:
    menConvList = []
    womenConvList = []

    for _, row in df.iterrows():
        menSus, menConv, menElderSus, menElderConv, \
        womenSus, womenConv, womenElderSus, womenElderConv = parseCell(row[col])

        menConvList.append(menConv)
        womenConvList.append(womenConv)

    avgMenConv.append(np.mean(menConvList))
    avgWomenConv.append(np.mean(womenConvList))

femaleShare = []

for m, w in zip(avgMenConv, avgWomenConv):
    total = m + w
    if (total == 0):
        femaleShare.append(0)
    else:
        femaleShare.append(w / total)

x = np.arange(len(categories))

cleanCategories = [re.sub(r"\s*\[.*?\]\s*$", "", c) for c in categories]

plt.figure(figsize=(18, 7))
plt.bar(x, femaleShare, color="purple", alpha=0.7)

overallAvg = np.mean(femaleShare)
plt.axhline(overallAvg, color="black", linestyle="--",
            label=f"Andel kvinnor lagförda genomsnitt ({overallAvg:.2f})")
plt.xticks(x, cleanCategories, rotation=45, ha="right")
plt.ylabel("Andel kvinnor lagförda (0–1)")
plt.title("Relativ andel lagförda kvinnor per brottstyp (2019–2024)")
plt.legend()
plt.tight_layout()
plt.savefig(r"../Plots/female_share_by_crime_type.png", dpi=300)
