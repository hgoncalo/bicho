from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

DIRTY_PATH = BASE_DIR / "past" / "dirty"
CLEAN_PATH = BASE_DIR / "past" / "clean"
OUTPUT_PATH = BASE_DIR / "output" / "poisson"
OUTPUT_PATH_REVAMPED = BASE_DIR / "output" / "poisson_revamped"

BASE_COLUMNS = [
    "Div",
    "Date",
    "Time",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR",
    "HTHG",
    "HTAG",
    "HTR",
    "HS",
    "AS",
    "HST",
    "AST",
    "HF",
    "AF",
    "HC",
    "AC",
    "HY",
    "AY",
    "HR",
    "AR"
]

SEASONS = [
    "19_20",
    "20_21",
    "21_22",
    "22_23",
    "23_24",
    "24_25",
    "25_26"
]

POISSON_LEARNING_BIAS = 0.1
POISSON_EWMA = 0.2

POISSON_REVAMPED_LEARNING_BIAS = 0.12
POISSON_REVAMPED_EWMA = 0.15
POISSON_REVAMPED_OD = 1.05

LEAGUE_AVG_SCORED = 1.4
LEAGUE_AVG_AGAINST = 1.2