from core.game_logic import get_valid_moves, apply_move
from ai.base_search import build_path
from ai.heuristic_apps import get_state_value
import random

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

def stochastic_hill_climbing(initial_state, goal_state, log_func):
    current_state = initial_state
    current_value = get_state_value(current_state, goal_state) 
    current_node = {
        'state': current_state,
        'parent_node': None,
        'action': None,
        'value': current_value
    }
    step = 1
    while True:
        log_func(f"Step {step}: Current State Value = {current_value}\nState: {current_state}")
        step += 1
        if current_state == goal_state:
            log_func("=> SUCCESS: Goal state reached!")
            return build_path(current_node)
        valid_moves = get_valid_moves(current_state)
        better_neighbors = []
        for move in valid_moves:
            next_state = apply_move(current_state, move)
            next_value = get_state_value(next_state, goal_state) 
            log_func(f"  Checking Neighbor: Value = {next_value} | Move: {move}")
            if next_value > current_value:
                better_neighbors.append({
                    'state': next_state,
                    'action': move,
                    'value': next_value
                })
        if not better_neighbors:
            log_func(f"\n=> STOPPED: Stuck at Local Maximum (Value={current_value}). No better neighbors.")
            if current_state == goal_state:
                return build_path(current_node)
            return None
        chosen_neighbor = random.choice(better_neighbors)
        current_state = chosen_neighbor['state']
        current_value = chosen_neighbor['value']
        current_node = {
            'state': current_state,
            'parent_node': current_node,
            'action': chosen_neighbor['action'],
            'value': current_value
        }
        log_func(f"  -> Randomly picked candidate! Value = {current_value} | Move: {chosen_neighbor['action']}\n" + "-"*30)

def random_restart_hill_climbing(initial_state, goal_state, log_func):
    MAX_RESTART = 20
    for i in range(1, MAX_RESTART + 1):
        log_func(f"\n[RESTART LƯỢT {i}]: Khởi động lại nhánh leo đồi mới từ Start...")
        current_state = initial_state
        current_value = get_state_value(current_state, goal_state)
        current_node = {
            'state': current_state,
            'parent_node': None,
            'action': None,
            'value': current_value
        }  
        step = 1
        stuck_this_turn = False
        while True:
            log_func(f" Lượt {i} | Bước {step}: Value = {current_value} | State: {current_state}")
            step += 1
            if current_state == goal_state:
                log_func(f"\n=> SUCCESS: Goal reached at restart turn {i}!")
                return build_path(current_node)
            valid_moves = get_valid_moves(current_state)
            better_neighbors = []
            for move in valid_moves:
                next_state = apply_move(current_state, move)
                next_value = get_state_value(next_state, goal_state)
                if next_value > current_value:
                    better_neighbors.append({
                        'state': next_state,
                        'action': move,
                        'value': next_value
                    })
            if not better_neighbors:
                log_func(f" -> Lượt {i} bị kẹt cực đại cục bộ tại Value = {current_value}!")
                stuck_this_turn = True
                break
            chosen_neighbor = random.choice(better_neighbors)
            current_state = chosen_neighbor['state']
            current_value = chosen_neighbor['value']
            current_node = {
                'state': current_state,
                'parent_node': current_node,
                'action': chosen_neighbor['action'],
                'value': current_value
            }
        if stuck_this_turn:
            continue
    log_func(f"\n=> FAILED: Spent all {MAX_RESTART} restarts but could not find the Goal.")
    return None

def local_beam_search(initial_state, goal_state, log_func):
    k = 3 
    log_func(f"Initializing Local Beam Search with Beam Width k = {k}...")
    current_state_set = []
    start_node = {'state': initial_state, 'parent_node': None, 'action': None}
    current_state_set.append(start_node)
    valid_start_moves = get_valid_moves(initial_state)
    random.shuffle(valid_start_moves)
    for move in valid_start_moves[:k-1]:
        random_state = apply_move(initial_state, move)
        current_state_set.append({
            'state': random_state,
            'parent_node': start_node,
            'action': move
        })
    step = 1
    max_iterations = 200  
    while step <= max_iterations:
        log_func(f"\n[BEAM STEP {step}]: Processing chùm gồm {len(current_state_set)} nodes...")
        for node in current_state_set:
            val = get_state_value(node['state'], goal_state)
            log_func(f"  - Active State: {node['state']} | Value = {val}")
        neighbor_states = []
        for current_node in current_state_set:
            current_state = current_node['state']
            valid_moves = get_valid_moves(current_state)
            for move in valid_moves:
                next_state = apply_move(current_state, move)
                child_node = {
                    'state': next_state,
                    'parent_node': current_node,
                    'action': move,
                    'value': get_state_value(next_state, goal_state)
                }
                neighbor_states.append(child_node)     
        log_func(f" -> Total generated neighbors in pool: {len(neighbor_states)} nodes.")
        for neighbor in neighbor_states:
            if neighbor['state'] == goal_state:
                log_func(f"\n=> SUCCESS: Goal reached at Beam Step {step}!")
                return build_path(neighbor)
        if not neighbor_states:
            log_func("\n=> FAILED: Neighbor pool is completely empty.")
            return None
        neighbor_states.sort(key=lambda node: node['value'], reverse=True)
        best_old_value = max(n.get('value', get_state_value(n['state'], goal_state)) for n in current_state_set)
        if neighbor_states[0]['value'] <= best_old_value:
            log_func(f"\n=> STOPPED: Local maximum pool reached. Best value stagnated at {neighbor_states[0]['value']}.")
            return None
        current_state_set = neighbor_states[:k]
        step += 1  
    log_func(f"\n=> FAILED: Reached maximum iteration limit ({max_iterations}) without finding Goal.")
    return None
