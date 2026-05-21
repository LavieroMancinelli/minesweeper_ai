from env import Env

def index_in_bounds(i, j, env):
    return i >= 0 and i < env.rows and j >= 0 and j < env.cols

def constraint_step(env):
    # reveal all cells adjacent to each cell with adj_count 0
    for i in range(env.rows):
        for j in range(env.cols):
            if env.adj_counts[i,j] == 0 and env.revealed[i,j] == True: # reveal all adjacent cells b/c guaranteed safe
                if index_in_bounds(i-1,j-1,env) and not env.revealed[i-1,j-1]:
                    env.take_action(i-1,j-1,"reveal")
                    return
                elif index_in_bounds(i-1,j,env) and not env.revealed[i-1,j]:
                    env.take_action(i-1,j,"reveal")
                    return
                elif index_in_bounds(i-1,j+1,env) and not env.revealed[i-1,j+1]:
                    env.take_action(i-1,j+1,"reveal")
                    return
                elif index_in_bounds(i,j-1,env) and not env.revealed[i,j-1]:
                    env.take_action(i,j-1,"reveal")
                    return
                elif index_in_bounds(i,j,env) and not env.revealed[i,j]:
                    env.take_action(i,j,"reveal")
                    return
                elif index_in_bounds(i,j+1,env) and not env.revealed[i,j+1]:
                    env.take_action(i,j+1,"reveal")
                    return
                elif index_in_bounds(i+1,j-1,env) and not env.revealed[i+1,j-1]:
                    env.take_action(i+1,j-1,"reveal")
                    return
                elif index_in_bounds(i+1,j,env) and not env.revealed[i+1,j]:
                    env.take_action(i+1,j,"reveal")
                    return
                elif index_in_bounds(i+1,j+1,env) and not env.revealed[i+1,j+1]:
                    env.take_action(i+1,j+1,"reveal")
                    return