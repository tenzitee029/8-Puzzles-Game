class Puzzle8CSP:
    def __init__(self, goal_state):
        self.goal_state = goal_state
        # 1. Các biến (Variables): 9 vị trí trên bàn cờ 3x3
        self.variables = [f'Pos{i}' for i in range(9)]
        # 2. Miền giá trị (Domains): Mỗi vị trí có thể chứa các số từ 0 đến 8
        self.domains = {var: list(range(9)) for var in self.variables}

    def is_consistent(self, var, value, assignment):
        # Ràng buộc 1: Không được trùng số với các vị trí đã gán khác (AllDiff)
        if value in assignment.values():
            return False
        # Ràng buộc 2: Phải khớp với trạng thái đích tại vị trí đó
        idx = int(var.replace('Pos', ''))
        if value != self.goal_state[idx]:
            return False
        return True

    def conflicts(self, var, value, assignment):
        conflict_count = 0
        idx = int(var.replace('Pos', ''))
        # Xung đột 1: Nếu số này trùng với số của một vị trí khác trên bàn cờ
        for other_var, other_val in assignment.items():
            if other_var != var and other_val == value:
                conflict_count += 1       
        # Xung đột 2: Nếu ô số tại vị trí này không trùng với trạng thái đích (Misplaced Tile)
        if value != self.goal_state[idx]:
            conflict_count += 1 
        return conflict_count