import pygame
import threading
import time
import config
from ui.components import Button, TextBox, ComboBox, ScrollableLogBox, ScrollablePathBox

# Import các thuật toán từ các module phân mảnh mới tách
from ai.base_search import bfs_search, dfs_search, iterative_deepening_search, ucs_search
from ai.heuristic_apps import greedy_search, a_star_search, ida_star_search
from ai.local_search import simple_hill_climbing, steepest_ascent_hill_climbing

class PygameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("8-Puzzle Solver Visualization - Modular Pygame Edition")
        self.clock = pygame.Clock()
        
        self.font_large = pygame.font.SysFont("sans-serif", 36, bold=True)
        self.font_medium = pygame.font.SysFont("sans-serif", 14, bold=True)
        self.font_small = pygame.font.SysFont("sans-serif", 12, bold=True) 
        self.font_code = pygame.font.SysFont("monospace", 12) 

        self.initial_state = (1, 2, 3, 4, 0, 6, 7, 5, 8)
        self.goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.current_state = self.initial_state
        self.path = []
        self.current_step = 0
        self.is_searching = False
        
        self.algorithms = ["BFS", "DFS", "IDS", "UCS", "GREEDY", "A*", "IDA*", "SimpleHC", "SteepestAscentHC"]
        self.logs_data = ["[SYSTEM]: Modular Pygame UI Initialized successfully.", "Choose an algorithm and start searching."]
        self.path_string = "Start -> Awaiting search results..."

        self.init_ui_elements()

    def init_ui_elements(self):
        self.buttons = []
        self.input_box = TextBox(20, 50, 255, 35, "1 2 3 4 0 6 7 5 8", self.font_medium)
        self.btn_update_state = Button(20, 95, 255, 35, "🔄 UPDATE PUZZLE", config.COLOR_PRIMARY, config.COLOR_TEXT_LIGHT, self.font_medium, id_val="UPDATE_STATE")
        self.buttons.append(self.btn_update_state)
        
        self.algo_combo = ComboBox(20, 180, 255, 35, self.algorithms, self.font_medium)
        self.btn_solve = Button(20, 225, 255, 40, "⚡ START SEARCH", config.COLOR_SUCCESS, config.COLOR_TEXT_LIGHT, self.font_medium, id_val="SOLVE")
        self.buttons.append(self.btn_solve)
        
        self.btn_prev = Button(20, 550, 75, 32, "◀ Prev", (127, 140, 141), config.COLOR_TEXT_LIGHT, self.font_small, id_val="PREV")
        self.btn_next = Button(200, 550, 75, 32, "Next ▶", (127, 140, 141), config.COLOR_TEXT_LIGHT, self.font_small, id_val="NEXT")
        self.buttons.append(self.btn_prev)
        self.buttons.append(self.btn_next)

        self.scrollable_log_box = ScrollableLogBox(310, 50, 710, 425, self.font_code)
        self.scrollable_log_box.update_logs(self.logs_data)
        self.scrollable_path_box = ScrollablePathBox(15, 620, 1020, 45, self.font_medium)

    def append_log(self, text):
        for line in text.split('\n'):
            if line.strip(): self.logs_data.append(line)
        if len(self.logs_data) > 3000: self.logs_data.pop(0)
        self.scrollable_log_box.update_logs(self.logs_data)
        if self.is_searching: self.scrollable_log_box.scroll_to_bottom()

    def update_custom_state(self):
        raw_text = self.input_box.text.strip()
        try:
            parsed_nums = [int(x) for x in raw_text.split() if x.strip() != '']
            if len(parsed_nums) != 9 or set(parsed_nums) != set(range(9)): raise ValueError
            self.initial_state = tuple(parsed_nums)
            self.current_state = self.initial_state
            self.path = []
            self.current_step = 0
            self.path_string = "Start -> Puzzle updated. Awaiting search..."
            self.scrollable_path_box.update_text(self.path_string)
            self.logs_data = [f"[SYSTEM]: Successfully updated puzzle state: {self.initial_state}"]
            self.scrollable_log_box.update_logs(self.logs_data)
        except ValueError:
            self.logs_data = ["[DATA ERROR]: Please enter exactly 9 unique numbers!"]
            self.scrollable_log_box.update_logs(self.logs_data)

    def run_search_thread(self):
        self.is_searching = True
        self.btn_solve.bg_color = (149, 165, 166)
        self.btn_solve.text = "SEARCHING..."
        selected_algo = self.algo_combo.get_selected()
        
        self.logs_data = [f"LAUNCHING ALGORITHM: {selected_algo}", f"Initial State: {self.initial_state}"]
        self.scrollable_log_box.update_logs(self.logs_data)
        
        start_time = time.time()
        if selected_algo == "BFS": self.path = bfs_search(self.initial_state, self.goal_state, self.append_log)
        elif selected_algo == "DFS": self.path = dfs_search(self.initial_state, self.goal_state, self.append_log)
        elif selected_algo == "IDS": self.path = iterative_deepening_search(self.initial_state, self.goal_state, self.append_log)
        elif selected_algo == "UCS": self.path = ucs_search(self.initial_state, self.goal_state, self.append_log)
        elif selected_algo == "GREEDY": self.path = greedy_search(self.initial_state, self.goal_state, self.append_log)
        elif selected_algo == "A*": self.path = a_star_search(self.initial_state, self.goal_state, self.append_log)
        elif selected_algo == "IDA*": self.path = ida_star_search(self.initial_state, self.goal_state, self.append_log)
        elif selected_algo == "SimpleHC": self.path = simple_hill_climbing(self.initial_state, self.goal_state, self.append_log)
        elif selected_algo == "SteepestAscentHC": self.path = steepest_ascent_hill_climbing(self.initial_state, self.goal_state, self.append_log)
        end_time = time.time()
        
        if self.path:
            self.append_log(f"=> SUCCESS! Found solution in {round(end_time - start_time, 4)}s!")
            actions = [node['action'] for node in self.path if node['action'] is not None]
            self.path_string = "Start -> " + " -> ".join(actions) + " -> GOAL"
            self.current_step = 0
            self.current_state = self.path[self.current_step]['state']
        else:
            self.append_log("=> FAILED! Solution path not found.")
            self.path_string = "Failure: This puzzle state is unsolvable."
            
        self.scrollable_path_box.update_text(self.path_string)
        self.is_searching = False
        self.btn_solve.bg_color = config.COLOR_SUCCESS
        self.btn_solve.text = "⚡ START SEARCH"

    def draw(self):
        self.screen.fill(config.COLOR_BG)
        mouse_pos = pygame.mouse.get_pos()
        
        left_panel = pygame.Rect(15, 15, 265, 575)
        pygame.draw.rect(self.screen, config.COLOR_CARD, left_panel, border_radius=8)
        
        lbl_input = self.font_medium.render("⚙️ Custom Initial State (9 digits):", True, config.COLOR_PRIMARY)
        self.screen.blit(lbl_input, (25, 25))
        self.input_box.draw(self.screen)
        
        lbl_algo = self.font_medium.render("1. Select Search Algorithm:", True, config.COLOR_TEXT_DARK)
        self.screen.blit(lbl_algo, (25, 155))
        
        for btn in self.buttons:
            btn.check_hover(mouse_pos)
            btn.draw(self.screen)
            
        lbl_board = self.font_medium.render("2. State Matrix View:", True, config.COLOR_TEXT_DARK)
        self.screen.blit(lbl_board, (25, 285))
        
        board_container = pygame.Rect(30, 310, 235, 235)
        pygame.draw.rect(self.screen, config.COLOR_TEXT_DARK, board_container, border_radius=6)
        
        for i in range(9):
            val = self.current_state[i]
            row, col = divmod(i, 3)
            tile_rect = pygame.Rect(35 + col*76, 315 + row*76, 72, 72)
            if val == 0: pygame.draw.rect(self.screen, config.COLOR_BLANK, tile_rect, border_radius=4)
            else:
                pygame.draw.rect(self.screen, config.COLOR_TILE, tile_rect, border_radius=4)
                val_surf = self.font_large.render(str(val), True, config.COLOR_TEXT_DARK)
                val_rect = val_surf.get_rect(center=tile_rect.center)
                self.screen.blit(val_surf, val_rect)
            if val == 0: pygame.draw.rect(self.screen, config.COLOR_DANGER, tile_rect, width=2, border_radius=4)

        total_steps = len(self.path) - 1 if self.path else 0
        lbl_step_num = self.font_medium.render(f"Step: {self.current_step}/{total_steps}", True, config.COLOR_TEXT_DARK)
        self.screen.blit(lbl_step_num, (108, 555))

        self.algo_combo.draw(self.screen)

        right_panel = pygame.Rect(295, 15, 740, 480)
        pygame.draw.rect(self.screen, config.COLOR_CARD, right_panel, border_radius=8)
        lbl_log_title = self.font_medium.render("3. Frontier Node Processing Log:", True, config.COLOR_DANGER)
        self.screen.blit(lbl_log_title, (310, 25))
        self.scrollable_log_box.draw(self.screen)

        bottom_panel = pygame.Rect(15, 600, 1020, 68)
        pygame.draw.rect(self.screen, config.COLOR_CARD, bottom_panel, border_radius=8)
        lbl_path_title = self.font_medium.render("4. Solution Route Trajectory:", True, (142, 68, 173))
        self.screen.blit(lbl_path_title, (25, 603))
        self.scrollable_path_box.draw(self.screen)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            self.input_box.handle_event(event)
            self.scrollable_path_box.handle_event(event)
            self.scrollable_log_box.handle_event(event)
            
            if not self.is_searching: self.algo_combo.handle_event(event)
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.algo_combo.is_open: continue
                mouse_pos = pygame.mouse.get_pos()
                for btn in self.buttons:
                    if btn.rect.collidepoint(mouse_pos):
                        if btn.id_val == "UPDATE_STATE" and not self.is_searching: self.update_custom_state()
                        elif btn.id_val == "SOLVE" and not self.is_searching:
                            threading.Thread(target=self.run_search_thread, daemon=True).start()
                        elif btn.id_val == "PREV" and self.path and self.current_step > 0:
                            self.current_step -= 1
                            self.current_state = self.path[self.current_step]['state']
                        elif btn.id_val == "NEXT" and self.path and self.current_step < len(self.path) - 1:
                            self.current_step += 1
                            self.current_state = self.path[self.current_step]['state']
        return True

    def main_loop(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(config.FPS)
        pygame.quit()