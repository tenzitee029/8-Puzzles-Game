from core.game_logic import get_valid_moves, apply_move, apply_move_ucs
from ai.uninformed import build_path

def heuristic_misplaced_tiles(state, goal_state):
    count = 0
    for i in range(9):
        if state[i] != 0 and state[i] != goal_state[i]:
            count += 1
    return count

def get_state_value(state, goal_state):
    misplaced = heuristic_misplaced_tiles(state, goal_state)
    return 9 - misplaced

def greedy_search(initial_state, goal_state, log_func):
    start_h = heuristic_misplaced_tiles(initial_state, goal_state)
    start_node = {'state': initial_state, 'parent_node': None, 'action': None, 'h_value': start_h}
    frontier = [start_node]
    reached_states = set()
    step = 1

    while frontier:
        current_node = frontier[0]
        for node in frontier:
            if node['h_value'] < current_node['h_value']:
                current_node = node             
        log_func(f"Bước {step}: Lấy nút tốt nhất (h(n)={current_node['h_value']})\nTrạng thái: {current_node['state']}")
        step += 1       
        current_state = current_node['state']
        if current_state == goal_state:
            return build_path(current_node)
        frontier.remove(current_node)
        reached_states.add(current_state)

        for move in get_valid_moves(current_state):
            new_state = apply_move(current_state, move)       
            in_frontier = any(node['state'] == new_state for node in frontier)

            if not in_frontier and (new_state not in reached_states):
                m_h = heuristic_misplaced_tiles(new_state, goal_state)
                child_node = {'state': new_state, 'parent_node': current_node, 'action': move, 'h_value': m_h}
                frontier.append(child_node)
    return None

def a_star_search(initial_state, goal_state, log_func):
    start_h = heuristic_misplaced_tiles(initial_state, goal_state)
    start_node = {'state': initial_state, 'parent_node': None, 'action': None, 'g_value': 0, 'f_value': start_h}
    frontier = [start_node]
    reached_g = {initial_state: 0}
    step = 1

    while frontier:
        current_node = frontier[0]
        for node in frontier:
            if node['f_value'] < current_node['f_value']:
                current_node = node
        log_func(f"Bước {step}: Lấy nút tốt nhất (f(n)={current_node['f_value']}, g(n)={current_node['g_value']})\nTrạng thái: {current_node['state']}")
        step += 1  
        current_state = current_node['state']
        if current_state == goal_state:
            return build_path(current_node)
        frontier.remove(current_node)
        for move in get_valid_moves(current_state):
            new_state, move_cost = apply_move_ucs(current_state, move)
            g_new = current_node['g_value'] + move_cost
            in_frontier_node = next((node for node in frontier if node['state'] == new_state), None)
            in_reached = new_state in reached_g and new_state not in [node['state'] for node in frontier]
            if in_reached:
                if g_new >= reached_g[new_state]: continue
                else:
                    reached_g[new_state] = g_new
                    m_h = heuristic_misplaced_tiles(new_state, goal_state)
                    child_node = {'state': new_state, 'parent_node': current_node, 'action': move, 'g_value': g_new, 'f_value': g_new + m_h}
                    frontier.append(child_node)
            elif in_frontier_node:
                if g_new < in_frontier_node['g_value']:
                    in_frontier_node['g_value'] = g_new
                    in_frontier_node['f_value'] = g_new + heuristic_misplaced_tiles(new_state, goal_state)
                    in_frontier_node['parent_node'] = current_node
                    in_frontier_node['action'] = move
                    reached_g[new_state] = g_new
            elif new_state not in reached_g:
                reached_g[new_state] = g_new
                m_h = heuristic_misplaced_tiles(new_state, goal_state)
                child_node = {'state': new_state, 'parent_node': current_node, 'action': move, 'g_value': g_new, 'f_value': g_new + m_h}
                frontier.append(child_node)
    return None

def ida_star_search(initial_state, goal_state, log_func): 
    def search(node, g, f_limit):
        current_state = node['state']
        h = heuristic_misplaced_tiles(current_state, goal_state)
        f = g + h
        if f > f_limit: return f, None 
        if current_state == goal_state: return 'FOUND', node       
        min_cutoff = float('inf')  
        for move in get_valid_moves(current_state):
            new_state, move_cost = apply_move_ucs(current_state, move)
            is_cycle = False
            curr_parent = node
            while curr_parent is not None:
                if curr_parent['state'] == new_state:
                    is_cycle = True
                    break
                curr_parent = curr_parent['parent_node']    
            if is_cycle: continue      
            child_node = {'state': new_state, 'parent_node': node, 'action': move, 'g_value': g + move_cost}  
            log_func(f"  DLS-A* Kiểm tra: f(n)={g + move_cost + heuristic_misplaced_tiles(new_state, goal_state)} (Giới hạn={f_limit})\n  Trạng thái: {new_state}")
            result, found_node = search(child_node, g + move_cost, f_limit)
            if result == 'FOUND': return 'FOUND', found_node   
            if result < min_cutoff: min_cutoff = result   
        return min_cutoff, None

    f_limit = heuristic_misplaced_tiles(initial_state, goal_state)
    start_node = {'state': initial_state, 'parent_node': None, 'action': None, 'g_value': 0}
    loop_count = 1
    while f_limit != float('inf') and loop_count < 100:
        log_func(f"\n=> VÒNG IDA* {loop_count}: Đặt f-giới hạn = {f_limit}")
        result, found_node = search(start_node, 0, f_limit)       
        if result == 'FOUND': return build_path(found_node)
        f_limit = result
        loop_count += 1   
    return None