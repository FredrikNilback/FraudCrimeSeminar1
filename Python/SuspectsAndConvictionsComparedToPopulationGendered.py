import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

dfOld = pd.read_csv(r"../CSVs/types_of_crime_by_gender_2010_2018.csv")
dfNew = pd.read_csv(r"../CSVs/types_of_crime_by_gender_2019_2024.csv")
dfPop = pd.read_csv(r"../CSVs/total_population.csv")


def getPopulation(year):
    return dfPop[str(year)].values[0]


def parseOld(cell):
    cell = cell.strip("[]")
    menStr, womenStr = cell.split("]:[")
    menStr = menStr.replace("[","").replace("]","")
    womenStr = womenStr.replace("[","").replace("]","")
    men = [int(x) for x in menStr.split(";")]
    women = [int(x) for x in womenStr.split(";")]
    return men[0], men[1], women[0], women[1]


def parseNew(cell):
    if pd.isna(cell):
        return 0, 0, 0, 0
    cell = cell.strip("[]")
    menStr, womenStr = cell.split("]:[")
    menStr = menStr.replace("[","").replace("]","")
    womenStr = womenStr.replace("[","").replace("]","")
    men = [int(x) if x != "NaN" else 0 for x in menStr.split(";")]
    women = [int(x) if x != "NaN" else 0 for x in womenStr.split(";")]
    return men[0], men[1], women[0], women[1]


yearsOld = [str(y) for y in range(2010, 2019)]
yearsNew = [str(y) for y in range(2019, 2025)]

menSuspects = []
menConvicted = []
womenSuspects = []
womenConvicted = []

for col in dfOld.columns:
    match = re.search(r"(\d{4})", col)
    if (not match):
        continue
    totalMenSus, totalMenConv, totalWomenSus, totalWomenConv = 0, 0, 0, 0
    for _, row in dfOld.iterrows():
        mSus, mConv, wSus, wConv = parseOld(row[col])
        totalMenSus += mSus
        totalMenConv += mConv
        totalWomenSus += wSus
        totalWomenConv += wConv
    menSuspects.append(totalMenSus)
    menConvicted.append(totalMenConv)
    womenSuspects.append(totalWomenSus)
    womenConvicted.append(totalWomenConv)

for year in yearsNew:
    totalMenSus, totalMenConv, totalWomenSus, totalWomenConv = 0, 0, 0, 0
    row = dfNew[dfNew["year"] == int(year)].iloc[0]
    for col in dfNew.columns:
        if (col == "year"):
            continue
        mSus, mConv, wSus, wConv = parseNew(row[col])
        totalMenSus += mSus
        totalMenConv += mConv
        totalWomenSus += wSus
        totalWomenConv += wConv
    menSuspects.append(totalMenSus)
    menConvicted.append(totalMenConv)
    womenSuspects.append(totalWomenSus)
    womenConvicted.append(totalWomenConv)

allYears = yearsOld + yearsNew

popTotal = [getPopulation(y) for y in allYears]
menSusPct = [s / p * 100 for s, p in zip(menSuspects, popTotal)]
menConvPct = [c / p * 100 for c, p in zip(menConvicted, popTotal)]
womenSusPct = [s / p * 100 for s, p in zip(womenSuspects, popTotal)]
womenConvPct = [c / p * 100 for c, p in zip(womenConvicted, popTotal)]

x = np.arange(len(allYears))
barWidth = 0.35

plt.figure(figsize=(14, 6))
barsMenSus = plt.bar(x - barWidth / 2, menSusPct, barWidth, label="Misstänkta män", color="skyblue")
barsMenConv = plt.bar(x - barWidth / 2, menConvPct, barWidth, label="Lagförda män", color="dodgerblue", alpha=0.7)
barsWomenSus = plt.bar(x + barWidth / 2, womenSusPct, barWidth, label="Misstänkta kvinnor", color="lightcoral")
barsWomenConv = plt.bar(x + barWidth / 2, womenConvPct, barWidth, label="Lagförda kvinnor", color="red", alpha=0.7)

for bar, sus, con in zip(barsMenConv, menSuspects, menConvicted):
    pct = con / sus * 100 if sus else 0
    plt.text(bar.get_x() + bar.get_width() / 2, menConvPct[barsMenConv.index(bar)] / 2, f"{pct:.0f}%", 
             ha="center", va="center", color="white", fontsize=10)

for bar, sus, con in zip(barsWomenConv, womenSuspects, womenConvicted):
    pct = con / sus * 100 if sus else 0
    plt.text(bar.get_x() + bar.get_width() / 2, womenConvPct[barsWomenConv.index(bar)] / 2, f"{pct:.0f}%", 
             ha="center", va="center", color="white", fontsize=10)

plt.xticks(x, allYears)
plt.ylabel("% av total befolkning")
plt.xlabel("År")
plt.title("Misstänkta och lagförda som procent av total befolkning, könsfördelning 2010–2024")
plt.legend()
plt.tight_layout()
plt.savefig("../Plots/men_vs_women_crimes_as_percentage_of_total_population.png", dpi=300)
