import time, random
from Azul.azul_model import AzulGameRule as GameRule
from copy import deepcopy
from collections import deque

# THINKTIME   = 0.9
NUM_PLAYERS = 2


# FUNCTIONS ----------------------------------------------------------------------------------------------------------#


# Defines this agent.
class myAgent():
    def __init__(self, _id):
        self.id = _id # Agent needs to remember its own id.
        self.game_rule = GameRule(NUM_PLAYERS) # Agent stores an instance of GameRule, from which to obtain functions.
        self.counter = 0

    # simply select the action that adds the most tiles in a pattern line
    def SelectAction(self, actions, rootstate):
        self.counter += 1

        most_to_line = -1 # number of tiles that can be added in a pattern line
        least_to_floor = 0  # number of tiles that are put in the floor line
        best_action = None
        best_full_rate = 0

        for action, fid, tgrab in actions:
            # the first action in a round, initialise it to be the best one
            if most_to_line == -1: 
                best_action = (action, fid, tgrab)
                most_to_line = tgrab.num_to_pattern_line
                least_to_floor = tgrab.num_to_floor_line
                current_full = rootstate.agents[self.id].lines_number[tgrab.pattern_line_dest]
                best_full_rate = (tgrab.num_to_pattern_line + current_full) / (tgrab.pattern_line_dest + 1) if tgrab.num_to_pattern_line > 0 else 0
                full_rate = 0 # can be deleted later
                continue
            
            # add tiles to pattern line, no tiles floor line
            if tgrab.num_to_floor_line == 0:
                current_full = rootstate.agents[self.id].lines_number[tgrab.pattern_line_dest] 
                full_rate = (tgrab.num_to_pattern_line + current_full) / (tgrab.pattern_line_dest + 1) 
                if full_rate > best_full_rate:
                    best_action = (action, fid, tgrab)
                    most_to_line = tgrab.num_to_pattern_line
                    least_to_floor = tgrab.num_to_floor_line
                    best_full_rate = full_rate

            # add tiles to pattern line and floor line
            elif tgrab.num_to_pattern_line > 0:
                # less or equivalent tiles to floor line but more tiles pattern line
                if tgrab.num_to_floor_line <= least_to_floor and tgrab.num_to_pattern_line > most_to_line:
                    current_full = rootstate.agents[self.id].lines_number[tgrab.pattern_line_dest] 
                    full_rate = (tgrab.num_to_pattern_line + current_full) / (tgrab.pattern_line_dest + 1)

                    best_action = (action, fid, tgrab)
                    most_to_line = tgrab.num_to_pattern_line
                    least_to_floor = tgrab.num_to_floor_line
                    best_full_rate = full_rate

            # no tiles to pattern line, only add tiles to floor line
            else:
                if tgrab.num_to_floor_line < least_to_floor:
                    best_action = (action, fid, tgrab)
                    most_to_line = 0
                    least_to_floor = tgrab.num_to_floor_line
                    best_full_rate = 0
                    full_rate = 0 # can be deleted later

            # print(action, tgrab.num_to_pattern_line, tgrab.pattern_line_dest, tgrab.num_to_floor_line, rootstate.agents[self.id].lines_number, full_rate)
            # print('best                    ', most_to_line, '-', least_to_floor, rootstate.agents[self.id].lines_number, best_full_rate)
            # print()
        return best_action
    
# END FILE -----------------------------------------------------------------------------------------------------------#
# python general_game_runner.py -g Azul -p -a agents.t_007.myTeam,agents.t_007.myTeam
# git tag -f 1403798
# git push origin -f 1403798

# basic vs myTeam
# 29 62
# 49 55
# 16 35
# 55 56
# 23 43
# 30 29
# 47 55
# 52 51
# 33 28
# 46 45
# 46 23