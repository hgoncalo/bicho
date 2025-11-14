from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

DIRTY_PATH = BASE_DIR / "past" / "dirty"
CLEAN_PATH = BASE_DIR / "past" / "clean"
OUTPUT_PATH = BASE_DIR / "output" / "poisson"
OUTPUT_PATH_REVAMPED = BASE_DIR / "output" / "poisson_revamped"

USED_MODEL = "poisson_revamped"
LEAGUE_ID = "P1"
LEAGUE_AGENDA_URL = "https://www.zerozero.pt/competicao/liga-portuguesa"
WEB_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

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

POISSON_LEARNING_BIAS = 0.05
POISSON_EWMA = 0.05
POISSON_OD = 1.05


# Médias fallback para o modelo de GOLOS (baseadas no teu utils antigo)
LEAGUE_AVG_SCORED = 1.4 
LEAGUE_AVG_AGAINST = 1.2


# Deves ter também os teus parâmetros otimizados anteriores
POISSON_REVAMPED_LEARNING_BIAS = 0.05
POISSON_REVAMPED_EWMA = 0.05
POISSON_REVAMPED_OD = 1.07
POISSON_REVAMPED_RF_WEIGHT = 0.3
POISSON_REVAMPED_SEASON_WEIGHT = 0.325