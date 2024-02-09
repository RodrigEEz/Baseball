from dependencies import Team, Field
import numpy as np

class Game:
    """Initialize game"""

    def __init__(self):
        self.team1 = Team()
        self.team2 = Team()
        self.inning = 1
        self.local = input('wanna play as local? (Y/N)')
        self.field = Field()
    
    #methods
        
    def playball(self):
        """defines Inning and defender/batter control of the game"""
        while self.inning < 9 or self.team1.score == self.team2.score:
                if self.local == 'Y':
                    self.bat(batter=self.team2, defender=self.team1)
                else:
                    self.bat(batter=self.team2, defender=self.team1)
                self.inning += 1

    def bat(self, batter, defender):
        """Defines batting sequence, considering strikes, outs and fouls"""
        strikes = 0
        outs = 0
        fouls = 0
        self.field.fill_positions(defender)

        while outs < 3:
            while strikes < 3:
                print('pitcher throws')
                print('batter bats')
                choice = np.choice([1,2,3]) #1--strike 2--foul 3--hit
                if choice == 1:
                    strikes += 1
                    if strikes == 3 or (strikes + fouls >= 3):
                        outs += 1
                        batter.rotate_batting_order()
                elif choice == 2:
                    fouls += 1
                elif choice == 3:
                        # define hit techinque (1- first base, 2- second base, 3- third base, 4- HR)
                        choice = np.choice([1,2,3,4]) # this will be changed once the hit technique is defined
                        batter.run(self.field.field, choice)
                        strikes = 0

game = Game()

game.playball()