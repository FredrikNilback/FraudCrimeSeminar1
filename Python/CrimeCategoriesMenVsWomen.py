import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

df = pd.read_csv(r"../CSVs/types_of_crime_by_gender_2019_2024.csv")

def parseCell(cell):
    if pd.isna(cell):
        return (0,0,0,0,0,0,0,0)

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

cleanCategories = [re.sub(r"\s*\[.*?\]\s*$", "", c) for c in categories]

x = np.arange(len(categories))
width = 0.35

plt.figure(figsize=(18, 7))

plt.bar(x - width/2, avgMenConv, width, label="Lagförda män")
plt.bar(x + width/2, avgWomenConv, width, label="Lagförda kvinnor")

plt.xticks(x, cleanCategories, rotation=45, ha="right")
#plt.yscale("log")
plt.ylabel("Genomsnittligt antal lagförda personer per år")
plt.title("Genomsnittliga antalet lagförda personer per år per kategori")
plt.legend()
plt.tight_layout()

plt.savefig(r"../Plots/crime_categories_men_vs_women_convicted.png", dpi=300)
#plt.savefig(r"../Plots/crime_categories_men_vs_women_convicted_log_scale.png", dpi=300)
