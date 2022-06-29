import psycopg2
import json
import regex as re
import sys

from player import Player

# to accerrate
locate = re.compile(r'\[ECO \"[ABCDE][0-9][0-9]\"\]')
extract = re.compile(r'[ABCDE][0-9][0-9]')

def pack_player(player):
    str_player = "(\'{0}\',{1},{2})".format(player.username,player.status,player.followers)
    return str_player

def find_eco(pgn):
    try:
        eco_block = re.findall(locate,pgn)
        # print(eco_block)
        
        return re.findall(extract,eco_block[0])[0]
    except IndexError:
       return "A00"

def pack_game(game):
   
    
    game['eco'] = find_eco(game["pgn"])
    
    str_game = "('{0}','{1}','{2}','{3}','{4}',{5})".format(game['white']['username'],game['black']['username'],game['eco'],game['white']['result'],game['time_control'],game['end_time'])
    
    
    return str_game

def upload_game(games):
    
    # print(games)
    
    with open('config.json') as f:
        config = json.load(f)
    
    host,user,dbname,password,sslmode = config['host'],config['user'],config['dbname'],config['password'],config['sslmode']
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, sslmode)
    conn = psycopg2.connect(conn_string)
    
    # insert player first
    player_set = set()
    
    for game in games:
        player_set.add(game['white']['username'])
        player_set.add(game['black']['username'])
        
    
    inserted = []
    
    for player in player_set:
        p = Player(player,fetch=True)
        inserted.append(pack_player(p))
    
    insert_str = ",".join(inserted)
    
    stmt = "INSERT INTO public.\"player\"(username,status,followers) VALUES " + insert_str + " ON CONFLICT (username) DO \
UPDATE SET status = excluded.status,followers = excluded.followers;"
    
    cursor = conn.cursor()
    
    cursor.execute(stmt)
    
    conn.commit()
    
    # print("Execution completed.")
    
    game_inserted = []
    for game in games:
        game_inserted.append(pack_game(game))
    
    game_cmd = ','.join(game_inserted)
    game_stmt = "INSERT INTO public.\"game\"(player_id_white,player_id_black,eco,result_code,time_control,end_time) VALUES " + game_cmd + " ON CONFLICT (player_id_white,player_id_black,end_time) DO NOTHING"
    
    
    
    cursor = conn.cursor()
    cursor.execute(game_stmt)
    
    
    conn.commit()
    
    conn.close()
    
    return