import json
import psycopg2
from collections import defaultdict
import csv

from player import Player

# 1 = white win, -1 = black win, 0 = draw, neglect = 100
result_to_record = {
    "win":1,
    "checkmated":-1,
    "agreed":0,
    "repetition":0,
    "timeout":-1,
    "resigned":-1,
    "stalemate":0,
    "lose":-1,
    "insufficient":0,
    "50move":0,
    "abandoned":100,
    "kingofthehill":-1,
    "threecheck":-1,
    "timevsinsufficient":0,
    "bughousepartnerlose":-1
}

class Analysis:
    def __init__(self,player):
        self.player = player
        self.record = None
        self.white_record = [0,0,0]
        self.white_win_rate = 0
        self.black_record = [0,0,0]
        self.black_win_rate = 0
        self.fetched = False
        self.white_opening_counter = defaultdict(int)
        self.black_opening_counter = defaultdict(int)
        
        reader = csv.reader(open("ECO.csv"))
        self.ECO = {}
        for line in reader:
            self.ECO[line[0]] = line[1]
        
    def calculate(self,conn = None):
        username = self.player.username
        if not self.fetched:
            # fetch the data
            stmt = "SELECT * FROM public.\"game\" WHERE player_id_white = \'{0}\' OR player_id_black = \'{0}\'".format(username)
            if conn is None:
                with open('config.json') as f:
                    config = json.load(f)

                host,user,dbname,password,sslmode = config['host'],config['user'],config['dbname'],config['password'],config['sslmode']
                conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
                conn = psycopg2.connect(conn_string)
                
            cursor = conn.cursor()
            cursor.execute(stmt)
            
            self.record = cursor.fetchall()
            
            conn.close()
        
        if len(self.record) == 0:
            print("No data found. Please load the data first.")
            return 0
        
        for relation in self.record:
            result = result_to_record[relation[3]]
            if result == 100:
                continue
            if relation[0] == username:
                if result == 1:
                    self.white_record[0] += 1
                elif result == 0:
                    self.white_record[1] += 1
                else:
                    self.white_record[2] += 1
                    
                self.white_opening_counter[relation[2]] += 1
            else:
                if result == -1:
                    self.black_record[0] += 1
                elif result == 0:
                    self.black_record[1] += 1
                else:
                    self.black_record[2] += 1
                self.black_opening_counter[relation[2]] += 1
        self.white_win_rate = [item/sum(self.white_record) for item in self.white_record]
        self.black_win_rate = [item / sum(self.black_record) for item in self.black_record]
        self.fetched = True
        return 1
        
    def show(self,conn=None):
        if not self.fetched:
            succeed = self.calculate(conn=conn)
            if not succeed:
                return
        
        print("|-------------------------------------------------------------------|")
        print("|                           ANALYSIS                                |")
        print("|-------------------------------------------------------------------|")
        print("Username:",self.player.username)
        print("Played as White: Win/Lose/Draw =", self.white_record[0],"/",self.white_record[2],"/",self.white_record[1])
        print("White win rate:",round(self.white_win_rate[0]*100,1),'%/',round(self.white_win_rate[2]*100,1),'%/',round(self.white_win_rate[1],1),'%')
        print("Played as Black: Win/Lose/Draw =", self.black_record[0],"/",self.black_record[2],"/",self.black_record[1])
        print("Black win rate:",round(self.black_win_rate[0]*100,1),'%/',round(self.black_win_rate[2]*100,1),'%/',round(self.black_win_rate[1]*100,1),'%')
        
        favorite_as_white = max(self.white_opening_counter,key=self.white_opening_counter.get)
        favorite_as_black = max(self.black_opening_counter,key=self.black_opening_counter.get)
        print("Favorite opening as White:",favorite_as_white,self.ECO[favorite_as_white])
        print("Favorite opening as Black:",favorite_as_black,self.ECO[favorite_as_black])
        
        return
        
    def openingAnalysis(self,eco):
        # do opening analysis
        white = [0,0,0]
        black = [0,0,0]
        for relation in self.record:
            if relation[2] != eco:
                continue
            
            result = result_to_record[relation[3]]
            
            if result == 100:
                continue
            
            if relation[0] == self.player.username:
                if result == 1:
                    white[0] += 1
                elif result == 0:
                    white[1] += 1
                else:
                    white[2] += 1
            else:
                if result == -1:
                    black[0] += 1
                elif result == 0:
                    black[1] += 1
                else:
                    black[2] += 1
        
        
        print("|-------------------------------------------------------------------|")
        print("|                       OPENING ANALYSIS                            |")
        print("|-------------------------------------------------------------------|")          
        print("Username:",self.player.username)
        print("Played ",eco,self.ECO[eco],sum(white)+sum(black),"times")
        print("{0} times as White, {1} times as Black".format(sum(white),sum(black)))
        if sum(white) > 0:
            print("Win {:.2f}%, Lose {:.2f}%, Draw {:.2f}% as White".format(white[0]/sum(white)*100,white[2]/sum(white)*100,white[1]/sum(white)*100))
        else:
            print("The user has never played this opening as White.")
            
        if sum(black) > 0:
            print("Win {:.2f}%, Lose {:.2f}%, Draw {:.2f}% as Black".format(black[0]/sum(black)*100,black[2]/sum(black)*100,black[1]/sum(black)*100))
        else:
            print("The user has never played this opening as Black.")

        return
        
class coAnalysis:
    def __init__(self,an1,an2):
        self.an1 = an1
        self.name1 = an1.player.username
    
        self.an2 = an2
        self.name2 = an2.player.username
    
    def show(self):
        white = [0,0,0]
        black = [0,0,0]
        
        for relation in self.an1.record:
            if (relation[0] == self.name1 and relation[1] == self.name2) or (relation[1] == self.name1 and relation[0] == self.name2):
                result = result_to_record[relation[3]]
                
                if relation[0] == self.name1:
                    if result == 1:
                        white[0] += 1
                    elif result == 0:
                        white[1] += 1
                    else:
                        white[2] += 1
                else:
                    if result == -1:
                        black[0] += 1
                    elif result == 0:
                        black[1] += 1
                    else:
                        black[2] += 1
            else:
                continue
        
        print("|-------------------------------------------------------------------|")
        print("|                         CROSS   ANALYSIS                          |")
        print("|-------------------------------------------------------------------|")
        print(self.name1,"versus",self.name2)
        print("They played each other",sum(white)+sum(black),"times")
        print(self.name1,"as White piece for",sum(white),"times")
        
        if sum(white) > 0:
            winrate_w = [item*100/sum(white) for item in white]
        else:
            winrate_w = None
        if sum(black) > 0:
            winrate_b = [item*100/sum(black) for item in black]
        else:
            winrate_b = None
        
        if winrate_w is not None:
            print(self.name1,"wins {:.2f}%, lose {:.2f}%,draw {:.2f}% as White against".format(*winrate_w),self.name2)
        else:
            print(self.name1,"had never played as White against",self.name2)
            
        if winrate_b is not None:
            print(self.name1,"wins {:.2f}%, lose {:.2f}%,draw {:.2f}% as Black against".format(*winrate_b),self.name2)
        else:
            print(self.name1,"had never played as Black against",self.name2)
        
        return
        
            
            