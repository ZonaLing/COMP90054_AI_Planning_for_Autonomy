import random
from Azul.azul_model import AzulGameRule as GameRule
from copy import deepcopy
from agents.t_007.MCTS import MCTSNode

NUM_PLAYERS = 2

class myAgent():
    def __init__(self, _id):
        self.id = _id # Agent needs to remember its own id.
        self.game_rule = GameRule(NUM_PLAYERS) # Agent stores an instance of GameRule, from which to obtain functions.
    
    # Select the actions that lead to maximum points for each round
    # MCTS stage 1: select
    def SelectAction(self,actions,rootstate):
        root = MCTSNode(self.id, state=rootstate, game_rule=self.game_rule)
        selected_action = root.best_action(simulations = 300)
             
        return selected_action
    