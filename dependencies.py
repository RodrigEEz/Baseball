import numpy as np
import functions

class Team:
    """A Team class"""

    def __init__(self, batting_order,user='machine'):
        self.user = user
        self.batting_order = batting_order 
        self.id, self.name, self.manager, self.players, self.pitcher, self.local = self.load_team()
        self.score = 0


    def load_team(self):
        """Looks for team information in the database"""

        select = 'SELECT * FROM TEAMS WHERE ID = ?'

        if self.user != 'machine':
            input_text = 'please select the team you want to play with: '
        else:
            input_text = 'please select the team you want to play against: '

        team_values = ()

        team = input(input_text)
        team_values = functions.execute_select(select, team)[0]
        players, pitcher = self.load_players(team)    

        if self.user != 'machine':
            local = input('Wanna play as local? (Y/N): ')
        else:
            local = None

        while team_values == ():
            team = input(input_text)
            try:
                team_values = functions.execute_select(select, team)[0]
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

        return team, name, manager, players, pitcher, local


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
        
        players_values = functions.execute_select(select, team)

        if players_values == []:
            raise IndexError('Team without players')
        else:
            for player in players_values:

                #Saves the pitcher in its own object
                if player[2] == 'PITCHER':
                    player_object = Pitcher(player[0], player[1], player[2])  
                    pitcher = player_object

                    #In case the player wants to play with pitchers as batters too
                    if self.batting_order == 1:
                        players.append(player_object)    
                    else:
                        pass

                else:
                    player_object = Player(player[0], player[1], player[2])
                    players.append(player_object)
            
            return players, pitcher
    
        
    def rotate_batting_order(self, K=1):
        """When a batter hits the ball, he gets in the diamond, so the next one in the lineup comes to the bat"""
        self.players = self.players[slice(K, len(self.players))] + self.players[slice(0, K)]


    def run(self, diamond, length):
        "Runs n number of bases based on the hit"

        for i in range(length-1):
            diamond.insert(0,0)

        diamond.insert(length-1,1)

        for i in range(length):      
           last =  diamond.pop()
           if last == 1:
               self.score +=1
               print('{} scores!'.format(self.name))
        
        self.rotate_batting_order()

    def save_stats(self, kind):
        """Saves team result in database"""

        select = """
                UPDATE TEAMS
                    SET GAMES_PLAYED = GAMES_PLAYED + 1,
                        {} = {} + 1
                    WHERE ID = {}
                """.format(kind, kind, str(self.id))

        functions.insert_data(select)

        for player in self.players:
            player.save_stats(kind)

        self.pitcher.save_stats()


class Player:
    """A player class"""

    def __init__(self , id, name, position):
        self.id  = id
        self.name = name
        self.position = position
        self.player_stats, self.batter_stats = self.set_stats()


    def set_stats(self, type='player'):
        """set stats as a dictionary"""
        
        if type == 'player' and self.position == 'PITCHER':
            return None,None
        else:
            select = """SELECT
                        B.*,
                        C.*,
                        A.GAMES_PLAYED,
                        A.GAMES_WON,
                        A.GAMES_LOST
                    FROM
                        PLAYERS A
                    LEFT JOIN 
                        BATTER_STATS B
                        ON A.ID =B.PLAYER_ID
                    LEFT JOIN
                        PITCHER_STATS C
                        ON A.ID = C.PLAYER_ID
                    WHERE
                        A.ID = ?"""
            
            column_names =  """SELECT
                                NAME,
                                TABLE_NAME
                            FROM
                                (
                                SELECT *, 'PLAYER_STATS' TABLE_NAME FROM PRAGMA_TABLE_INFO('PLAYERS') WHERE NAME LIKE '%GAMES%'
                                UNION
                                SELECT *, 'BATTER_STATS' TABLE_NAME FROM PRAGMA_TABLE_INFO('BATTER_STATS')
                                UNION
                                SELECT *, 'PITCHER_STATS' TABLE_NAME FROM PRAGMA_TABLE_INFO('PITCHER_STATS')
                                )
                            ORDER BY
                                TABLE_NAME"""

            
            stats = functions.execute_select(select, self.id)[0]
            stats = ["" if stat == None else stat for stat in stats]

            # For every type of stat (general stats, batter stats and pitcher_stats), creates a dictionary with every stat of the player

            player_stats, batter_stats, pitcher_stats = 0,0,0

            stats_names = functions.execute_select(column_names)

            stats_dict = dict(zip(stats_names, stats))

            # Drops keys that aren't needed
            stats_dict = {stat_name:stat for stat_name, stat in stats_dict.items() if stat != "" if stat_name[0] != 'PLAYER_ID'}

            player_stats = {stat_name[0]:stat for stat_name, stat in stats_dict.items() if stat_name[1] == 'PLAYER_STATS'}

            batter_stats = {stat_name[0]:stat for stat_name, stat in stats_dict.items() if stat_name[1] == 'BATTER_STATS'}

            if self.position == 'PITCHER':
                pitcher_stats = {stat_name[0]:stat for stat_name, stat in stats_dict.items() if stat_name[1] == 'PITCHER_STATS'}
                return player_stats, batter_stats, pitcher_stats
            else:
                return player_stats, batter_stats    


    def normalize_stats(self, min_AB, normalization_penalty, type='player'):
        """Normalizes probabilites based on average stats"""

        stats_names = ['PA','BB','OUT','1B', '2B', '3B', 'HR']

        if type != 'player' and self.position == 'PITCHER':
            stats = self.pitcher_stats
        else:
            stats = self.batter_stats

        avg_stats = functions.read_average_stats()

        normalized_stats = dict()

        for stat in stats_names:
            stat_value = stats[stat]
            inner_term =  (min_AB - stats['PA']) * ((1/normalization_penalty)*avg_stats[stat]/avg_stats['PA'])

            if self.position == 'PITCHER':
                normalized_stat = stat_value + np.ceil(inner_term)
            else:
                normalized_stat = stat_value + np.floor(inner_term)

            normalized_stats[stat] = normalized_stat

        return normalized_stats
    

    def bat(self, pitcher):
        """Decides the outcome of a plate appereance based on batter and pitcher success rate"""

        probs = ['BB','OUT','1B', '2B', '3B', 'HR'] 

        avg_stats = functions.read_average_stats()

        # In case that Plates appereances are lower than 100, player stats are normalized to avoid small sample size overrepresentation
        if self.batter_stats['PA'] < 100:
            batter_stats = self.normalize_stats(100, 0.5, avg_stats)
        else:
            batter_stats = self.batter_stats

        if pitcher.pitcher_stats['PA'] < 100:
            pitcher_stats = pitcher.normalize_stats(100, 0.5, avg_stats)
        else:
            pitcher_stats = pitcher.pitcher_stats

        combined_probs = dict()

        # Calculates probabilities for every outcome, given the probability of occurence of every outcome for each of the opponents
        for prob in probs:
            a = batter_stats[prob]/batter_stats['PA']
            b = pitcher_stats[prob]/pitcher_stats['PA']
            c = avg_stats[prob]/avg_stats['PA']
            combined_probs[prob] = functions.calculate_moreyz(a,b,c)
            print(combined_probs)

        combined_probs_values = list(combined_probs.values())

        # Divides by three because for every plate appereance, the batter has 3 opportunities to hit against the pitcher
        combined_probs_values = [value/3 for value in combined_probs_values]

        # The remaining probability will be assigned to the strike outcome
        combined_probs_values.insert(0,1-sum(combined_probs_values))

        hit_result = np.random.choice([1,2,3,4,5,6,7], p=combined_probs_values)

        if hit_result > 3:
            result = 4
        else:
            result = hit_result

        hit_result = hit_result-3

        return result, hit_result


    def save_result(self,stats, type='batter'):
        """Saves the Plate Appereance result, for player statistics"""
        
        if type == 'pitcher':
            self.pitcher_stats['PA']+=1
            for stat in stats:
                self.pitcher_stats[stat]+=1
        else:
            self.batter_stats['PA']+=1
            for stat in stats:
                self.batter_stats[stat]+=1
    
    def save_stats(self, kind):
        """Saves stats into the database"""

        general_select = """
                        UPDATE PLAYERS
                            SET GAMES_PLAYED  = GAMES_PLAYED + 1,
                            {} = {} + 1
                        WHERE ID = {}
                        """.format(kind, kind, str(self.id))

        functions.insert_data(general_select)

        #save batter stats
        batterstats_select  = """UPDATE BATTER_STATS SET"""

        batterstats_values = []

        for key, value in self.batter_stats.items():
            batterstats_values.append(f"'{key}' = {value}")

        batterstats_select += " " + ",".join(batterstats_values)
        batterstats_select += " WHERE PLAYER_ID = {}".format(str(self.id))
        if batterstats_values != []:
            functions.insert_data(batterstats_select)


class Pitcher(Player):
    """A pitcher class"""

    def __init__(self, id, name, position):
        super().__init__(id, name, position)
        self.player_stats, self.batter_stats,self.pitcher_stats = self.set_stats('pitcher')

    def save_stats(self):
        """Save pitcher stats"""

        pitcherstats_select  = """UPDATE PITCHER_STATS SET"""

        pitcherstats_values = []

        for key, value in self.pitcher_stats.items():
            if key != 'PITCHING_DISTRIBUTION':
                pitcherstats_values.append(f"'{key}' = {value}")

        pitcherstats_select += " " + ",".join(pitcherstats_values)
        pitcherstats_select += " WHERE PLAYER_ID = {}".format(str(self.id))
        if pitcherstats_values != []:
             functions.insert_data(pitcherstats_select)


class Field:
    """A Field class"""

    def __init__(self):
        self.bases = [0,0,0,0]

    def clean_field(self):
        self.field = [0,0,0,0]
