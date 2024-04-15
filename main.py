from dependencies import Team, Field
from functions import code_result, update_average_stats
import time, os

class Game:
    """Initialize game"""

    def __init__(self):
        self.bat_type = input('Do you wanna play with pitchers as batters (1) or not (2): ')
        self.team1 = Team(self.bat_type, 'user')
        self.team2 = Team(self.bat_type)
        self.inning = 1
        self.field = Field()
        
    def playball(self):
        """defines Inning and defender/batter control of the game"""

        self.print_playball()

        while self.inning <= 1 or self.team1.score == self.team2.score:
                
                if self.team1.local == 'Y':
                    # Local Team defense
                    self.bat(self.team2, self.team1, self.inning)
                    # Visitor Team defense
                    self.bat(self.team1, self.team2, self.inning)
                else:
                    # Local Team defense
                    self.bat(self.team1, self.team2, self.inning)
                    # Visitor Team defense
                    self.bat(self.team2, self.team1, self.inning)
                    
                self.inning += 1

        # Saves stats so calculations can use historical data
        self.savegame(self.team1, self.team2) if self.team1.score > self.team2.score else self.savegame(self.team2, self.team1)


    def bat(self, batter, defender, inning):
        """Defines batting sequence, considering strikes, outs and fouls"""
        strikes = 0
        outs = 0
        fouls = 0
        balls = 0
        player_outcome = 0

        time.sleep(5)

        while outs < 3:

            self.print_scoreboard(batter, defender, inning, strikes, outs, fouls, balls)

            print("{} is pitching.\n".format(defender.pitcher.name))

            time.sleep(1)

            print("{} is ready at bat.".format(batter.players[0].name))
            time.sleep(3)
            print('pitcher throws...')
            time.sleep(2)
            result, hit_result = batter.players[0].bat(defender.pitcher)

            # Strike
            if result == 1:
                print('STRIKE')
                strikes += 1
                if strikes == 3 or (strikes + fouls >= 3):
                    print('STRIKEOUT!')
                    outs += 1
                    batter.rotate_batting_order()
                    strikes, fouls, balls = 0,0,0
                    player_outcome = ['SO']
                time.sleep(3)   

            # Ball
            elif result == 2:
                print('BALL!')
                balls += 1
                if balls >= 4:
                        print('{} walks to the first base.'.format(batter.players[0].name))
                        batter.run(self.field.bases, 1)
                        strikes, fouls, balls = 0,0,0  
                        player_outcome = ['BB']
                time.sleep(3)

            # Out
            elif result == 3:
                    print('OUT!')
                    outs +=1
                    batter.rotate_batting_order()
                    strikes, fouls, balls = 0,0,0  
                    player_outcome = ['OUT']
                    time.sleep(3)

            # Hit
            elif result == 4:
                    print('HIT!')
                    batter.run(self.field.bases, hit_result)
                    strikes, fouls, balls = 0,0,0  
                    hit_result = code_result(hit_result)
                    player_outcome = ['H', hit_result]
                    time.sleep(3)

            #Saves the result of the turn to the batter and pitcher stats
            if player_outcome != 0:
                batter.players[-1].save_result(player_outcome)
                defender.pitcher.save_result(player_outcome, type='pitcher')
                player_outcome = 0
            
            os.system('cls')


    def print_playball(self):
        """Prints PLAYBALL in console"""

        os.system('cls')

        print(' _____________________________')
        print('|                             |')
        print('|        PLAY BALL!!!!!!!!    |')
        print('|_____________________________|')
        time.sleep(2)

        os.system('cls')


    def print_scoreboard(self, team1, team2, innings, strikes, outs, fouls, balls):
        """Prints scoreboard"""

        local_name, visitor_name = (team1.name.title(), team2.name.title()) if team1.local == 'Y' else (team2.name.title(), team1.name.title())
        local_points, visitor_points = (str(team1.score), str(team2.score)) if team1.local == 'Y' else (str(team2.score), str(team1.score))
        innings = str(innings)

        print(' ___________________________________________________________')
        print('|             TEAM                |   INNING   |   POINTS   |')
        print('|---------------------------------|------------|------------|')
        print('| {} |     {}|{}     |'.format(local_name.ljust(31,' '), innings.ljust(7, ' '),local_points.rjust(7, ' ')))
        print('| {} |            |{}     |'.format(visitor_name.ljust(31,' '), visitor_points.rjust(7, ' ')))
        print(' -----------------------------------------------------------')

        print(' ___________________________________________________________')
        print('|     OUTS    |    STRIKES    |     FOULS     |    BALLS    |')
        print('|-------------|---------------|---------------|-------------|')
        print('|      {}      |       {}       |       {}       |      {}      |'.format(str(outs), str(strikes), str(fouls), str(balls)))

        print('\n')

    def savegame(self, winner, loser):
        """Saves the game results in the database"""

        savegame = input('Wanna save game (Y/N)')

        if savegame == 'Y':

             winner.save_stats('GAMES_WON')
             loser.save_stats('GAMES_LOST')

             update_average_stats()
                    

play_again = True

while play_again:

    game = Game()
    game.playball()

    play_again = input("Want to play again? (Y/N): ")
    play_again = False if play_again == "N" else True