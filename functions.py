import json    

def select_team():
    #team = input('please select the team you want to play with: ')

    with open('data.json') as json_file:
        data = json.load(json_file)

    return data

team = select_team()

team = team['teams'][0]

for i in team.keys():
    print(i['position'])