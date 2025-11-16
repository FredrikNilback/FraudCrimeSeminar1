import pandas as pd
import re
import matplotlib.pyplot as plt

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

df = pd.read_csv(r"../CSVs/types_of_crime_by_gender_2019_2024.csv")
df = df.rename(columns=lambda x: re.sub(r"\[.*?\]", "", x))

categories = [c for c in df.columns if c != "year"]
elderProsecutions = {c: 0 for c in categories}
totalProsecutions = {c: 0 for c in categories}
hasElderData = {c: False for c in categories}

for _, row in df.iterrows():
    for cat in categories:
        parsed = parseBlock(str(row[cat]))
        if (parsed == None):
            continue
        if (parsed["menElderProsecuted"] != None or parsed["womenElderProsecuted"] != None):
            hasElderData[cat] = True

        B = parsed["menProsecuted"] or 0
        F = parsed["womenProsecuted"] or 0
        D = parsed["menElderProsecuted"] or 0
        H = parsed["womenElderProsecuted"] or 0

        totalProsecutions[cat] += B + F
        elderProsecutions[cat] += D + H

elderShare = {
    cat: (elderProsecutions[cat] / totalProsecutions[cat] if totalProsecutions[cat] > 0 else 0) for cat in categories
}

plotDf = pd.Series(elderShare)
plotDf = plotDf[[cat for cat in plotDf.index if hasElderData[cat]]].sort_values(ascending=False)

plt.figure(figsize=(12, 6))
ax = plotDf.plot(kind="bar")
plt.title("Andel äldre/funktionsnedsatta som blir utsatta för bedrägeri per kategori")
ax.set_ylabel("Andel äldre/funktionsnedsatta som blir utsatta")
ax.yaxis.set_label_coords(-0.03, 0.1)
plt.tight_layout()
plt.savefig(r"../Plots/types_of_crimes_against_elders.png", dpi=300)
