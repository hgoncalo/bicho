import pandas as pd
import sys, os
import numpy as np  # Adicionado para backtesting
import itertools  # Adicionado para backtesting
from pathlib import Path
from scipy.stats import poisson

# Configuração do Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.data import utils
# Remove this workaround later

# Fetches data from .csv in order to get all the necessary data for Poisson
def fetchData(file):
    df = pd.read_csv(file)
    home_df = ((df[['Date','HomeTeam','AwayTeam','FTHG','FTAG']]).rename(columns={'HomeTeam':'Team','AwayTeam':'Opponent','FTHG':'GoalsScored','FTAG':'GoalsAgainst'})).assign(IsHome='Y')
    away_df = ((df[['Date','AwayTeam','HomeTeam','FTAG','FTHG']]).rename(columns={'AwayTeam':'Team','HomeTeam':'Opponent','FTAG':'GoalsScored','FTHG':'GoalsAgainst'})).assign(IsHome='N')
    real_df = pd.concat([home_df,away_df])
    return [home_df,away_df,real_df,df]

def fetchCalendar(file):
    df = pd.read_csv(file)
    calendar = df[['Date','HomeTeam','AwayTeam']]
    return calendar

# Team + League (AvgScored: Goals that HOME scores on avg, AvgAgainst: Goals that AWAY scores on avg)
def getAverages(home_df,away_df,real_df):
    hometeam_avg = home_df.groupby('Team').agg(HomeAvgScored=('GoalsScored','mean'),HomeAvgAgainst=('GoalsAgainst','mean'),Matches=('Date','count'))
    awayteam_avg = away_df.groupby('Team').agg(AwayAvgScored=('GoalsScored','mean'),AwayAvgAgainst=('GoalsAgainst','mean'),Matches=('Date','count'))
    avg = (pd.merge(hometeam_avg,awayteam_avg,left_index=True, right_index=True)).rename(columns={'Matches_x':'HomeMatches','Matches_y':'AwayMatches'})
    avg['AvgScored'] = (avg['HomeAvgScored'])*(avg['HomeMatches']/(avg['HomeMatches']+avg['AwayMatches'])) + (avg['AwayAvgScored'])*(avg['AwayMatches']/(avg['HomeMatches']+avg['AwayMatches']))
    avg['AvgAgainst'] = (avg['HomeAvgAgainst'])*(avg['HomeMatches']/(avg['HomeMatches']+avg['AwayMatches'])) + (avg['AwayAvgAgainst'])*(avg['AwayMatches']/(avg['HomeMatches']+avg['AwayMatches']))
    
    # Removed HomeFactor limitation
    avg['HomeFactor'] = ((avg['HomeAvgScored']/avg['AwayAvgScored'].replace(0,np.nan)).fillna(1)).clip(lower=0.8, upper=1.5)
    
    avg['Matches'] = avg['HomeMatches'] + avg['AwayMatches']
    return avg[['AvgScored','AvgAgainst','HomeFactor','Matches']]

def lambdaForces(avg_df):
    teams = avg_df.index.unique()
    lambda_forces = pd.DataFrame({'Team':teams,'LambdaAtt':0,'LambdaDef':0,'HomeFactor':0})

    league_avg_scored = avg_df['AvgScored'].mean()
    league_avg_against = avg_df['AvgAgainst'].mean()

    lambda_forces['LambdaAtt'] = lambda_forces['Team'].map(lambda t: avg_df.loc[t,'AvgScored'] / league_avg_scored)
    lambda_forces['LambdaDef'] = lambda_forces['Team'].map(lambda t: avg_df.loc[t,'AvgAgainst'] / league_avg_against)
    lambda_forces['HomeFactor'] = lambda_forces['Team'].map(lambda t: avg_df.loc[t,'HomeFactor'])
    return [lambda_forces,league_avg_scored,league_avg_against]

# Modified: Accepts 'EWMA,BIAS' as arguments instead of direct import from utils.py, enabling backtesting
def updateLambdaForces(current_round,game,lf,league_avg_scored,league_avg_against, ewma, bias, seasonw):
    updated_lf = lf.copy()

    home_team = game.loc['HomeTeam']
    pred_goals_home = game.loc['PredHomeGoals']
    real_goals_home = game.loc['RealHomeGoals']
    error_home = real_goals_home - pred_goals_home
    old_lf_home = lf.loc[lf['Team'] == home_team]

    away_team = game.loc['AwayTeam']
    pred_goals_away = game.loc['PredAwayGoals']
    real_goals_away = game.loc['RealAwayGoals']
    error_away = real_goals_away - pred_goals_away
    old_lf_away = lf.loc[lf['Team'] == away_team]

    lambda_att_home = real_goals_home / league_avg_scored
    lambda_att_away = real_goals_away / league_avg_scored
    lambda_def_home = real_goals_away / league_avg_against
    lambda_def_away = real_goals_home / league_avg_against

    updated_lf.loc[updated_lf['Team'] == home_team,'LambdaAtt'] = (((ewma * lambda_att_home) + ((1 - ewma) * old_lf_home['LambdaAtt'])) + (bias * error_home))
    updated_lf.loc[updated_lf['Team'] == away_team,'LambdaAtt'] = (((ewma * lambda_att_away) + ((1 - ewma) * old_lf_away['LambdaAtt'])) + (bias * error_away))
    updated_lf.loc[updated_lf['Team'] == home_team,'LambdaDef'] = (((ewma * lambda_def_home) + ((1 - ewma) * old_lf_home['LambdaDef'])) + (bias * error_away))
    updated_lf.loc[updated_lf['Team'] == away_team,'LambdaDef'] = (((ewma * lambda_def_away) + ((1 - ewma) * old_lf_away['LambdaDef'])) + (bias * error_home))

    games_played = current_round / 34

    # changing
    season_weight = seasonw

    numeric_cols = ['LambdaAtt','LambdaDef','HomeFactor']
    lf_mix = updated_lf.copy()
    lf_mix[numeric_cols] = (season_weight * updated_lf[numeric_cols]) + ((1 - season_weight) * lf[numeric_cols])
    return lf_mix

# MODIFICADO: Aceita 'od' (Overall Goals) como argumento
def predictGame(game,lf, od):
    home_team = game.loc['HomeTeam']
    away_team = game.loc['AwayTeam']
    lf_home = lf.loc[lf['Team'] == home_team]
    lf_away = lf.loc[lf['Team'] == away_team]

    if (lf_home.empty):
        lambda_home_att = (lf['LambdaAtt'].mean()) * 0.9
        lambda_home_def = (lf['LambdaDef'].mean()) * 1.1
        home_factor = lf['HomeFactor'].mean()
    else:
        lambda_home_att = lf_home['LambdaAtt'].iloc[0]
        lambda_home_def = lf_home['LambdaDef'].iloc[0]
        home_factor = lf_home['HomeFactor'].iloc[0]

    if (lf_away.empty):
        lambda_away_att = (lf['LambdaAtt'].mean()) * 0.9
        lambda_away_def = (lf['LambdaDef'].mean()) * 1.1
    else:
        lambda_away_att = lf_away['LambdaAtt'].iloc[0]
        lambda_away_def = lf_away['LambdaDef'].iloc[0]

    # modified: removed away_goals, penalizes way too much
    lambda_home = lambda_home_att * lambda_away_def * home_factor * od
    lambda_away = lambda_away_att * lambda_home_def * od

    k = np.arange(0, 10)
    prob_home = poisson.pmf(k, lambda_home)
    prob_away = poisson.pmf(k, lambda_away)

    goals_home = k[np.argmax(prob_home)]
    goals_away = k[np.argmax(prob_away)]
    return goals_home,goals_away

# Modified: accepts 'ewma', 'bias', 'od', 'rf_weight' for backtest
def simulateCalendar(season,season_data,calendar,lf,averages, ewma, bias, od, rf_weight, seasonw, write_file=False):
    lambda_force,league_avg_scored,league_avg_against = lf
    new_lf = lambda_force.copy()

    teams_current_season = calendar['AwayTeam'].unique()

    new_lf = new_lf[new_lf['Team'].isin(teams_current_season)]

    for team in teams_current_season:
        if team not in new_lf['Team'].values:
            new_lf = pd.concat([new_lf, pd.DataFrame([
            {
            'Team': team,
            'LambdaAtt': new_lf['LambdaAtt'].mean(),
            'LambdaDef': new_lf['LambdaDef'].mean(),
            'HomeFactor': new_lf['HomeFactor'].mean()
            }
            ])],ignore_index=True)

    df = season_data[3]
    calendar['PredHomeGoals'] = 0
    calendar['PredAwayGoals'] = 0
    calendar['RealHomeGoals'] = 0
    calendar['RealAwayGoals'] = 0
    calendar['ErrorHomeGoals'] = 0
    calendar['ErrorAwayGoals'] = 0

    # modified: dynamically updates averages at the end of each matchweek
    total_home_goals_so_far = []
    total_away_goals_so_far = []
    dynamic_league_avg_scored = league_avg_scored
    dynamic_league_avg_against = league_avg_against

    games_per_round = 9
    current_games = 0
    current_round = 1
    for id in calendar.index:
        current_games += 1
        if (current_games == games_per_round):
            current_games = 0
            if len(total_home_goals_so_far) > 0:
                # Média real da época até agora
                new_dynamic_avg_scored = np.mean(total_home_goals_so_far)
                new_dynamic_avg_against = np.mean(total_away_goals_so_far)
                
                # Suavization using rf_weight to avoid volability
                weight = rf_weight
                dynamic_league_avg_scored = (weight * new_dynamic_avg_scored) + ((1-weight) * dynamic_league_avg_scored)
                dynamic_league_avg_against = (weight * new_dynamic_avg_against) + ((1-weight) * dynamic_league_avg_against)
            current_round += 1

        game = calendar.loc[id]
        goals_home,goals_away = predictGame(game,new_lf, od)
        
        calendar.loc[id, 'PredHomeGoals'] = goals_home
        calendar.loc[id, 'PredAwayGoals'] = goals_away
        calendar.loc[id, 'RealHomeGoals'] = df.loc[id,'FTHG']
        calendar.loc[id, 'RealAwayGoals'] = df.loc[id,'FTAG']
        calendar.loc[id, 'ErrorHomeGoals'] = calendar.loc[id, 'RealHomeGoals'] - calendar.loc[id, 'PredHomeGoals']
        calendar.loc[id, 'ErrorAwayGoals'] = calendar.loc[id, 'RealAwayGoals'] - calendar.loc[id, 'PredAwayGoals']
        
        game = calendar.loc[id] 
        total_home_goals_so_far.append(game['RealHomeGoals'])
        total_away_goals_so_far.append(game['RealAwayGoals'])
        
        new_lf = updateLambdaForces(current_round,game,new_lf,dynamic_league_avg_scored,dynamic_league_avg_against, ewma, bias, seasonw)

    non_predicted_lf = lambdaForces(averages)
    home_factor_map = non_predicted_lf[0].set_index('Team')['HomeFactor']
    new_lf['HomeFactor'] = new_lf['Team'].map(home_factor_map)

    # modified: added 'write_file' if we want to only use backtesting
    if write_file:
        exportDf(calendar,f"CALENDAR_{season}")
        
    return [new_lf,non_predicted_lf[1],non_predicted_lf[2]] 

def exportDf(df,fileName):
    df.to_csv(f"{utils.OUTPUT_PATH_REVAMPED}/{fileName}.csv")
    return

def start():
    old_season = old_lf = None
    utils.OUTPUT_PATH_REVAMPED.mkdir(parents=True, exist_ok=True)
    
    # now fetches the utils to pass as arguments
    ewma = utils.POISSON_REVAMPED_EWMA
    bias = utils.POISSON_REVAMPED_LEARNING_BIAS
    od = utils.POISSON_REVAMPED_OD 
    rf_weight = utils.POISSON_REVAMPED_RF_WEIGHT
    seasonw = utils.POISSON_REVAMPED_SEASON_WEIGHT
    
    for season in utils.SEASONS:
        file = utils.OUTPUT_PATH_REVAMPED / f"{season}.csv"
        if (file.is_file()):
            old_season = file
            old_lf = [pd.read_csv(utils.OUTPUT_PATH_REVAMPED / f"LF_{season}.csv"),utils.LEAGUE_AVG_SCORED,utils.LEAGUE_AVG_AGAINST]
        else:
            csv_path = utils.CLEAN_PATH / f"{season}.csv"
            if not csv_path.is_file():
                print(f"Ficheiro {csv_path} não encontrado, a saltar.")
                continue

            if (old_season == None):
                season_data = fetchData(csv_path)
                averages = getAverages(season_data[0],season_data[1],season_data[2])
                old_lf = lambdaForces(averages) 
            else:
                calendar = fetchCalendar(csv_path)
                season_data = fetchData(csv_path)
                averages = getAverages(season_data[0],season_data[1],season_data[2])
                old_lf = simulateCalendar(season,season_data,calendar,old_lf,averages,
                                          ewma, bias, od, rf_weight, seasonw, write_file=True) 
            old_season = file
            exportDf(averages,season)
            exportDf(old_lf[0],f"LF_{season}")
    return   

# modified: added backtesting using root mean sequared error (RMSE)
def calculate_rmse(all_calendars):
    all_errors_sq = []
    if not all_calendars: return np.inf 
    for calendar in all_calendars:
        all_errors_sq.extend(calendar['ErrorHomeGoals'] ** 2)
        all_errors_sq.extend(calendar['ErrorAwayGoals'] ** 2)
    if not all_errors_sq: return np.inf
    return np.sqrt(np.mean(all_errors_sq))

# modified: real backtest, using grid_search
def run_backtest():
    ewma_values = [0.05]
    bias_values = [0.05]
    od_values = [1.07]
    rf_weight_values = [0.3]
    seasonw_values = [0.325]
    param_grid = list(itertools.product(ewma_values, bias_values, od_values,rf_weight_values,seasonw_values))
    results = {}

    print(f"Iniciando backtest (Modelo REVAMPED) com {len(param_grid)} combinações...")

    for i, params in enumerate(param_grid):
        ewma, bias, od, rf_weight, seasonw = params
        
        old_lf = None
        all_season_calendars = [] 

        for season in utils.SEASONS:
            csv_path = utils.CLEAN_PATH / f"{season}.csv"
            if not csv_path.is_file(): continue
                
            season_data = fetchData(csv_path) 
            averages = getAverages(season_data[0], season_data[1], season_data[2]) 

            if (old_lf == None):
                old_lf = lambdaForces(averages) 
            else:
                calendar = fetchCalendar(csv_path)
                
                old_lf = simulateCalendar(season, season_data, calendar, old_lf, averages, 
                                          ewma=ewma, bias=bias, od=od, rf_weight=rf_weight,seasonw=seasonw,
                                          write_file=False) 
                
                all_season_calendars.append(calendar) 
        
        # Calculates RMSE
        rmse = calculate_rmse(all_season_calendars)
        results[params] = rmse
        print(f"  {i+1}/{len(param_grid)} | Params (EWMA, BIAS, OD): {params} -> RMSE: {rmse:.4f}")

    if not results:
        print("Backtest não produziu resultados.")
        return

    print("\n--- Backtest Concluído ---")
    sorted_results = sorted(results.items(), key=lambda item: item[1])
    
    print("\nTop 5 Melhores Combinações:")
    for params, rmse in sorted_results[:5]:
        print(f"  Params (EWMA, BIAS, OD): {params} -> RMSE: {rmse:.4f}")

    best_params_tuple, best_rmse = sorted_results[0]
    print(f"\nMelhor RMSE: {best_rmse:.4f}")
    print(f"Melhores Parâmetros (EWMA, BIAS, OD): {best_params_tuple}")
    
    return sorted_results

# Last known RMSE: 1.1591
if __name__ == "__main__":
    # Para correr a simulação normal com os parâmetros do utils.py:
    start() 
    
    # Para encontrar os melhores parâmetros para o novo modelo OTIMIZADO:
    #run_backtest()