from template import Agent
import random, time
import heapq
import math
from copy import deepcopy
from Azul.azul_model import AzulGameRule as GameRule

NUM_PLAYERS = 2
THINKTIME = 0.9
MIN_DIFF_H = 15
MIN_DIFF = 10
COL_POINTS = 7
ROW_POINTS = 2
SET_POINTS =10

class myAgent(Agent):
    def __init__(self,_id):
        super().__init__(_id)
        self.id = _id
        self.game_rule = GameRule(NUM_PLAYERS)

    def CheckGoalReached(self, state):
        # Goal reached when score greater than opponent's score 
        if self.id == 0:
            opponent_id = 1
        else:
            opponent_id = 0
        score, tiles = state.agents[self.id].ScoreRound()
        opponent_score, op_tiles= state.agents[opponent_id].ScoreRound()

        # Calculate bonus points
        r = state.agents[self.id].GetCompletedRows()
        c = state.agents[self.id].GetCompletedColumns()
        s = state.agents[self.id].GetCompletedSets()
        op_r = state.agents[opponent_id].GetCompletedRows()
        op_c = state.agents[opponent_id].GetCompletedColumns()
        op_s = state.agents[opponent_id].GetCompletedSets()

        bonus_points = r*ROW_POINTS + c*COL_POINTS + s*SET_POINTS
        op_bonus = op_r*ROW_POINTS + op_c*COL_POINTS + op_s*SET_POINTS

        if score + bonus_points > opponent_score + MIN_DIFF + op_bonus:
            return True
        else:
            return False

    def Heuristic(self, actions, state):
        if self.id == 0:
            opponent_id = 1
        else:
            opponent_id = 0
        score, t = state.agents[self.id].ScoreRound()
        opponent_score, t2 = state.agents[opponent_id].ScoreRound()

        # Calculate bonus points
        r = state.agents[self.id].GetCompletedRows()
        c = state.agents[self.id].GetCompletedColumns()
        s = state.agents[self.id].GetCompletedSets()
        op_r = state.agents[opponent_id].GetCompletedRows()
        op_c = state.agents[opponent_id].GetCompletedColumns()
        op_s = state.agents[opponent_id].GetCompletedSets()

        bonus_points = r*ROW_POINTS + c*COL_POINTS + s*SET_POINTS
        op_bonus = op_r*ROW_POINTS + op_c*COL_POINTS + op_s*SET_POINTS

        if score == 0:
            return 99
        h = 0
        h += opponent_score + op_bonus - score - bonus_points + MIN_DIFF_H
        if h < 0:
            return 0
        return h

    def GetSuccessor(self, action, state):
        return self.game_rule.generateSuccessor(state, action, self.id)
    
    def SelectAction(self, actions, game_state):
        start_time = time.time()

        priority_queue = []
        closed = []

        state = deepcopy(game_state)
        actions = self.game_rule.getLegalActions(game_state, self.id)

        root_node = (state, [])
        entry = (self.Heuristic(actions, state), root_node)
        heapq.heappush(priority_queue, entry)

        best_g = dict()

        # Priority Queue A Star Search
        while len(priority_queue) > 0 and time.time()-start_time < THINKTIME:
            queue_item = heapq.heappop(priority_queue)
            cost, node = queue_item
            state, action_list = node

            if (queue_item not in closed) or (cost < best_g[state]):
                closed.append(queue_item)
                best_g[state] = cost

                legalActions = self.game_rule.getLegalActions(state, self.id)
                if len(legalActions) > 2:
                    # Sort actions
                    legalActions = sorted(legalActions, key = lambda x:(x[2].num_to_floor_line, -x[2].num_to_pattern_line))

                # Check goal reached
                if len(action_list) > 0:
                    if self.CheckGoalReached(state):
                        if self.game_rule.validAction(action_list[0], actions):
                            return action_list[0]
                
                for a in legalActions:
                    action_list = action_list + [a]
                    nstate = deepcopy(state)
                    next_state = self.game_rule.generateSuccessor(nstate, a, self.id)  
                    heuristic_value = self.Heuristic(action_list, next_state) + random.uniform(0.0000001, 0.009)
                    # If heuristic value is less than 200 add it back into the queue
                    if heuristic_value < 200:
                        next_node = (next_state, action_list)
                        entry = (cost + heuristic_value, next_node)
                        heapq.heappush(priority_queue, entry)

        # If a star fails then sort actions and return the first move   
        legalActions = self.game_rule.getLegalActions(game_state, self.id)
        legalActions = sorted(legalActions, key = lambda x:(x[2].num_to_floor_line, -x[2].num_to_pattern_line))
        return legalActions[0]