import random
from core.game_logic import get_valid_moves, apply_move


def manhattan_distance(state, goal_state):
    distance = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue
        goal_index = goal_state.index(tile)
        distance += abs(index // 3 - goal_index // 3) + abs(index % 3 - goal_index % 3)
    return distance


def evaluate_state(state, goal_state):
    # Higher values are better for the AI player.
    return 100 - manhattan_distance(state, goal_state)


def _minimax(state, goal_state, depth, maximizing_player, bad_states=None):
    if state == goal_state or depth == 0:
        return evaluate_state(state, goal_state), None

    if bad_states is None:
        bad_states = set()

    moves = _filter_moves(state, bad_states)
    if not moves:
        moves = get_valid_moves(state)

    best_move = None
    if maximizing_player:
        best_value = float('-inf')
        random.shuffle(moves)
        for move in moves:
            next_state = apply_move(state, move)
            value, _ = _minimax(next_state, goal_state, depth - 1, False, bad_states | {state})
            if value > best_value:
                best_value = value
                best_move = move
        return best_value, best_move
    else:
        best_value = float('inf')
        random.shuffle(moves)
        for move in moves:
            next_state = apply_move(state, move)
            value, _ = _minimax(next_state, goal_state, depth - 1, True, bad_states | {state})
            if value < best_value:
                best_value = value
                best_move = move
        return best_value, best_move


def _alphabeta(state, goal_state, depth, alpha, beta, maximizing_player, bad_states=None):
    if state == goal_state or depth == 0:
        return evaluate_state(state, goal_state), None

    if bad_states is None:
        bad_states = set()

    moves = _filter_moves(state, bad_states)
    if not moves:
        moves = get_valid_moves(state)

    best_move = None
    if maximizing_player:
        value = float('-inf')
        random.shuffle(moves)
        for move in moves:
            next_state = apply_move(state, move)
            child_value, _ = _alphabeta(next_state, goal_state, depth - 1, alpha, beta, False, bad_states | {state})
            if child_value > value:
                value = child_value
                best_move = move
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value, best_move
    else:
        value = float('inf')
        random.shuffle(moves)
        for move in moves:
            next_state = apply_move(state, move)
            child_value, _ = _alphabeta(next_state, goal_state, depth - 1, alpha, beta, True, bad_states | {state})
            if child_value < value:
                value = child_value
                best_move = move
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value, best_move


def _expectimax(state, goal_state, depth, maximizing_player, bad_states=None):
    if state == goal_state or depth == 0:
        return evaluate_state(state, goal_state), None

    if bad_states is None:
        bad_states = set()

    moves = _filter_moves(state, bad_states)
    if not moves:
        moves = get_valid_moves(state)

    if maximizing_player:
        best_value = float('-inf')
        best_move = None
        random.shuffle(moves)
        for move in moves:
            next_state = apply_move(state, move)
            value, _ = _expectimax(next_state, goal_state, depth - 1, False, bad_states | {state})
            if value > best_value:
                best_value = value
                best_move = move
        return best_value, best_move
    else:
        total_value = 0
        for move in moves:
            next_state = apply_move(state, move)
            value, _ = _expectimax(next_state, goal_state, depth - 1, True, bad_states | {state})
            total_value += value
        return total_value / len(moves), None


def _filter_moves(state, bad_states=None):
    if bad_states is None:
        bad_states = set()
    return [move for move in get_valid_moves(state) if apply_move(state, move) not in bad_states]


def choose_ai_move(state, goal_state, algorithm, log_func, depth=4, bad_states=None):
    if state == goal_state:
        return None

    if algorithm == "Adversarial - Minimax":
        score, move = _minimax(state, goal_state, depth, True, set(bad_states) if bad_states else None)
        log_func(f"[AI] Minimax chooses {move} with score {round(score, 2)}")
        return move
    if algorithm == "Adversarial - Alpha-Beta":
        score, move = _alphabeta(state, goal_state, depth, float('-inf'), float('inf'), True, set(bad_states) if bad_states else None)
        log_func(f"[AI] Alpha-Beta chooses {move} with score {round(score, 2)}")
        return move
    if algorithm == "Adversarial - Expectimax":
        score, move = _expectimax(state, goal_state, depth, True, set(bad_states) if bad_states else None)
        log_func(f"[AI] Expectimax chooses {move} with score {round(score, 2)}")
        return move
    return None


def choose_bot_move(state, goal_state, algorithm, log_func, bad_states=None):
    moves = _filter_moves(state, set(bad_states) if bad_states else None)
    if not moves:
        moves = get_valid_moves(state)

    best_score = float('-inf')
    best_moves = []
    for move in moves:
        next_state = apply_move(state, move)
        score = evaluate_state(next_state, goal_state)
        if score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    if algorithm == "Adversarial - Expectimax":
        move = random.choice(best_moves)
        log_func(f"[Bot] Expectimax-like move chosen: {move} (score {round(best_score,2)})")
        return move

    move = random.choice(best_moves)
    log_func(f"[Bot] Best move chosen: {move} (score {round(best_score,2)})")
    return move


def play_adversarial_match(initial_state, goal_state, algorithm, log_func):
    current_state = initial_state
    current_player = "AI"
    history = [{'player': 'Start', 'state': current_state, 'action': None}]
    turn = 0
    winner = None
    max_turns = 80
    last_state = None

    while turn < max_turns:
        if current_state == goal_state:
            winner = "AI" if current_player == "Bot" else "Bot"
            log_func(f"[RESULT] {winner} reached the goal state!")
            break

        if current_player == "AI":
            move = choose_ai_move(current_state, goal_state, algorithm, log_func, depth=4, bad_states=[last_state] if last_state else None)
            if not move:
                log_func("[AI] No move available.")
                break
            next_state = apply_move(current_state, move)
            history.append({'player': 'AI', 'state': next_state, 'action': move})
            last_state = current_state
            current_state = next_state
            if current_state == goal_state:
                winner = "AI"
                log_func("[RESULT] AI reached the goal state!")
                break
            current_player = "Bot"
        else:
            move = choose_bot_move(current_state, goal_state, algorithm, log_func, bad_states=[last_state] if last_state else None)
            if not move:
                log_func("[Bot] No move available.")
                break
            next_state = apply_move(current_state, move)
            history.append({'player': 'Bot', 'state': next_state, 'action': move})
            last_state = current_state
            current_state = next_state
            if current_state == goal_state:
                winner = "Bot"
                log_func("[RESULT] Bot reached the goal state!")
                break
            current_player = "AI"

        turn += 1

    if not winner:
        if current_state == goal_state:
            winner = "AI" if current_player == "Bot" else "Bot"
        else:
            winner = "Draw"
            log_func("[RESULT] Maximum turns reached without a winner. Draw.")

    return history, winner
