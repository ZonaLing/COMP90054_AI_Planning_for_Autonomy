import random
from Azul.azul_model import AzulGameRule as GameRule
from copy import deepcopy
import Azul.azul_utils as utils

NUM_PLAYERS = 2

class myAgent():
    def __init__(self, _id):
        self.id = _id # Agent needs to remember its own id.
        self.game_rule = GameRule(NUM_PLAYERS) # Agent stores an instance of GameRule, from which to obtain functions.
        self.is_first_round = True
    
    # Designing heuristic function
    # Score calculation for selecting actions
    def azulheuristic(self, state):
        agent_state = state.agents[self.id]

        score = 0
        increase_points = 0
        decrease_points = 0
        floor_tile_weight = 2
        bonus_points = 0

        # Calculating bonus for adjacent tiles
        for row in range(agent_state.GRID_SIZE):
            for column in range(agent_state.GRID_SIZE):
                if agent_state.grid_state[row][column] == 1:
                    LeftRight_adj = sum(agent_state.grid_state[row, max(0, column-1):min(agent_state.GRID_SIZE, column+2)])
                    UpDown_adj = sum(agent_state.grid_state[max(0, row-1):min(agent_state.GRID_SIZE, row+2), column])
                    increase_points  = increase_points + LeftRight_adj + UpDown_adj

                    if LeftRight_adj > 0 or UpDown_adj > 0:
                        increase_points = increase_points + 1

        # Calculating decreased points for tiles on the floor line
        for i in range(len(agent_state.floor)):
            if agent_state.floor[i] == 1:
                decrease_points = decrease_points + agent_state.FLOOR_SCORES[i]*floor_tile_weight

        rows_completed = agent_state.GetCompletedRows()
        columns_completed = agent_state.GetCompletedColumns()
        set_completed = agent_state.GetCompletedSets()
        bonus_points += rows_completed*(agent_state.ROW_BONUS) + columns_completed*(agent_state.COL_BONUS) + set_completed*(agent_state.SET_BONUS)

        score += increase_points - decrease_points + bonus_points
        return score
    
    # Implement the actions that adhered to the game rules
    def GetActions(self, state):
        return self.game_rule.getLegalActions(state, self.id)
    
    # Carry out a given action on this state and return True if goal is reached received.
    def DoAction(self, state, action):
        score = state.agents[self.id].score
        state = self.game_rule.generateSuccessor(state, action, self.id)
        
        goal_reached = False #TODO: Students, how should agent check whether it reached goal or not
        
        return goal_reached
    
    # Make sure that the agent can get the first point for the first action in the first round
    def GetOnePoint(self, actions, rootstate):
        agent_state = rootstate.agents[self.id]

        if actions[0] == utils.Action.TAKE_FROM_CENTRE or actions[0] == utils.Action.TAKE_FROM_FACTORY :
            grab_tile = actions[2]

            if grab_tile.num_to_pattern_line > 0:
                lineindex = grab_tile.pattern_line_dest

            if agent_state.lines_number[lineindex] == lineindex + 1:
                return True
        
        return False
    
    # Avoid actions of taking tiles and end in floor lines for the initial step of each round
    def PlaceFloorLine(self, actions, rootstate):
        if actions[0] == utils.Action.TAKE_FROM_CENTRE or actions[0] == utils.Action.TAKE_FROM_FACTORY:
            grab_tile = actions[2]

            if grab_tile.num_to_floor_line > 0:
                return True
            
        return False
    
    # Select the actions that lead to maximum points for each round and the final game
    # Greedy Best First Search
    def SelectAction(self,actions,rootstate):

        best_action = None
        max_score = 0
        first_action_first_round = True
        
        for action in actions:
            next_state = deepcopy(rootstate)
            next_state = self.game_rule.generateSuccessor(next_state, action, self.id)

            if self.PlaceFloorLine(action, rootstate):
                    continue
            
            if first_action_first_round:
                if self.GetOnePoint(action, next_state):
                    best_action = action
                    break
            
            score = self.azulheuristic(next_state)
            if score > max_score:
                max_score = score
                best_action = action

        if best_action is None:
            best_action = random.choice(actions)

        return best_action