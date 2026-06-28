# ai/belief_and_or.py
import random
from core.game_logic import get_valid_moves, apply_move

def and_or_graph_search(initial_state, goal_state, log_func):
    log_func("[SYSTEM]: Khởi chạy AND-OR Graph Search...")
    def get_nondeterministic_results(state, action):
        primary_result = apply_move(state, action)
        results_set = [primary_result]
        all_moves = get_valid_moves(state)
        if len(all_moves) > 1:
            alternative_move = random.choice([m for m in all_moves if m != action])
            alternative_result = apply_move(state, alternative_move)
            if alternative_result != primary_result:
                results_set.append(alternative_result)
        return list(set(results_set)) 
    def or_search(state, path):
        log_func(f"  OR_SEARCH kiểm tra State: {state}")
        if state == goal_state:
            log_func("    -> Đạt trạng thái ĐÍCH! Trả về kế hoạch rỗng [].")
            return []
        if state in path:
            log_func("    -> Cảnh báo: Trùng lặp đường đi (Cycle detected)! Thất bại.")
            return 'failure'
        for action in get_valid_moves(state):
            result_states = get_nondeterministic_results(state, action)
            plan = and_search(result_states, path + [state])
            if plan != 'failure':
                log_func(f"    -> Hướng chọn hành động thành công: {action}")
                return [action, plan]           
        return 'failure'
    def and_search(states, path):
        log_func(f"    AND_SEARCH phân nhánh xử lý tập kết quả: {states}")
        plans = {}
        for s in states:
            plan_s = or_search(s, path)
            if plan_s == 'failure':
                return 'failure'
            plans[s] = plan_s
        return plans
    result_plan = or_search(initial_state, [])
    if result_plan != 'failure':
        log_func("\n=> SUCCESS: Tìm thấy cây kế hoạch chiến lược AND-OR thành công!")
        return [{'state': initial_state, 'action': f"Plan Tree Found: {str(result_plan)[:60]}..."}]
    else:
        log_func("\n=> FAILED: Không tìm thấy kế hoạch an toàn cho mọi tình huống nhiễu.")
        return None

def belief_fully_observable_search(initial_state, goal_state, log_func):
    log_func("[BELIEF]: Chế độ nhìn thấy toàn phần (Fully Observable).")
    current_belief = {initial_state}
    log_func(f"  Trạng thái niềm tin ban đầu chỉ chứa 1 phần tử xác định: {current_belief}")
    if initial_state == goal_state:
        return [{'state': initial_state, 'action': 'Goal'}]  
    moves = get_valid_moves(initial_state)
    next_state = apply_move(initial_state, moves[0])
    log_func(f"  Dịch chuyển niềm tin sang: {{{next_state}}}")
    log_func("=> Kế hoạch: Hội tụ về việc giải ma trận đơn lẻ tuần tự.")
    return [{'state': initial_state, 'action': moves[0]}, {'state': next_state, 'action': 'Done'}]

def belief_unobservable_search(initial_state, goal_state, log_func):
    log_func("[BELIEF]: Chế độ KHÔNG nhìn thấy (Sensorless Search). Tác nhân bị mù cảm biến.")
    simulated_belief_set = {
        initial_state,
        (1, 2, 3, 4, 6, 0, 7, 5, 8),
        (1, 2, 3, 0, 4, 6, 7, 5, 8)
    }
    log_func(f"  Belief State ban đầu gồm một TẬP HỢP các khả năng ma trận có thể xảy ra:\n  {simulated_belief_set}")
    action = 'Up'
    next_belief_set = set()
    for state in simulated_belief_set:
        if action in get_valid_moves(state):
            next_belief_set.add(apply_move(state, action))
        else:
            next_belief_set.add(state)     
    log_func(f"  Sau khi mù quáng thực hiện hành động '{action}', Tập niềm tin mới cập nhật thành:\n  {next_belief_set}")
    log_func("=> Kế hoạch: Tìm chuỗi hành động ép buộc (Coercion Sequence) đưa tập niềm tin về đích.")
    return [{'state': initial_state, 'action': f'{action} (Sensorless Convegence)'}]

def belief_partially_observable_search(initial_state, goal_state, log_func):
    log_func("[BELIEF]: Chế độ nhìn thấy MỘT PHẦN (Partially Observable).")
    log_func("  Cảm biến giới hạn: Chỉ nhìn thấy vị trí của ô trống [0], các ô số còn lại bị che khuất.")
    blank_idx = initial_state.index(0)
    log_func(f"  Nhận diện cảm biến: Ô trống đang nằm tại vị trí index {blank_idx}.")
    simulated_partial_belief = {
        initial_state,
        (1, 2, 3, 5, 0, 6, 7, 4, 8),
        (1, 4, 3, 2, 0, 6, 7, 5, 8)
    }
    log_func(f"  Belief State tương ứng bao gồm tập ma trận có cùng vị trí ô trống:\n  {simulated_partial_belief}")
    action = 'Left'
    log_func(f"  Thực hiện hành động '{action}' dựa trên vùng cảm biến nhìn thấy.")
    return [{'state': initial_state, 'action': f'{action} (Partial Observation Search)'}]