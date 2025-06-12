import Azul.azul_utils as utils
from copy import deepcopy
import math
from collections import defaultdict
import numpy as np
from Azul.azul_model import AzulGameRule as GameRule

NUM_PLAYERS = 2

# Goal: Maximize the points in each round, and try to get more bonus points at the end
class MCTSNode(object):
    # objects initialisation
    def __init__(self, id, state, game_rule, parent = None, action = None):
        self.id = id
        self.state = state
        self.game_rule = game_rule
        self.parent = parent
        self.action = action
        self.children = []
        self._visit_times = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._untried_actions = self.untried_actions()

    def untried_actions(self):
        untried_actions = self.GetActions(self.state, self.id)
        return untried_actions
    
    # get the sorted actions to prevent over exploring
    def GetActions(self, state, id):
        actions = self.game_rule.getLegalActions(state, id)
        return self.sort_actions(actions)
    
    # carry out a given action on this state and return True if goal is reached received.
    def DoAction(self, state, action):
        state = self.game_rule.generateSuccessor(state, action, self.id)
        self.game_rule.current_state = state
        
        return state
    
    # compute the scores of list of actions from a state
    # compute the gap between wins and loses
    def q(self):
        wins = self._results[1]
        loses = self._results[-1]
        return wins - loses
    
    # compute the number of times each node has been visited
    def n(self):
        return self._visit_times
    
    # add more weights to actions of completing rows
    def Prioritize_Row_Action(self, actions, rootstate):
        agent_state = rootstate.agents[self.id]
        score = 0
        
        if actions[0] == utils.Action.TAKE_FROM_CENTRE or actions[0] == utils.Action.TAKE_FROM_FACTORY :
            tg = actions[2]
            grid_row = tg.pattern_line_dest
            
            
            tiles_to_fill_row = sum(agent_state.grid_state[grid_row][col] == 1 for col in range(agent_state.GRID_SIZE))

            if tiles_to_fill_row == agent_state.GRID_SIZE - 1:
                score += 3
            
            elif tiles_to_fill_row == agent_state.GRID_SIZE - 2:
                score += 1

        return score
    
    # add more weights to actions of completing columns
    def Prioritize_Col_Action(self, actions, rootstate):
        agent_state = rootstate.agents[self.id]
        score = 0
        
        if actions[0] == utils.Action.TAKE_FROM_CENTRE or actions[0] == utils.Action.TAKE_FROM_FACTORY :
            tg = actions[2]
            grid_col = int(agent_state.grid_scheme[tg.pattern_line_dest][tg.tile_type])
            
            
            tiles_to_fill_column = sum(agent_state.grid_state[row][grid_col] == 1 for row in range(agent_state.GRID_SIZE))

            if tiles_to_fill_column == agent_state.GRID_SIZE - 1:
                score += 3
            
            elif tiles_to_fill_column == agent_state.GRID_SIZE - 2:
                score += 1

        return score
    
    # add more weights to actions of completing sets
    def Prioritize_Set_Action(self, actions, rootstate):
        agent_state = rootstate.agents[self.id]
        score = 0
        
        if actions[0] == utils.Action.TAKE_FROM_CENTRE or actions[0] == utils.Action.TAKE_FROM_FACTORY :
            tg = actions[2]
            tile_type = tg.tile_type
            
            
            tiles_to_fill_set = sum(agent_state.grid_state[row][col] == 1 and agent_state.grid_scheme[row][col] == tile_type
                                    for row in range(agent_state.GRID_SIZE)
                                    for col in range(agent_state.GRID_SIZE))

            if tiles_to_fill_set == agent_state.GRID_SIZE - 1:
                score += 3
            
            elif tiles_to_fill_set == agent_state.GRID_SIZE - 2:
                score += 1

        return score
    
    # make sure that the agent can get at least one point in each round in one game
    def GetOnePoint(self, actions, rootstate):
        agent_state = rootstate.agents[self.id]
        score = 0

        if actions[0] == utils.Action.TAKE_FROM_CENTRE or actions[0] == utils.Action.TAKE_FROM_FACTORY :
            tg = actions[2]

            line = 0

            if tg.num_to_pattern_line > 0:
                line = tg.pattern_line_dest
            else:
                line = -1

            if line >= 0 and (agent_state.lines_number[line] + tg.num_to_pattern_line) == line + 1:
                score += 2

            if tg.num_to_floor_line == 0:
                score += 1

        return score
    
    # MCTS stage 2: expand
    def expand(self):
        self._untried_actions = self.sort_actions(self._untried_actions)
        action = self._untried_actions.pop(0)
        
        next_state = deepcopy(self.state)
        next_state = self.DoAction(next_state, action)
        child_node = MCTSNode(self.id, next_state, self.game_rule, parent=self, action = action)
        self.children.append(child_node)
        return child_node        
    
    # check if the node is the terminal node
    def is_terminal(self):
        return not self.state.TilesRemaining()
    
    # MCTS stage 3: simulate
    def simulate(self):
        current_simulation_state = deepcopy(self.state)

        while current_simulation_state.TilesRemaining():
            # legal_action = sorted(self.GetActions(current_simulation_state, self.id), key = lambda action: (action[2].num_to_floor_line, -action[2].num_to_pattern_line))
            legal_action = self.GetActions(current_simulation_state, self.id)
            if not legal_action:
                break
            action = self.rollout_policy(legal_action)
            current_simulation_state = self.DoAction(current_simulation_state, action)
            
        
        # calculate the score at the end of each round for comparison
        current_simulation_state.ExecuteEndOfRound()
        agent_score = self.state.agents[self.id].EndOfGameScore()
        
        if self.id == 0:
            competitor_id = 1
        else:
            competitor_id = 0
        
        competitor_score = current_simulation_state.agents[competitor_id].EndOfGameScore()
        
        return agent_score-competitor_score
    
    # MCTS stage 4: backpropagate
    def backpropagate(self, outcome):
        self._visit_times += 1

        self._results[outcome] += 1
        
        if self.parent:
            self.parent.backpropagate(outcome)
    
    # select the best child node that returns the best score with calculating UCT function
    def best_child(self, cparam = 0.1):
        uct = [(child.q()/ child.n()) + cparam * np.sqrt((2 * np.log(self.n())/child.n())) 
                for child in self.children]

        best_child = self.children[np.argmax(uct)]

        return best_child
    
    # define rollout policy to select a best action
    def rollout_policy(self, legal_action):
        
        best_action = max(legal_action, key = lambda action: (
                        self.GetOnePoint(action, self.state),
                        -action[2].num_to_floor_line))
        
        return best_action
    
    def tree_policy(self):
        current_node = self
        while not current_node.is_terminal():

            if not current_node.fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()

        return current_node

    def best_action(self, simulations):
        
        for _ in range(0, simulations):
            v = self.tree_policy()
            reward = v.simulate()
            v.backpropagate(reward)
        
        best_child_node = self.best_child(cparam=0.)
        
        return best_child_node.action
        
    def fully_expanded(self):
        return len(self._untried_actions) == 0
    
    # prioritise actions to be made: sorting
    def sort_actions(self, available_actions):
        # exclude special ENDROUND actions for available actions
        available_actions = [a for a in available_actions if a[0] != 'E']

        # penalise the actions to floor line and reward for actions that fulfills the pattern line
        sorted_actions = sorted(available_actions, 
                                key= lambda x: (
                                    # sort actions based on scores
                                    # choose the action that can get scores
                                    -self.GetOnePoint(x, self.state),
                                    # if GetOne Point actions score the same, choose the actions that tend to complete columns first
                                    -self.Prioritize_Col_Action(x, self.state),
                                    # if still the same score of col actions, choose the better complete row action
                                    -self.Prioritize_Row_Action(x, self.state),
                                    # if still the same score of row actions, choose the  better complete set action
                                    -self.Prioritize_Set_Action(x, self.state),
                                    x[2].num_to_floor_line))
        num_actions = len(sorted_actions)
        sorted_actions = sorted_actions[0: math.ceil(num_actions / 10)]
        return sorted_actions
    
class myAgent():
    def __init__(self, _id):
        self.id = _id # Agent needs to remember its own id.
        self.game_rule = GameRule(NUM_PLAYERS) # Agent stores an instance of GameRule, from which to obtain functions.
    
    # Select the actions that lead to maximum points for each round and the final game
    # MCTS stage 1: select
    def SelectAction(self,actions,rootstate):
        root = MCTSNode(self.id, state=rootstate, game_rule=self.game_rule)
        selected_action = root.best_action(simulations = 300)
        return selected_action