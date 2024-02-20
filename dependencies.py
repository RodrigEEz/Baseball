import sqlite3
import time

class Team:
    """A sample Team class"""

    def __init__(self):
        self.id, self.name, self.manager, self.players, self.pitcher = self.load_team()
        self.score = 0

    def load_team(self):
        """Looks for team information in the database"""

        select = 'SELECT * FROM TEAMS WHERE ID = ?'

        team_values = ()

        con = sqlite3.connect('database.sqlite')
        cur = con.cursor()
        while team_values == ():
            team = input('please select the team you want to play with: ')
            selected = cur.execute(select, team)
            try:
                team_values = selected.fetchall()[0]
                try:
                    players, pitcher = self.load_players(team)
                except IndexError:
                    print('The team does not have players assigned. Please select other team.')
                    team_values = ()
            except IndexError:
                print('Select a valid team.')
                team_values = ()

        name = team_values[1]
        manager = team_values[2]

        return team, name, manager, players, pitcher

    def load_players(self, team):
        "Looks for players information in the database"

        players = list()

        select = "\
                SELECT\
                    A.ID,\
                    A.NAME,\
                    B.POSITION_NAME,\
                    A.GAMES_PLAYED,\
                    A.GAMES_WON,\
                    A.GAMES_LOST\
                FROM\
	                PLAYERS A\
                INNER JOIN\
	                POSITIONS B\
	                ON A.POSITION_ID = B.ID\
                WHERE\
                    A.TEAM_ID = ?"
        
        con = sqlite3.connect('database.sqlite')
        cur = con.cursor()
        selected = cur.execute(select, team)
        players_values = selected.fetchall()

        if players_values == []:
            raise IndexError('Team without players')
        else:
            for player in players_values:
                if player[2] == 'PITCHER':
                    player_object = Pitcher(player[0], player[1], player[2], player[3:])  
                    pitcher = player_object
                else:
                    player_object = Player(player[0], player[1], player[2], player[3:])
                players.append(player_object)
            
            return players, pitcher
    
        
    def rotate_batting_order(self, K=1):
        """When a batter hits the ball, he gets in the diamond, so the next one in the lineup comes to the bat"""
        self.players = self.players[slice(K, len(self.players))] + self.players[slice(0, K)]

    def run(self, diamond, length ):

        for i in range(length-1):
            diamond.insert(0,0)

        diamond.insert(length-1,1)

        for i in range(length):      
           last =  diamond.pop()
           if last == 1:
               self.score +=1
        
        self.rotate_batting_order()


class Player:
    """A sample player class"""

    def __init__(self , id, name, position, stats):
        self.id  = id
        self.name = name
        self.position = position
        self.stats = self.set_stats(stats, ['games_played', 'games_won', 'games_lost'])

    def set_stats(self, stats, stats_names):
        """set stats as a dictionary"""

        stats_dict = dict()

        i = 0

        for stat in stats_names:
            stats_dict[stat] = stats[i]
            i +=1

        return stats_dict

class Pitcher(Player):
    """A class for the pitcher"""

    def __init__(self, id, name, position, stats):
        super().__init__(id, name, position, stats)
        pitching_stats = self.set_pitching_stats()

    def set_pitching_stats(self):
        """returns pitching stats"""

        stats_names = ['accuracy']

        select = 'SELECT\
                        *\
                  FROM\
                        PITCHER_STATS\
                  WHERE\
                        PLAYER_ID = ?'

        con = sqlite3.connect('database.sqlite')
        cur = con.cursor()
        selected = cur.execute(select, (str(self.id),))
        stats = selected.fetchall()[0]

        stats_dict = dict()

        stats_dict = self.set_stats(stats, stats_names)

        return stats_dict
        

class Field:
    """A sample Field class"""

    def __init__(self):
        self.bases = [0,0,0,0]

    def clean_field(self):
        self.field = [0,0,0,0]

def print_playball():
    print(' _____________________________')
    print('|                             |')
    print('|        PLAY BALL!!!!!!!!    |')
    print('|_____________________________|')
    time.sleep(2)

def print_scoreboard(local_name, visitor_name, local_points, visitor_points, innings):
    print(' ___________________________________________________________')
    print('|             TEAM                |   INNING   |   POINTS   |')
    print('|---------------------------------|------------|------------|')
    print('| {} |     {}|{}     |'.format(local_name.ljust(31,' '), innings.ljust(7, ' '),local_points.rjust(7, ' ')))
    print('| {} |            |{}     |'.format(visitor_name.ljust(31,' '), visitor_points.rjust(7, ' ')))
    print(' -----------------------------------------------------------')
    time.sleep(5)