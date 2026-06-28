def get_valid_moves(state):
    moves = []
    blank_index = state.index(0)
    if blank_index > 2: moves.append('Up')
    if blank_index < 6: moves.append('Down')
    if blank_index % 3 != 0: moves.append('Left')
    if (blank_index + 1) % 3 != 0: moves.append('Right')
    return moves

def apply_move(state, move_name):
    state_list = list(state)
    blank_index = state_list.index(0)
    if move_name == 'Up': new_index = blank_index - 3
    elif move_name == 'Down': new_index = blank_index + 3
    elif move_name == 'Left': new_index = blank_index - 1
    elif move_name == 'Right': new_index = blank_index + 1
    
    state_list[blank_index], state_list[new_index] = state_list[new_index], state_list[blank_index]
    return tuple(state_list)

def apply_move_ucs(state, move_name):
    state_list = list(state)
    blank_index = state_list.index(0)
    if move_name == 'Up': new_index = blank_index - 3
    elif move_name == 'Down': new_index = blank_index + 3
    elif move_name == 'Left': new_index = blank_index - 1
    elif move_name == 'Right': new_index = blank_index + 1
    
    move_cost = state_list[new_index]  
    state_list[blank_index], state_list[new_index] = state_list[new_index], state_list[blank_index]
    return tuple(state_list), move_cost