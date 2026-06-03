from core.game_logic import get_valid_moves, apply_move
from ai.base_search import build_path
from ai.heuristic_apps import get_state_value

def simple_hill_climbing(initial_state, goal_state, log_func):
    current_state = initial_state
    current_value = get_state_value(current_state, goal_state)
    current_node = {'state': current_state, 'parent_node': None, 'action': None, 'value': current_value}
    step = 1
    while True:
        log_func(f"Step {step}: Current State Value = {current_value}\nState: {current_state}")
        step += 1
        if current_state == goal_state:
            log_func("=> SUCCESS: Goal state reached!")
            return build_path(current_node)
        valid_moves = get_valid_moves(current_state)
        better_neighbor_found = False
        for move in valid_moves:
            next_state = apply_move(current_state, move)
            next_value = get_state_value(next_state, goal_state)
            log_func(f"  Evaluating Neighbor: Value = {next_value} | Move: {move}")
            if next_value > current_value:
                current_state = next_state
                current_value = next_value
                current_node = {'state': current_state, 'parent_node': current_node, 'action': move, 'value': current_value}
                log_func(f"  -> Found better state! Moving to {current_state}\n" + "-"*30)
                better_neighbor_found = True
                break
        if not better_neighbor_found:
            log_func(f"\n=> STOPPED: Stuck at Local Maximum (Value={current_value}).")
            if current_state == goal_state: return build_path(current_node)
            return None

def steepest_ascent_hill_climbing(initial_state, goal_state, log_func):  
    current_state = initial_state
    current_value = get_state_value(current_state, goal_state)   
    current_node = {'state': current_state, 'parent_node': None, 'action': None, 'value': current_value}    
    step = 1
    while True:
        log_func(f"Step {step}: Current State Value = {current_value}\nState: {current_state}")
        step += 1       
        if current_state == goal_state:
            log_func("=> SUCCESS: Goal state reached!")
            return build_path(current_node)          
        valid_moves = get_valid_moves(current_state)   
        best_neighbor_state = None
        best_neighbor_value = current_value 
        best_move = None
        for move in valid_moves:
            next_state = apply_move(current_state, move)
            next_value = get_state_value(next_state, goal_state)   
            log_func(f"  Checking Neighbor: Value = {next_value} | Move: {move}")
            if next_value > best_neighbor_value:
                best_neighbor_value = next_value
                best_neighbor_state = next_state
                best_move = move
        if best_neighbor_state is None:
            log_func(f"\n=> STOPPED: Stuck at Local Maximum (Value={current_value}).")
            if current_state == goal_state: return build_path(current_node)
            return None
        current_state = best_neighbor_state
        current_value = best_neighbor_value
        current_node = {'state': current_state, 'parent_node': current_node, 'action': best_move, 'value': current_value}
        log_func(f"  -> Moving to BEST neighbor! Value = {current_value} | State: {current_state}\n" + "-"*30)