import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

oldCsvPath = r"../CSVs/types_of_crime_by_gender_2010_2018.csv"
newCsvPath = r"../CSVs/types_of_crime_by_gender_2019_2024.csv"

dfOld = pd.read_csv(oldCsvPath)
dfNew = pd.read_csv(newCsvPath)

def parseCellOld(cell):
    cell = cell.strip("[]")
    menPart, womenPart = cell.split("]:[")
    menPart = menPart.replace("[","").replace("]","")
    womenPart = womenPart.replace("[","").replace("]","")
    
    menNums = [int(x) if x != "NaN" else 0 for x in menPart.split(";")]
    womenNums = [int(x) if x != "NaN" else 0 for x in womenPart.split(";")]
    return menNums + womenNums


def parseCellNew(cell):
    if (pd.isna(cell)):
        return [0, 0, 0, 0]
    cell = cell.strip("[]")
    menPart, womenPart = cell.split("]:[")
    menPart = menPart.replace("[","").replace("]","")
    womenPart = womenPart.replace("[","").replace("]","")
    
    menNums = [int(x) if x != "NaN" else 0 for x in menPart.split(";")]
    womenNums = [int(x) if x != "NaN" else 0 for x in womenPart.split(";")]
    return [menNums[0], menNums[1], womenNums[0], womenNums[1]]


oldYearCols = [col for col in dfOld.columns if re.search(r"\d{4}", col)]
for col in oldYearCols:
    year = re.search(r"\d{4}", col).group()
    dfOld[[f"{year}MenSuspects",
           f"{year}MenConvicted",
           f"{year}WomenSuspects",
           f"{year}WomenConvicted"]] = dfOld[col].apply(parseCellOld).apply(pd.Series)

dfOld = dfOld.drop(columns=oldYearCols)

newRows = []
for idx, row in dfNew.iterrows():
    year = row["year"]
    menSusTotal, menConvTotal, womenSusTotal, womenConvTotal = 0, 0, 0, 0
    for col in dfNew.columns:
        if (col == "year"):
            continue
        menSus, menConv, womenSus, womenConv = parseCellNew(row[col])
        menSusTotal += menSus
        menConvTotal += menConv
        womenSusTotal += womenSus
        womenConvTotal += womenConv
    newRows.append({
        f"{year}MenSuspects": menSusTotal,
        f"{year}MenConvicted": menConvTotal,
        f"{year}WomenSuspects": womenSusTotal,
        f"{year}WomenConvicted": womenConvTotal
    })

dfNewWide = pd.DataFrame(newRows)

dfAll = pd.concat([dfOld, dfNewWide], ignore_index=True)
years = sorted({int(re.search(r"\d{4}", col).group()) for col in dfAll.columns if "MenSuspects" in col})

menSuspects = dfAll[[f"{y}MenSuspects" for y in years]].sum()
menConvicted = dfAll[[f"{y}MenConvicted" for y in years]].sum()
womenSuspects = dfAll[[f"{y}WomenSuspects" for y in years]].sum()
womenConvicted = dfAll[[f"{y}WomenConvicted" for y in years]].sum()

x = np.arange(len(years))
barWidth = 0.45

plt.figure(figsize=(12,6))
barsMenSus = plt.bar(x - barWidth/2, menSuspects, barWidth, label="Misstänkta män", color="skyblue")
barsMenConv = plt.bar(x - barWidth/2, menConvicted, barWidth, label="Lagförda män", color="dodgerblue", alpha=0.7)
barsWomenSus = plt.bar(x + barWidth/2, womenSuspects, barWidth, label="Misstänkta kvinnor", color="lightcoral")
barsWomenConv = plt.bar(x + barWidth/2, womenConvicted, barWidth, label="Lagförda kvinnor", color="red", alpha=0.7)

for bar, sus, con in zip(barsMenConv, menSuspects, menConvicted):
    pct = con / sus * 100 if sus else 0
    plt.text(bar.get_x() + bar.get_width()/2, con/2, f"{pct:.0f}%", ha="center", va="center", color="white", fontsize=10)

for bar, sus, con in zip(barsWomenConv, womenSuspects, womenConvicted):
    pct = con / sus * 100 if sus else 0
    plt.text(bar.get_x() + bar.get_width()/2, con/2, f"{pct:.0f}%", ha="center", va="center", color="white", fontsize=10)

plt.xticks(x, years)
plt.xlabel("År")
plt.ylabel("Antal misstänkta (varav lagförda)")
plt.title("Misstänkta och lagförda. Könsfördelning 2010-2024")
plt.legend()
plt.tight_layout()
plt.savefig("../Plots/total_crimes_men_vs_women_suspects_vs_convicted.png", dpi=300)
