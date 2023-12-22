import requests
import json

# URL du JSON
url = "https://cdn.nba.com/static/json/staticData/scheduleLeagueV2.json"

# Obtenir le contenu JSON de l'URL
response = requests.get(url)
data = response.json()

# Liste des matchs avec les informations demandées
matches_info = []

for game_date in data['leagueSchedule']['gameDates']:
    for game in game_date['games']:
        match_info = {
            'gameDateTimeUTC': game['gameDateTimeUTC'],
            'weekNumber': game['weekNumber'],
            'arenaName': game['arenaName'],
            'seriesText': game['seriesText'],
            'hometeamName': game['homeTeam']['teamName'],
            'awayteamName': game['awayTeam']['teamName'],
        }
        matches_info.append(match_info)


teams_dict = {
    1: "Lakers",
    2: "Heat",
    3: "Warriors",
    4: "Celtics",
    5: "Spurs",
    6: "Knicks",
    7: "Pistons",
    8: "Magic",
    9: "Suns",
    10: "Pacers",
    11: "Jazz",
    12: "Trail Blazers",
    13: "Raptors",
    14: "Mavericks",
    15: "Bucks",
    16: "Thunder",
    17: "Bulls",
    18: "Pelicans",
    19: "Rockets",
    20: "Kings",
    21: "Clippers",
    22: "Cavaliers",
    23: "Hawks",
    24: "Grizzlies",
    25: "Nuggets",
    26: "Hornets",
    27: "76ers",
    28: "Wizards",
    29: "Timberwolves",
    30: "Nets"
}

for i in matches_info:
    if (i['hometeamName'] == teams_dict[1] or i['awayteamName'] == teams_dict[1]):
        print(i['hometeamName'] + " vs " + i['awayteamName'] + " " + i['gameDateTimeUTC'])