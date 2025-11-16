import pandas as pd
import re
import matplotlib.pyplot as plt

def parseReported(block):
    block = block.strip()
    match = re.match(r'\[(\d+):', block)
    if (not match):
        return None
    return int(match.group(1))

reportedDf = pd.read_csv(r"../CSVs/total_crimes_reported_2019_2024.csv")
reportedDf = reportedDf.rename(columns=lambda x: re.sub(r'\[.*?\]', '', x))
categories = [c for c in reportedDf.columns if c != "year"]

reportedTotals = {c: 0 for c in categories}
for _, row in reportedDf.iterrows():
    for cat in categories:
        val = parseReported(str(row[cat]))
        if (val != None):
            reportedTotals[cat] += val

genderDf = pd.read_csv(r"../CSVs/types_of_crime_by_gender_2019_2024.csv")
genderDf = genderDf.rename(columns=lambda x: re.sub(r"\[.*?\]", "", x))
genderCategories = [c for c in genderDf.columns if c != "year"]
genderCategories = [c for c in genderCategories if "Ej specificerad" not in c.strip()]

totalSuspects = {c: 0 for c in genderCategories}
totalProsecuted = {c: 0 for c in genderCategories}

def parseBlock(block):
    block = block.strip()
    match = re.match(r'\[\[([^]]+)\]:\[([^]]+)\]\]', block)
    if (not match):
        return None
    menRaw, womenRaw = match.groups()
    menVals = [None if x == "NaN" else int(x) for x in menRaw.split(';')]
    womenVals = [None if x == "NaN" else int(x) for x in womenRaw.split(';')]

    while (len(menVals) < 4):
        menVals.append(0)
    while (len(womenVals) < 4):
        womenVals.append(0)

    return {
        "menTotalSuspects": menVals[0],
        "menProsecuted": menVals[1],
        "menElderSuspects": menVals[2],
        "menElderProsecuted": menVals[3],
        "womenTotalSuspects": womenVals[0],
        "womenProsecuted": womenVals[1],
        "womenElderSuspects": womenVals[2],
        "womenElderProsecuted": womenVals[3]
    }


for _, row in genderDf.iterrows():
    for cat in genderCategories:
        parsed = parseBlock(str(row[cat]))
        if (parsed == None):
            continue
        B = parsed["menTotalSuspects"] or 0
        F = parsed["womenTotalSuspects"] or 0
        P = parsed["menProsecuted"] or 0
        Q = parsed["womenProsecuted"] or 0

        totalSuspects[cat] += B + F
        totalProsecuted[cat] += P + Q

plotDf = pd.DataFrame({
    "Rapporterade brott": pd.Series({k: reportedTotals[k] for k in genderCategories}),
    "Antal misstänkta": pd.Series(totalSuspects),
    "Antal lagförda": pd.Series(totalProsecuted)
})
plotDf = plotDf.sort_values("Rapporterade brott", ascending=False)

plt.figure(figsize=(14, 7))
ax = plotDf.plot(kind="bar")
plt.title("Uppklarningsstatistik genomsnitt per kategori (2019-2024)")
plt.ylabel("Antal fall")
#plt.yscale("log")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(r"../Plots/reported_vs_suspects_prosecuted.png", dpi=300)
#plt.savefig(r"../Plots/reported_vs_suspects_prosecuted_log_scale.png", dpi=300)
