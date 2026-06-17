# ai/advanced_search.py
import random
import math
from core.game_logic import get_valid_moves, apply_move
from ai.base_search import build_path
from ai.heuristic_apps import heuristic_misplaced_tiles

# --- SIMULATED ANNEALING ALGORITHM ---
def simulated_annealing(initial_state, goal_state, log_func):
    current_state = initial_state
    T = 100.0
    T_min = 0.01
    alpha = 0.95
    current_node = {
        'state': current_state,
        'parent_node': None,
        'action': None
    }  
    step = 1
    while T > T_min:
        h_current = heuristic_misplaced_tiles(current_state, goal_state)
        log_func(f"Step {step}: Temp T = {round(T, 3)} | h(Current) = {h_current}\nState: {current_state}")
        step += 1
        if current_state == goal_state:
            log_func("=> SUCCESS: Goal state reached!")
            return build_path(current_node)     
        valid_moves = get_valid_moves(current_state)
        if not valid_moves:
            break
        chosen_move = random.choice(valid_moves)
        next_state = apply_move(current_state, chosen_move)
        h_next = heuristic_misplaced_tiles(next_state, goal_state)
        delta = h_next - h_current
        if delta < 0:
            current_state = next_state
            current_node = {
                'state': current_state,
                'parent_node': current_node,
                'action': chosen_move
            }
            log_func(f"  -> Better neighbor accepted! f(n) decreased by {abs(delta)}.")
        else:
            p = math.exp(-delta / T)
            rand_val = random.random()
            if rand_val < p:
                current_state = next_state
                current_node = {
                    'state': current_state,
                    'parent_node': current_node,
                    'action': chosen_move
                }
                log_func(f"  -> Worse neighbor accepted by probability! p = {round(p, 4)} (Rand: {round(rand_val, 4)})")
            else:
                log_func(f"  -> Worse neighbor rejected. p = {round(p, 4)} (Rand: {round(rand_val, 4)})")
        T = alpha * T
        log_func("-" * 35)
    if current_state == goal_state:
        return build_path(current_node)
    log_func("\n=> STOPPED: Temperature cooled down to T_min without reaching Goal.")
    return None