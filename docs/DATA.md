
# Data

## CSV Parameter Documentation
Explanation about how the data was parsed, its types and descriptions. These fields are the most important to the analysis and may be subject to change.


| Parameter | Type     | Description |
|-----------|----------|-------------|
| Div       | string   | League Division |
| Date      | string   | Match Date (dd/mm/yy) |
| Time      | string   | Time of match kick off |
| HomeTeam  | string   | Home Team |
| AwayTeam  | string   | Away Team |
| FTHG, HG  | integer  | Full Time Home Team Goals |
| FTAG, AG  | integer  | Full Time Away Team Goals |
| FTR, Res  | string   | Full Time Result (H=Home Win, D=Draw, A=Away Win) |
| HTHG      | integer  | Half Time Home Team Goals |
| HTAG      | integer  | Half Time Away Team Goals |
| HTR       | string   | Half Time Result (H=Home Win, D=Draw, A=Away Win) |
| HS        | integer  | Home Team Shots |
| AS        | integer  | Away Team Shots |
| HST       | integer  | Home Team Shots on Target |
| AST       | integer  | Away Team Shots on Target |
| HHW       | integer  | Home Team Hit Woodwork |
| AHW       | integer  | Away Team Hit Woodwork |
| HC        | integer  | Home Team Corners |
| AC        | integer  | Away Team Corners |
| HF        | integer  | Home Team Fouls Committed |
| AF        | integer  | Away Team Fouls Committed |
| HFKC      | integer  | Home Team Free Kicks Conceded |
| AFKC      | integer  | Away Team Free Kicks Conceded |
| HO        | integer  | Home Team Offsides |
| AO        | integer  | Away Team Offsides |
| HY        | integer  | Home Team Yellow Cards |
| AY        | integer  | Away Team Yellow Cards |
| HR        | integer  | Home Team Red Cards |
| AR        | integer  | Away Team Red Cards |



## Cleaning the data

Using *clean_data.py*, we could transform the original ("dirty") files, mostly provided by [Football-Data.co.uk](https://www.football-data.co.uk/portugalm.php), into more efficient and concise information. How each function is handled is described here:

| Function | Description |
|-----------|-------------|
| getData()| Fetches the "dirty" data from the stipulated folder |
| cleanData()| Removes unnecessary "fodder" from the original data |