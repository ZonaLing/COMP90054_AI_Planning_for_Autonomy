import copy, math

class Minimax:
    def __init__(self, id):
        self.id = id

    def evaluate(self, state, depth):
        oppo_id = 1 if self.id == 0 else 0
        state.ExecuteEndOfRound() # end the round

        scores = {}
        grid_tile_counts = {0: 0, 1: 0} # tile count on the grid for each agent

        for id in [self.id, oppo_id]:
            agent = state.agents[id]
            bonus = agent.EndOfGameScore()
            scores[id] = agent.score

            # calculate the number of tiles on the grid after scoring 
            for i in range(len(agent.grid_state)):
                for j in range(len(agent.grid_state[0])):
                    if agent.grid_state[i][j] == 1:
                        grid_tile_counts[id] += 1

        # get the largest count among my agent and the opponent 
        max_tile_count = max(grid_tile_counts.values())

        # how many tiles my agent got on the grid compared to the opponent
        rate = grid_tile_counts[self.id] / max_tile_count if max_tile_count != 0 else 1
        # how many tiles the opponent got on the grid compared to my agent
        oppo_rate = grid_tile_counts[oppo_id] / max_tile_count if max_tile_count != 0 else 1
        
        return scores[self.id]*rate - scores[oppo_id]*oppo_rate
    
    def DoAction(self, state, action, game_rule):
        state = game_rule.generateSuccessor(state, action, self.id)  
        game_rule.current_game_state = state
        return state

    def minimax(self, state, depth : int, maximizingPlayer : bool, game_rule, alpha, beta):
        if depth == 0 or not state.TilesRemaining():
            reward = self.evaluate(state, depth)
            return reward, None

        # sort actions before expanding
        actions = self.sort_actions(game_rule.getLegalActions(state, self.id))
        
        if maximizingPlayer:
            value = float('-inf')  
        
            for action in actions:
                next_state = copy.deepcopy(state)
                next_state = self.DoAction(next_state, action, game_rule)
                tmp = self.minimax(next_state, depth-1, False, game_rule, alpha, beta)[0]

                if tmp > value:
                    value = tmp
                    # the current best move, note that it's invalid in the root
                    best_action = action

                alpha = max(alpha, value)             
                if beta <= alpha:
                    break

        else:
            value = float('inf')
            
            for action in actions:
                next_state = copy.deepcopy(state)
                next_state = self.DoAction(next_state, action, game_rule)
                tmp = self.minimax(next_state, depth-1, True, game_rule, alpha, beta)[0]

                if tmp < value:
                    value = tmp
                    best_action = action
                
                beta = min(beta, value)
                if beta <= alpha:
                    break

        return value, best_action

    def sort_actions(self, available_actions):
        # get rid of ENDROUND actions
        available_actions = [a for a in available_actions if a[0] != 'E']
        
        # sort the actions by number of tiles added on the floor descending 
        # and number of tiles added to the pattern line ascendingly
        sorted_actions = sorted(available_actions, key= lambda x: (x[2].num_to_floor_line, -x[2].num_to_pattern_line))
        
        num_actions = len(sorted_actions)
        # reduce the number of actions by a factor of a if there are too many actions to explore
        if num_actions > 27: 
            a = 3
        else:
            a = 2
        sorted_actions = sorted_actions[0: math.ceil(num_actions / a)]
        return sorted_actions