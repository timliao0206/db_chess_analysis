from analysis import Analysis, coAnalysis
from player import Player,load_game,check_username
from game import *

# help create command line arguments
from argparse import ArgumentParser
    
def main():
    parser = ArgumentParser()

    parser.add_argument('-u','--update',dest = 'update_user',help='Update user\'s data, added into database if not exist',metavar='USERNAME')
    parser.add_argument('--num',dest='num',nargs='?',const = 3,type = int,help="the number specified for the update months. Default is 3 months.")
    parser.add_argument('-a','--analysis',dest = 'analysis',help = 'Analysis player\'s data',metavar='USERNAME')
    parser.add_argument('-c','--cross-alignment',nargs=2,dest='cross',help="Compare and analysis the game between two players",metavar=('USERNAME1','USERNSME2'))
    parser.add_argument('-o','--opening',nargs=2,dest='opening',help="show the data of given opening of a player",metavar=('OPENING_ECO','USERNAME'))


    args = parser.parse_args()
    
    analysis = None

    if args.update_user:
        # update the user using player's function
        
        name = args.update_user
        
        # check if it is valid username
        if not check_username(name):
            print("Username Invalid.Terminated.")
            
            return
            
        # update it accroding to the month specified
        
        print("Loading... This may take some time...")
        
        
        month = 3
        if args.num:
            month = args.num
        
        player = Player(name)
        
        load_game(player,month)
        
        print("Load complete!")
    if args.analysis:
        # do analysis
        
        name = args.analysis
        player = Player(name)
        
        analysis = Analysis(player)
        analysis.show()
        
    if args.cross:
        # do cross alignment
        
        an1 = Analysis(Player(args.cross[0]))
        an1.calculate()
        an2 = Analysis(Player(args.cross[1]))
        an2.calculate()
        
        cross = coAnalysis(an1,an2)
        cross.show()
        
    if args.opening:
        # opening analysis
        
        if analysis is None:
            name = args.opening[1]
            analysis = Analysis(Player(name,fetch=True))
            analysis.calculate()
        analysis.openingAnalysis(args.opening[0])

if __name__ == '__main__':
    main()