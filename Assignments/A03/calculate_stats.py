import json
import os,sys
import pprint as pp
from process_files import openFileJson


def getSeason(fname):
    #Gets game-id out of file name
    gameid,ext = os.path.basename(fname).split('.')

    #Year is first 4 characters
    year = int(gameid[:4])
    #Month is next 2 characters
    month = int(gameid[4:6])

    #If Jan. or Feb., then season is of previous year
    if month == 1 or month == 2:
        year = year - 1
       
    return year

def writePlayerInfo():
    #Empty dictionary
    players = {}

    #Opens a file for writing
    g = open("player_info.json","w")
    
    #Opens file containing file paths from game_data
    with open('files.txt') as f:
        #Read every file path
        for line in f:
            #Truncates empty character at end of line
            line = line[:27]

            #Gets file data
            data = openFileJson(line)
            
            #Old season
            oldseason = 2009
            #Get current season year
            year = getSeason(line)
            newseason = False
            #If new season
            if oldseason != year:
                newseason = True
                oldseason = year

            # pull out the game id and game data
            for gameid,gamedata in data.items():
                if gameid != 'nextupdate':
                    # go straight for the drives
                    for driveid,drivedata in gamedata['drives'].items():
                        if driveid != 'crntdrv':
                            for playid,playdata in drivedata['plays'].items():
                                for playerid, playerdata in playdata['players'].items():
                                    for info in playerdata:
                                        if playerid != '0':
                                            #If player is not in dictionary
                                            if playerid not in players:
                                                players[playerid] = {}
                                                players[playerid]['Name'] = info['playerName'] 
                                                #Teams played for since 2009
                                                players[playerid]['Teams'] = []
                                                players[playerid]['Teams'].append(info['clubcode']) 
                                                #Teams played for with year as key
                                                players[playerid]['TeamInfo'] = {}
                                                players[playerid]['TeamInfo'][year] = []
                                                players[playerid]['TeamInfo'][year].append(info['clubcode'])     
                                                players[playerid]['RushYards'] = []
                                                players[playerid]['PassYards'] = []
                                                players[playerid]['FieldGoals'] = []
                                                if info['statId'] == 10:
                                                    players[playerid]['RushYards'].append(info['yards'])
                                                if info['statId'] == 15:
                                                    players[playerid]['PassYards'].append(info['yards'])
                                                if info['statId'] == 70:
                                                    players[playerid]['FieldGoals'].append(info['yards'])
                                            #If player already in dicitionary    
                                            else:   
                                                #If player is playing for new team
                                                if info['clubcode'] not in players[playerid]['Teams']:
                                                    players[playerid]['Teams'].append(info['clubcode'])
                                                #If its a new season create list for season year
                                                if newseason:
                                                    players[playerid]['TeamInfo'][year] = []  
                                                #If playing for new team in same year
                                                if info['clubcode'] not in players[playerid]['TeamInfo'][year]:               
                                                    players[playerid]['TeamInfo'][year].append(info['clubcode'])
                                                if info['statId'] == 10:
                                                    players[playerid]['RushYards'].append(info['yards'])
                                                if info['statId'] == 15:
                                                    players[playerid]['PassYards'].append(info['yards'])
                                                if info['statId'] == 70:
                                                    players[playerid]['FieldGoals'].append(info['yards'])

     #Writes all game IDs
    g.write(json.dumps(players))

def writeTeamInfo():
    teams = {}

    #Opens a file for writing
    g = open("team_info.json","w")

    abbr = openFileJson('./team_abbrev.json')

    #Opens file containing file paths from game_data
    with open('files.txt') as f:
        #Read every file path
        for line in f:
            #Truncates empty character at end of line
            line = line[:27]

            #Gets file data
            data = openFileJson(line)

            # pull out the game id and game data
            for gameid,gamedata in data.items():
                if gameid != 'nextupdate':        
                    #Get home and away teams 
                    home = gamedata['home']['abbr']
                    away = gamedata['away']['abbr'] 
                    #Check for correct abbreviation  
                    home = abbr[home]                
                    away = abbr[away]

                    #If team not in dictionary, add them
                    if home not in teams:
                        teams[home] = {}
                        teams[home]['penalties'] = 0
                        teams[home]['penalty yards'] = 0
                        teams[home]['wins'] = 0
                        teams[home]['losses'] = 0
                    teams[home]['penalties'] = teams[home]['penalties'] + gamedata['home']['stats']['team']['pen']
                    teams[home]['penalty yards'] = teams[home]['penalty yards'] + gamedata['home']['stats']['team']['penyds']
                    if away not in teams:
                        teams[away] = {}
                        teams[away]['penalties'] = 0
                        teams[away]['penalty yards'] = 0
                        teams[away]['wins'] = 0
                        teams[away]['losses'] = 0
                    teams[away]['penalties'] = teams[away]['penalties'] + gamedata['away']['stats']['team']['pen']
                    teams[away]['penalty yards'] = teams[away]['penalty yards'] + gamedata['away']['stats']['team']['penyds']

                    if gamedata['home']['score']['T'] > gamedata['away']['score']['T']:
                        teams[home]['wins'] = teams[home]['wins'] + 1
                        teams[away]['losses'] = teams[away]['losses'] + 1
                    elif gamedata['home']['score']['T'] < gamedata['away']['score']['T']:
                        teams[away]['wins'] = teams[away]['wins'] + 1
                        teams[home]['losses'] = teams[home]['losses'] + 1

     #Writes all game IDs
    g.write(json.dumps(teams))


def getPlayersWithMostTeams():
    players = []
    data = openFileJson('./player_info.json')
    
    max_key = max(data, key= lambda x: len(set(data[x]['Teams']))) 
    
    size = len(data[max_key]['Teams'])
    for playerid,playerdata in data.items():
        if len(playerdata['Teams']) == size:
            players.append(playerdata['Name'])
    return players, size

def getPlayersWithMostTeamsInSingleYear():
    players = []
    data = openFileJson('./player_info.json')

    size = 1
    for playerid,playerdata in data.items():           
        for year,yeardata in playerdata['TeamInfo'].items():
            if len(yeardata) > size:
                size = len(yeardata)
                tup = (playerdata['Name'],size, year)
                players.append(tup)

    players = list(filter(lambda x: x[1] == size, players))
    return players
                  
def getPlayerMostNegativeRush():
    players = []
    data = openFileJson('./player_info.json')
    
    lowest = 0
    for playerid,playerdata in data.items():   
        if playerdata['RushYards']:
            for yards in  playerdata['RushYards']:
                if yards != None and yards <= lowest:
                    lowest = yards
                    tup = (playerdata['Name'],lowest)
                    players.append(tup)

    players = list(filter(lambda x: x[1] == lowest, players))
    return players

def getPlayerMostNegativeRushes():
    players = {}
    data = openFileJson('./player_info.json')
    
    for playerid,playerdata in data.items():   
        for yards in playerdata['RushYards']:
            if yards != None and yards < 0:
                if playerid not in players:
                    players[playerid] = 1
                else:
                    players[playerid] = players[playerid] + 1 
    #pp.pprint(sorted(players.values(), reverse=True))

    highest_count = players[max(players, key=players.get)]
    player_list = []
    for k in players:
        if players[k] == highest_count:
            tup = (data[k]['Name'], players[k])
            player_list.append(tup)       
    return player_list

def getPlayerMostNegativePasses():
    players = {}
    data = openFileJson('./player_info.json')
    
    for playerid,playerdata in data.items():   
        for yards in playerdata['PassYards']:
            if yards != None and yards < 0:
                #print(playerdata['Name'])
                if playerid not in players:
                    players[playerid] = 1
                else:
                    players[playerid] = players[playerid] + 1 
    #pp.pprint(sorted(players.values()))

    highest_count = players[max(players, key=players.get)]
    player_list = []
    for k in players:
        if players[k] == highest_count:
            tup = (data[k]['Name'], players[k])
            player_list.append(tup)
          
    return player_list

def getTeamMostPenalties():
    team = []

    data = openFileJson('./team_info.json')

    most = data[max(data, key= lambda x: data[x]['penalties'])]['penalties']

    for t, tdata in data.items():
        if tdata['penalties'] == most:
            tup = (t,most)
            team.append(tup)

    return team

def getTeamMostPenaltyYards():
    team = []

    data = openFileJson('./team_info.json')

    most = data[max(data, key= lambda x: data[x]['penalty yards'])]['penalty yards']

    for t, tdata in data.items():
        if tdata['penalty yards'] == most:
            tup = (t,most)
            team.append(tup)
    return team

def getHighestWinLossRatio():
    teams = []

    data = openFileJson('./team_info.json')

    max_key = max(data, key= lambda x: data[x]['wins']/data[x]['losses'])
    max_wlr = data[max_key]['wins'] / data[max_key]['losses']

    for t,tdata in data.items():
        ratio = tdata['wins']/tdata['losses']
        if ratio == max_wlr:
            tup = (t,ratio)
            teams.append(tup)
    
    return teams

def getWinLossRatio(team):
    data = openFileJson('./team_info.json')

    ratio = data[team]['wins']/data[team]['losses']

    return ratio

def getPenalties(team):
    data = openFileJson('./team_info.json')

    pens = data[team]['penalties']
    return pens

def getAvgNumPlays():
    count = 0
    plays = 0
    #Opens file containing file paths from game_data
    with open('files.txt') as f:
        #Read every file path
        for line in f:
            #Truncates empty character at end of line
            line = line[:27]

            #Gets file data
            data = openFileJson(line)

            count = count + 1

            # pull out the game id and game data
            for gameid,gamedata in data.items():
                if gameid != 'nextupdate':
                    # go straight for the drives
                    for driveid,drivedata in gamedata['drives'].items():
                        if driveid != 'crntdrv':
                            plays = plays + drivedata['numplays']
    
    return round(plays/count)

def getLongestFieldGoal():
    players = []
    data = openFileJson('./player_info.json')
    
    furthest = 0
    for player,playerdata in data.items():
        for yard in playerdata['FieldGoals']:
            if yard and yard >= furthest:
                furthest = yard
                tup = (playerdata['Name'],furthest)
                players.append(tup)
    players = list(filter(lambda x: x[1] == furthest, players))
    return players
    



              
#Writes player info to JSON file
#writePlayerInfo()
#writeTeamInfo()


"""
print('=================================================================')
print('1. Find the player(s) that played for the most teams.')
player_max_team,num_teams = getPlayersWithMostTeams()
for player in player_max_team:    
    print('%s played for %d teams' % (player, num_teams))
print('=================================================================') 
print()


print('=================================================================')
print('2. Find the player(s) that played for the most teams in a year.')
players = getPlayersWithMostTeamsInSingleYear()
for player in players:
    print('%s played for %d teams in %s' % (player[0], player[1], player[2]))
print('=================================================================')
print() 


print('=================================================================')
print('3. Find the player(s) that had the most yards rushed for a loss.')
players = getPlayerMostNegativeRush()
for player in players:
    print('%s had a rush of  %d yards' % (player[0], player[1]))
print('=================================================================') 
print()

print('=================================================================')
print('4. Find the player(s) that had the most rushes for a loss.')
players = getPlayerMostNegativeRushes()
for player in players:
    print('%s has rushed for negative yards %d times' % (player[0], player[1]))
print('=================================================================') 
print()


print('=================================================================')
print('5. Find the player(s) that had the most rushes for a loss.')
players = getPlayerMostNegativePasses()
for player in players:
    print('%s has passed for negative yards %d times' % (player[0], player[1]))
print('=================================================================') 
print()

print('=================================================================')
print('6. Find the team with the most penalties.')
teams = getTeamMostPenalties()
for team in teams:
    print('%s has a total of %d penalties' % (team[0], team[1]))
print('=================================================================') 
print()

print('=================================================================')
print('7. Find the team with the most yards in penalties.')
teams = getTeamMostPenaltyYards()
for team in teams:
    print('%s has a total of %d penalty yards' % (team[0], team[1]))
print('=================================================================') 
print()


print('=================================================================')
print('8. Find the correlation between most penalized teams and games won / lost.')
teams = getTeamMostPenalties()
for team in teams:
    ratio = getWinLossRatio(team[0])
    print('%s has the most penalties(%d) and a win/loss ratio of %f' % (team[0], team[1], ratio))
teams = getHighestWinLossRatio()
for team in teams:
    pens = getPenalties(team[0])
    print('%s has the best win/loss ratio(%f) and %d penalties' % (team[0], team[1], pens))
print('=================================================================') 
print()

print('=================================================================')
print('9. Average number of plays in a game.')
avg = getAvgNumPlays()
print('On average, there are %d plays in a game' % (avg))
print('=================================================================') 
print()

print('=================================================================')
print('10. Longest field goal.')
players = getLongestFieldGoal()
for player in players:
    print('%s kicked a field goal for %d yards' % (player[0],player[1]))
print('=================================================================') 
print()
"""
