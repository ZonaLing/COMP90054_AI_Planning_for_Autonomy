from Azul.azul_model import AzulGameRule as GameRule
from agents.t_007.minimax import Minimax

NUM_PLAYERS = 2

class myAgent():
    def __init__(self, _id):
        self.id = _id 
        self.game_rule = GameRule(NUM_PLAYERS) # Agent stores an instance of GameRule, from which to obtain functions.

    def SelectAction(self, actions, rootstate):
        depth = 3
        # create a minimax instance
        m = Minimax(self.id)
        # run minimax algorithm
        _, action = m.minimax(rootstate, depth, True, self.game_rule, float('-inf'), float('inf'))
        return action