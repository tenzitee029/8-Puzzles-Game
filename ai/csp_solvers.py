# ai/csp_solvers.py
import random
import copy

def convert_assignment_to_state(assignment):
    state_list = [0] * 9
    for var, value in assignment.items():
        idx = int(var.replace('Pos', ''))
        state_list[idx] = value
    return tuple(state_list)

# 1. THUẬT TOÁN BACKTRACKING SEARCH
def backtracking_search(csp, log_func):
    log_func("[CSP]: Khởi chạy Backtracking Search trên 8-Puzzle...")
    path_visual = []
    def recursive_backtracking(assignment):
        if len(assignment) == len(csp.variables):
            return assignment
        unassigned = [v for v in csp.variables if v not in assignment]
        var = unassigned[0]
        for value in csp.domains[var]:
            if csp.is_consistent(var, value, assignment):
                assignment[var] = value
                current_puzzle_state = convert_assignment_to_state(assignment)
                log_func(f"  Gán {var} = {value} -> Trạng thái: {current_puzzle_state}")
                path_visual.append({'state': current_puzzle_state, 'action': f"Assign {var}={value}"})
                result = recursive_backtracking(assignment)
                if result != 'failure':
                    return result   
                del assignment[var]
                if path_visual: path_visual.pop()
        return 'failure'
    final_result = recursive_backtracking({})
    if final_result != 'failure':
        log_func(f"=> THÀNH CÔNG: Đã gán thành công cấu hình ĐÍCH!")
        return path_visual
    return None

# 2. THUẬT TOÁN FORWARD CHECKING SEARCH
def forward_checking_search(csp, log_func):
    log_func("[CSP]: Khởi chạy Forward Checking trên 8-Puzzle...")
    path_visual = []
    def forward_check(csp_domains, var, value):
        local_domains = copy.deepcopy(csp_domains)
        for other_var in csp.variables:
            if other_var != var and value in local_domains[other_var]:
                local_domains[other_var].remove(value)
                if not local_domains[other_var]:
                    return 'failure', local_domains
        return 'success', local_domains
    def recursive_forward_check(assignment, current_domains):
        if len(assignment) == len(csp.variables):
            return assignment 
        unassigned = [v for v in csp.variables if v not in assignment]
        var = unassigned[0] 
        for value in current_domains[var]:
            if csp.is_consistent(var, value, assignment):
                assignment[var] = value
                current_puzzle_state = convert_assignment_to_state(assignment)
                path_visual.append({'state': current_puzzle_state, 'action': f"FC Assign {var}={value}"})
                status, updated_domains = forward_check(current_domains, var, value)
                if status != 'failure':
                    log_func(f"  FC thành công {var}={value}. Tỉa miền giá trị số {value} ở các ô còn lại.")
                    result = recursive_forward_check(assignment, updated_domains)
                    if result != 'failure':
                        return result          
                log_func(f"  -> Thất bại nhánh {var}={value}, khôi phục miền giá trị.")
                del assignment[var]
                if path_visual: path_visual.pop()
        return 'failure'
    final_result = recursive_forward_check({}, csp.domains)
    if final_result != 'failure':
        log_func(f"=> THÀNH CÔNG (Forward Checking)!")
        return path_visual
    return None

# 3. THUẬT TOÁN KIỂM TRA TÍNH NHẤT QUÁN CUNG AC-3
def ac3_search(csp, log_func):
    log_func("[CSP]: Khởi chạy lan truyền ràng buộc AC-3 trên 8-Puzzle...")
    local_domains = copy.deepcopy(csp.domains)
    queue = []
    for x_i in csp.variables:
        for x_j in csp.variables:
            if x_i != x_j:
                queue.append((x_i, x_j))
    def rm_inconsistent_values(x_i, x_j):
        removed = False
        idx_j = int(x_j.replace('Pos', ''))
        goal_val_j = csp.goal_state[idx_j]
        for x in list(local_domains[x_i]):
            satisfiable = any(x != y and x == csp.goal_state[int(x_i.replace('Pos', ''))] for y in local_domains[x_j])
            if not satisfiable:
                local_domains[x_i].remove(x)
                removed = True
        return removed
    while queue:
        x_i, x_j = queue.pop(0)
        if rm_inconsistent_values(x_i, x_j):
            log_func(f"  AC-3 tỉa miền giá trị của {x_i} dựa trên ràng buộc chéo với {x_j}.")
            for x_k in csp.variables:
                if x_k != x_i and x_k != x_j:
                    queue.append((x_k, x_i))                
    log_func(f"=> AC-3 hoàn tất cắt tỉa! Miền giá trị thu gọn cuối cùng:\n  {local_domains}")
    final_assigned = {k: v[0] for k, v in local_domains.items() if len(v) == 1}
    return [{'state': convert_assignment_to_state(final_assigned), 'action': 'AC-3 Constraint Arc Filtered'}]

# 4. THUẬT TOÁN MIN-CONFLICTS
def min_conflicts_search(csp, log_func):
    max_steps = 150
    log_func(f"[CSP]: Khởi chạy Min-Conflicts Search trên 8-Puzzle (Max steps = {max_steps})...")
    current = {}
    shuffled_tiles = list(range(9))
    random.shuffle(shuffled_tiles)
    for i, var in enumerate(csp.variables):
        current[var] = shuffled_tiles[i]
    path_visual = []  
    for i in range(1, max_steps + 1):
        current_puzzle_state = convert_assignment_to_state(current)
        total_conflicts = sum(1 for v in csp.variables if current[v] != csp.goal_state[int(v.replace('Pos', ''))])
        log_func(f"  Step {i}: Cấu hình bàn cờ: {current_puzzle_state} | Số ô sai vị trí (Xung đột) = {total_conflicts}")
        path_visual.append({'state': current_puzzle_state, 'action': f"Step {i} (Conflicts: {total_conflicts})"}) 
        if total_conflicts == 0:
            log_func(f"=> THÀNH CÔNG: Min-Conflicts đã sửa bàn cờ về đúng trạng thái đích tại bước {i}!")
            return path_visual
        conflicted_vars = [v for v in csp.variables if current[v] != csp.goal_state[int(v.replace('Pos', ''))]]
        var = random.choice(conflicted_vars)
        best_value = current[var]
        min_conf = float('inf') 
        for val in csp.domains[var]:
            c_count = csp.conflicts(var, val, current)
            if c_count < min_conf:
                min_conf = c_count
                best_value = val
        current[var] = best_value     
    log_func(f"=> THẤT BẠI: Qua {max_steps} bước nhưng cấu hình chưa hội tụ về trạng thái đích.")
    return None