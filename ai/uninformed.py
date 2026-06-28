from core.game_logic import get_valid_moves, apply_move, apply_move_ucs

def build_path(goal_node):
    path = []
    current = goal_node
    while current is not None:
        path.append(current)
        current = current.get('parent_node')
    path.reverse()
    return path

def bfs_search(initial_state, goal_state, log_func):
    start_node = {'state': initial_state, 'parent_node': None, 'action': None}
    if initial_state == goal_state: return build_path(start_node)
    queue = [start_node] 
    visited_states = {initial_state}
    step = 1
    while queue:
        current_node = queue.pop(0) 
        log_func(f"Bước {step}: Lấy nút từ hàng đợi\nTrạng thái: {current_node['state']}")
        step += 1
        for move in get_valid_moves(current_node['state']):
            new_state = apply_move(current_node['state'], move)
            if new_state not in visited_states:
                child_node = {'state': new_state, 'parent_node': current_node, 'action': move}
                if new_state == goal_state: return build_path(child_node)
                queue.append(child_node)
                visited_states.add(new_state)
    return None

def dfs_search(initial_state, goal_state, log_func):
    start_node = {'state': initial_state, 'parent_node': None, 'action': None}    
    if initial_state == goal_state: return build_path(start_node)
    stack = [start_node] 
    visited_states = {initial_state}
    step = 1
    while stack:
        current_node = stack.pop() 
        log_func(f"Bước {step}: Lấy nút từ đỉnh ngăn xếp\nTrạng thái: {current_node['state']}")
        step += 1
        possible_moves = get_valid_moves(current_node['state'])
        possible_moves.reverse()    
        for move in possible_moves:
            new_state = apply_move(current_node['state'], move)
            if new_state not in visited_states:
                child_node = {'state': new_state, 'parent_node': current_node, 'action': move}         
                if new_state == goal_state: return build_path(child_node)
                stack.append(child_node)
                visited_states.add(new_state)
    return None

def is_cycle(node):
    current = node['parent_node']
    while current is not None:
        if current['state'] == node['state']: return True
        current = current['parent_node']
    return False

def depth_limited_search(initial_state, goal_state, limit, log_func):
    start_node = {'state': initial_state, 'parent_node': None, 'action': None, 'depth': 0}
    stack = [start_node]
    result = 'failure'
    step = 1
    while stack:
        node = stack.pop()
        log_func(f"  Bước DLS {step}: Kiểm tra nút (Độ sâu={node['depth']})\n  Trạng thái: {node['state']}")
        step += 1
        if node['state'] == goal_state: return node  
        if node['depth'] > limit:
            result = 'cutoff'
        elif not is_cycle(node):
            possible_moves = get_valid_moves(node['state'])
            possible_moves.reverse()
            for move in possible_moves:
                new_state = apply_move(node['state'], move)
                child_node = {'state': new_state, 'parent_node': node, 'action': move, 'depth': node['depth'] + 1}
                stack.append(child_node)            
    return result

def iterative_deepening_search(initial_state, goal_state, log_func):
    depth = 0
    while depth < 22:
        log_func(f"\n=> ĐANG TÌM KIẾM VỚI NGƯỠNG ĐỘ SÂU = {depth}")
        result = depth_limited_search(initial_state, goal_state, depth, log_func)
        if result != 'cutoff': 
            if result != 'failure': return build_path(result)
            return None
        depth += 1
    return None

def ucs_search(initial_state, goal_state, log_func):
    start_node = {'state': initial_state, 'parent_node': None, 'action': None, 'path_cost': 0}
    if initial_state == goal_state: return build_path(start_node)
    queue = [start_node] 
    visited_states = {initial_state}
    step = 1
    while queue:
        current_node = queue[0]
        for node in queue:
            if node['path_cost'] < current_node['path_cost']:
                current_node = node
        queue.remove(current_node)
        log_func(f"Bước {step}: Lấy nút có chi phí nhỏ nhất (Tổng chi phí={current_node['path_cost']})\nTrạng thái: {current_node['state']}")
        step += 1
        for move in get_valid_moves(current_node['state']):
            new_state, move_cost = apply_move_ucs(current_node['state'], move)
            if new_state not in visited_states:
                total_child_cost = current_node['path_cost'] + move_cost
                child_node = {'state': new_state, 'parent_node': current_node, 'action': move, 'path_cost': total_child_cost}
                if new_state == goal_state: return build_path(child_node)
                queue.append(child_node)
                visited_states.add(new_state)
    return None