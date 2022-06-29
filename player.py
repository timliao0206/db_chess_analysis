import requests
import json
import regex as re


status_code = {"closed":0,
               "closed:fair_play_violations":1,'closed:abuse':1,
               "basic":2,
               "premium":3,
               "mod":4,
               "staff":5}

def check_username(username):
    return re.fullmatch(r"[0-9a-zA-Z]+",username)


class Player:
    def __init__(self,username,status=0,followers=0,fetch=False):
        self.username = username
        self.status = status
        self.followers = followers
        if fetch:
            self.fetch()
    
    # fetch the user data by its username    
    def fetch(self):
        r = requests.get("https://api.chess.com/pub/player/" + self.username)
        
        
        data = None
        if r.status_code == 200:
            data = json.loads(r.text)
        else:
            print("Player " + self.username + " not found or ban internet connection.")
            return
        self.status = status_code[data['status']]
        self.followers = data['followers']
        
        return
    

from game import upload_game

# load game by username. Load game played in most recent 3 month by default 
def load_game(player,time_period = 3):
    r = requests.get("https://api.chess.com/pub/player/" + player.username + "/games/archives")
    
    data = None
    if r.status_code == 200:
        data = json.loads(r.text)
    else:
        print("Player " + player.username + " not found or bad internet connection.")
        return
    
    archive = data['archives']
    
    import time
    def queryFunc(url):
        time.sleep(0.1)
        return json.loads(requests.get(url).text)
    
    array = map(queryFunc,archive[-time_period:])
    
    games = []
    for x in array:
        monthGameList = x["games"]
        games += monthGameList
    
    upload_game(games)
    # insert the games into database
        
        
        
    
    