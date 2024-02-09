import json

class Team:
    """Defines team and it's resources during game"""

    def __init__(self):
        self.selected_team  = self.select_team()
        self.score = 0
        self.batting_order = self.define_batting_order()
        self.positions = self.define_positions()

    def define_batting_order(self):
        pass

    def define_positions(self):

        positions = dict()

        for player in self.selected_team.keys():
            positions[self.selected_team[player]['position']] = self.selected_team[player]['name']

        return positions

    def select_team(self):
        team = int(input('please select the team you want to play with: '))

        with open('data.json') as json_file:
            data = json.load(json_file)

        team = data['teams'][team]

        return team
        
    def rotate_batting_order(self, K=1):
        """When a batter hits the ball, he gets in the diamond, so the next one in the lineup comes to the bat"""
        self.batting_order = self.batting_order[slice(K, len(self.batting_order))] + self.batting_order[slice(0, K)]

    def run(self, diamond, length ):

        for i in range(length-1):
            diamond.insert(0,0)

        diamond.insert(length-1,1)

        for i in range(length):      
           last =  diamond.pop()
           if last == 1:
               self.score +=1
        
        self.rotate_batting_order()


class Field:
    

    def __init__(self):
        self.pitcher = ''
        self.first_base = ''
        self.second_base = ''
        self.shortstop = ''
        self.third_base = ''
        self.catcher = ''
        self.left_yard = ''
        self.center_yard = ''
        self.right_yard = ''
        self.field = [0,0,0,0]

    def fill_positions(self, team):
        self.pitcher = team.positions['pitcher']
        self.first_base = team.positions['first_base']
        self.second_base = team.positions['second_base']
        self.short_stop = team.positions['short_stop']
        self.third_base = team.positions['third_base']
        self.catcher = team.positions['catcher']
        self.left_yard = team.positions['left_yard']
        self.center_yard = team.positions['center_yard']
        self.right_yard = team.positions['right_yard']

    def clean_field(self):
        self.field = [0,0,0,0]