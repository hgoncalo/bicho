from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

DIRTY_PATH = BASE_DIR / "past" / "dirty"
CLEAN_PATH = BASE_DIR / "past" / "clean"
OUTPUT_PATH = BASE_DIR / "output"

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
    "24_25"
]

POISSON_LEARNING_BIAS = 0.1
POISSON_EWMA = 0.2