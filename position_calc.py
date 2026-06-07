import pandas as pd
import os

DATA_PATH = "data/FPL/2025/gws/"


def getGw(gw_int):
    return pd.read_csv(f"{DATA_PATH}gw_{gw_int}.csv")


# maps for converting BPS points
scoringBpsMap = {
    "FWD": {"GKP": -12, "DEF": -12, "MID": -6, "FWD": 0},
    "MID": {"GKP": -6, "DEF": -6, "MID": 0, "FWD": 6},
    "DEF": {"GKP": 0, "DEF": 0, "MID": 6, "FWD": 12},
    "GKP": {"GKP": 0, "DEF": 0, "MID": 6, "FWD": 12},
}

cleanSheetBpsMap = {
    "FWD": {"GKP": 12, "DEF": 12, "MID": 0, "FWD": 0},
    "MID": {"GKP": 12, "DEF": 12, "MID": 0, "FWD": 0},
    "DEF": {"GKP": 0, "DEF": 0, "MID": -12, "FWD": -12},
    "GKP": {"GKP": 0, "DEF": 0, "MID": -12, "FWD": -12},
}

# maps for converting absolute points
scoringMap = {
    "FWD": {"GKP": 2, "DEF": 2, "MID": 1, "FWD": 0},
    "MID": {"GKP": 1, "DEF": 1, "MID": 0, "FWD": -1},
    "DEF": {"GKP": 0, "DEF": 0, "MID": -1, "FWD": -2},
    "GKP": {"GKP": 0, "DEF": 0, "MID": -1, "FWD": -2},
}

cleanSheetMap = {
    "FWD": {"GKP": 4, "DEF": 4, "MID": 1, "FWD": 0},
    "MID": {"GKP": 3, "DEF": 3, "MID": 0, "FWD": -1},
    "DEF": {"GKP": 0, "DEF": 0, "MID": -3, "FWD": -4},
    "GKP": {"GKP": 0, "DEF": 0, "MID": -3, "FWD": -4},
}
goalsConcededMap = {
    "FWD": {"GKP": -1, "DEF": -1, "MID": 0, "FWD": 0},
    "MID": {"GKP": -1, "DEF": -1, "MID": 0, "FWD": 0},
    "DEF": {"GKP": 0, "DEF": 0, "MID": 1, "FWD": 1},
    "GKP": {"GKP": 0, "DEF": 0, "MID": 1, "FWD": 1},
}


def getGwFixtures(playerID, df):
    return df[df["element"] == playerID]["fixture"].tolist()


def getGwFixtureInfo(df, fixture):
    df = df[df["fixture"] == fixture]
    df = df.set_index("element")
    return df


def recalculateFixtureBonus(df, playerID, newPos):
    oldPos = df.loc[playerID].position
    BPS = df.loc[playerID].bps
    if oldPos == newPos:
        return 0
    BPS += df.loc[playerID].clean_sheets * cleanSheetBpsMap[oldPos][newPos]
    BPS += df.loc[playerID].goals_scored * scoringBpsMap[oldPos][newPos]
    df.loc[playerID, "bps"] = BPS
    try:
        newBonus = (
            df.nlargest(3, "bps", keep="all")["bps"].rank(method="max").loc[playerID]
        )
        return int(newBonus - df.loc[playerID].bonus)
    except KeyError:
        return 0


def recalculateFixturePoints(df, playerID, newPos):
    oldPos = df.loc[playerID].position
    points = df.loc[playerID].total_points
    if oldPos == newPos:
        return 0
    points += df.loc[playerID].clean_sheets * cleanSheetMap[oldPos][newPos]
    points += df.loc[playerID].goals_scored * scoringMap[oldPos][newPos]
    points += (df.loc[playerID].goals_conceded // 2) * goalsConcededMap[oldPos][newPos]
    points += recalculateFixtureBonus(df, playerID, newPos)
    return points


def recalculateTotalPoints(playerID, newPos):
    newPoints = 0
    oldPoints = 0
    available_gws = [
        int(f.replace("gw_", "").replace(".csv", ""))
        for f in os.listdir(DATA_PATH)
        if f.endswith(".csv")
    ]
    for i in sorted(available_gws):
        gw = getGw(i)
        fixtureList = getGwFixtures(playerID, gw)
        for fixture in fixtureList:
            fx = getGwFixtureInfo(gw, fixture)
            newPoints += recalculateFixturePoints(fx, playerID, newPos)
            oldPoints += fx.loc[playerID].total_points
    return {"old": oldPoints, "new": newPoints}


if __name__ == "__main__":
    print(f"Salah (MID to FWD): {recalculateTotalPoints(playerID=381, newPos='FWD')}")
    print(f"Haaland (FWD to MID): {recalculateTotalPoints(playerID=430, newPos='MID')}")
    print(
        f"Van Dijk (DEF to MID): {recalculateTotalPoints(playerID=373, newPos='MID')}"
    )
    print(
        f"O'Reilly (DEF to MID): {recalculateTotalPoints(playerID=411, newPos='MID')}"
    )
