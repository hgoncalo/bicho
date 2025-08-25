import pandas as pd
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.data import utils
# Remove this workaround later
from pathlib import Path
from scipy.stats import poisson
import numpy as np

# Make sure the file is correct, else kaput
# Fetches data from .csv in order to get all the necessary data for Poisson, also creates double entry for each game (Home and Away view), easier to group by Team
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
    avg['HomeFactor'] = ((avg['HomeAvgScored']/avg['AwayAvgScored'].replace(0,np.nan)).fillna(1)).clip(lower=0.85, upper=1.15)
    avg['Matches'] = avg['HomeMatches'] + avg['AwayMatches']
    return avg[['AvgScored','AvgAgainst','HomeFactor','Matches']]

def lambdaForces(avg_df):
    teams = avg_df.index.unique()
    lambda_forces = pd.DataFrame({'Team':teams,'LambdaAtt':0,'LambdaDef':0,'HomeFactor':0})

    league_avg_scored = avg_df['AvgScored'].mean()
    league_avg_against = avg_df['AvgAgainst'].mean()

    # Currently using AvgScored/LeagueAvgScored and AvgAgainst/LeagueAvgAgainst, seems to provide better results than divided by LeagueAvgAll
    lambda_forces['LambdaAtt'] = lambda_forces['Team'].map(lambda t: avg_df.loc[t,'AvgScored'] / league_avg_scored)
    lambda_forces['LambdaDef'] = lambda_forces['Team'].map(lambda t: avg_df.loc[t,'AvgAgainst'] / league_avg_against)
    lambda_forces['HomeFactor'] = lambda_forces['Team'].map(lambda t: avg_df.loc[t,'HomeFactor'])
    return [lambda_forces,league_avg_scored,league_avg_against]

def updateLambdaForces(current_round,game,lf,league_avg_scored,league_avg_against):
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

    # Calculates Lambdas
    lambda_att_home = real_goals_home / league_avg_scored
    lambda_att_away = real_goals_away / league_avg_scored
    lambda_def_home = real_goals_away / league_avg_against
    lambda_def_away = real_goals_home / league_avg_against

    # Update LambdaForces according to the game and historic Lambdas and Error Tracking
    # Team's LambdaAtt improves if model underestimated the team (error_home > 0), LambdaDef improves if model overestimated the opponent (error_away < 0)
    # Remember: The bigger LambdaAtt and the smaller LambdaDef, the better
    updated_lf.loc[updated_lf['Team'] == home_team,'LambdaAtt'] = (((utils.POISSON_EWMA * lambda_att_home) + ((1 - utils.POISSON_EWMA) * old_lf_home['LambdaAtt'])) + (utils.POISSON_LEARNING_BIAS * error_home))
    updated_lf.loc[updated_lf['Team'] == away_team,'LambdaAtt'] = (((utils.POISSON_EWMA * lambda_att_away) + ((1 - utils.POISSON_EWMA) * old_lf_away['LambdaAtt'])) + (utils.POISSON_LEARNING_BIAS * error_away))
    updated_lf.loc[updated_lf['Team'] == home_team,'LambdaDef'] = (((utils.POISSON_EWMA * lambda_def_home) + ((1 - utils.POISSON_EWMA) * old_lf_home['LambdaDef'])) + (utils.POISSON_LEARNING_BIAS * error_away))
    updated_lf.loc[updated_lf['Team'] == away_team,'LambdaDef'] = (((utils.POISSON_EWMA * lambda_def_away) + ((1 - utils.POISSON_EWMA) * old_lf_away['LambdaDef'])) + (utils.POISSON_LEARNING_BIAS * error_home))

    # Mix the models (so the beggining of a season doesen't kaput the whole model) -> eight games should be enough to get everything stable
    games_played = current_round / 34
    season_weight = max(min((games_played)*4.5,1),0.75) # a game should always be worth between [0.75,1], depending if it's the season start or if it's already finished
    numeric_cols = ['LambdaAtt','LambdaDef','HomeFactor']
    lf_mix = updated_lf.copy()
    lf_mix[numeric_cols] = (season_weight * updated_lf[numeric_cols]) + ((1 - season_weight) * lf[numeric_cols])
    return lf_mix

def predictGame(game,lf):
    home_team = game.loc['HomeTeam']
    away_team = game.loc['AwayTeam']
    lf_home = lf.loc[lf['Team'] == home_team]
    lf_away = lf.loc[lf['Team'] == away_team]

    if (lf_home.empty):
        # Use adjusted means in teams that just got promoted
        lambda_home_att = (lf['LambdaAtt'].mean()) * 0.9
        lambda_home_def = (lf['LambdaDef'].mean()) * 1.1
        home_factor = lf['HomeFactor'].mean()
    else:
        lambda_home_att = lf_home['LambdaAtt'].iloc[0]
        lambda_home_def = lf_home['LambdaDef'].iloc[0]
        home_factor = lf_home['HomeFactor'].iloc[0]

    if (lf_away.empty):
        # Use adjusted means in teams that just got promoted
        lambda_away_att = (lf['LambdaAtt'].mean()) * 0.9
        lambda_away_def = (lf['LambdaDef'].mean()) * 1.1
        away_factor = lf['HomeFactor'].mean()
    else:
        lambda_away_att = lf_away['LambdaAtt'].iloc[0]
        lambda_away_def = lf_away['LambdaDef'].iloc[0]
        away_factor = lf_away['HomeFactor'].iloc[0]

    #equivalente a LambdaA
    #lambda(Home) = lambdaAtt(Home) * lambdaDef(Away) * HomeFactor(Home) 
    #lambda(Away) = lambdaAtt(Home) * lambdaDef(Away) * (2 - HomeFactor(Away))
    lambda_home = lambda_home_att * lambda_away_def * home_factor
    lambda_away = lambda_away_att * lambda_home_def * (2 - away_factor)

    # At max 9 goals (in order to make an accurate enough prediction)
    k = np.arange(0, 10)
    prob_home = poisson.pmf(k, lambda_home)
    prob_away = poisson.pmf(k, lambda_away)

    goals_home = k[np.argmax(prob_home)]
    goals_away = k[np.argmax(prob_away)]
    return goals_home,goals_away

def simulateCalendar(season,season_data,calendar,lf,averages):
    lambda_force,league_avg_scored,league_avg_against = lf
    new_lf = lambda_force.copy()

    teams_current_season = calendar['AwayTeam'].unique()

    # Removes the demoted teams from the LF
    new_lf = new_lf[new_lf['Team'].isin(teams_current_season)]

    # Updates the LF with the promoted teams
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

    games_per_round = 9
    current_games = 0
    current_round = 1
    for id in calendar.index:
        current_games += 1
        if (current_games == games_per_round):
            current_games = 0
            current_round += 1

        game = calendar.loc[id]
        goals_home,goals_away = predictGame(game,new_lf)
        calendar.loc[id, 'PredHomeGoals'] = goals_home
        calendar.loc[id, 'PredAwayGoals'] = goals_away
        calendar.loc[id, 'RealHomeGoals'] = df.loc[id,'FTHG']
        calendar.loc[id, 'RealAwayGoals'] = df.loc[id,'FTAG']
        calendar.loc[id, 'ErrorHomeGoals'] = calendar.loc[id, 'RealHomeGoals'] - calendar.loc[id, 'PredHomeGoals']
        calendar.loc[id, 'ErrorAwayGoals'] = calendar.loc[id, 'RealAwayGoals'] - calendar.loc[id, 'PredAwayGoals']
        game = calendar.loc[id] # update, because game is a view and not the document (it doesent update by itself)
        #print(game)
        new_lf = updateLambdaForces(current_round,game,new_lf,league_avg_scored,league_avg_against)

    # No fim da season, update HomeFactors, ver LF real e exportar calendário
    non_predicted_lf = lambdaForces(averages)

    home_factor_map = non_predicted_lf[0].set_index('Team')['HomeFactor']
    new_lf['HomeFactor'] = new_lf['Team'].map(home_factor_map)

    exportDf(calendar,f"CALENDAR_{season}")
    return [new_lf,non_predicted_lf[1],non_predicted_lf[2]] #league averages

def exportDf(df,fileName):
    df.to_csv(f"{utils.OUTPUT_PATH}/{fileName}.csv")
    return

def start():
    old_season = old_lf = None
    for s in range(0,len(utils.SEASONS)):
        season = utils.SEASONS[s]
        file = utils.OUTPUT_PATH / f"{season}.csv"
        if (file.is_file()):
            #exists and we've already got the final league averages
            old_season = file
            old_lf = [pd.read_csv(utils.OUTPUT_PATH / f"LF_{season}.csv"),utils.LEAGUE_AVG_SCORED,utils.LEAGUE_AVG_AGAINST]
        else:
            csv_path = utils.CLEAN_PATH / f"{season}.csv"
            if (old_season == None):
                #cold start
                season_data = fetchData(csv_path)
                averages = getAverages(season_data[0],season_data[1],season_data[2])
                old_lf = lambdaForces(averages) # cold starts LF
            else:
                #new season to calculate/predict
                calendar = fetchCalendar(csv_path)
                season_data = fetchData(csv_path)
                averages = getAverages(season_data[0],season_data[1],season_data[2])
                old_lf = simulateCalendar(season,season_data,calendar,old_lf,averages) # dynamically updates LF (returns LF from current season, updated)
            old_season = file
            exportDf(averages,season)
            exportDf(old_lf[0],f"LF_{season}")
    return   

if __name__ == "__main__":
    start()

#TODO:
# - Fazer backtest com os BIAS/EWMA do utils.py
# - Update HomeFactor, pois precisa de ser depois da season...
# - Fix Equipas Promovidas não aparecerem no LF, aliás: Aparecem no Averages mas estamos a exportar o OldLF