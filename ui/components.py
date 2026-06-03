import pygame
import config

class Button:
    def __init__(self, x, y, width, height, text, bg_color, text_color, font, id_val=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = font
        self.id_val = id_val
        self.is_hovered = False

    def draw(self, screen):
        color = [min(c + 20, 255) for c in self.bg_color] if self.is_hovered else self.bg_color
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        txt_surf = self.font.render(self.text, True, self.text_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, txt_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

class TextBox:
    def __init__(self, x, y, width, height, default_text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = default_text
        self.font = font
        self.is_active = False
        self.color_active = config.COLOR_PRIMARY
        self.color_inactive = (189, 195, 199)

    def draw(self, screen):
        border_color = self.color_active if self.is_active else self.color_inactive
        pygame.draw.rect(screen, (248, 249, 250), self.rect, border_radius=4)
        pygame.draw.rect(screen, border_color, self.rect, width=2, border_radius=4)
        txt_surf = self.font.render(self.text, True, config.COLOR_TEXT_DARK)
        screen.blit(txt_surf, (self.rect.x + 8, self.rect.y + (self.rect.height - txt_surf.get_height())//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.is_active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.is_active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if event.unicode in "0123456789 ":
                    self.text += event.unicode

class ComboBox:
    def __init__(self, x, y, width, height, options, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.font = font
        self.selected_index = 0
        self.is_open = False
        self.hovered_index = -1

    def draw(self, screen):
        pygame.draw.rect(screen, (248, 249, 250), self.rect, border_radius=4)
        pygame.draw.rect(screen, (189, 195, 199), self.rect, width=2, border_radius=4)
        
        txt_surf = self.font.render(self.options[self.selected_index], True, config.COLOR_TEXT_DARK)
        screen.blit(txt_surf, (self.rect.x + 10, self.rect.y + (self.rect.height - txt_surf.get_height())//2))
        
        arrow_surf = self.font.render("▼" if not self.is_open else "▲", True, config.COLOR_TEXT_DARK)
        screen.blit(arrow_surf, (self.rect.right - 25, self.rect.y + (self.rect.height - arrow_surf.get_height())//2))
        
        if self.is_open:
            for i, option in enumerate(self.options):
                item_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.height, self.rect.width, self.rect.height)
                bg_color = (220, 225, 230) if i == self.hovered_index else config.COLOR_CARD
                pygame.draw.rect(screen, bg_color, item_rect)
                pygame.draw.rect(screen, (210, 215, 220), item_rect, width=1)
                
                opt_surf = self.font.render(option, True, config.COLOR_TEXT_DARK)
                screen.blit(opt_surf, (item_rect.x + 10, item_rect.y + (item_rect.height - opt_surf.get_height())//2))

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEMOTION:
            if self.is_open:
                self.hovered_index = -1
                for i in range(len(self.options)):
                    item_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.height, self.rect.width, self.rect.height)
                    if item_rect.collidepoint(mouse_pos):
                        self.hovered_index = i
                        break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.is_open = not self.is_open
                return True
            elif self.is_open:
                for i in range(len(self.options)):
                    item_rect = pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.height, self.rect.width, self.rect.height)
                    if item_rect.collidepoint(mouse_pos):
                        self.selected_index = i
                        self.is_open = False
                        return True
                self.is_open = False
        return False

    def get_selected(self):
        return self.options[self.selected_index]

class ScrollableLogBox:
    def __init__(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.line_height = 16
        self.scroll_y = 0
        self.max_scroll_y = 0
        self.logs_list = []
        self.scrollbar_width = 8
        self.scrollbar_rect = pygame.Rect(self.rect.right - self.scrollbar_width - 4, self.rect.y + 4, self.scrollbar_width, 30)
        self.is_dragging = False
        self.drag_start_y = 0
        self.scroll_start_y = 0

    def update_logs(self, logs_list):
        self.logs_list = logs_list
        total_content_height = len(self.logs_list) * self.line_height
        view_height = self.rect.height - 20
        
        if total_content_height > view_height: self.max_scroll_y = total_content_height - view_height
        else:
            self.max_scroll_y = 0
            self.scroll_y = 0

    def scroll_to_bottom(self):
        self.scroll_y = self.max_scroll_y

    def draw(self, screen):
        pygame.draw.rect(screen, config.COLOR_LOG_BG, self.rect, border_radius=6)
        view_width = self.rect.width - 20 if self.max_scroll_y == 0 else self.rect.width - 25
        view_height = self.rect.height - 20
        clip_surface = pygame.Surface((view_width, view_height), pygame.SRCALPHA)
        
        for index, line in enumerate(self.logs_list):
            line_surf = self.font.render(line, True, config.COLOR_LOG_TXT)
            clip_surface.blit(line_surf, (10, index * self.line_height - self.scroll_y))
            
        screen.blit(clip_surface, (self.rect.x + 5, self.rect.y + 10))
        
        if self.max_scroll_y > 0:
            total_content_height = len(self.logs_list) * self.line_height
            ratio = view_height / total_content_height
            scrollbar_height = max(int(view_height * ratio), 30)
            scroll_percent = self.scroll_y / self.max_scroll_y
            available_track = view_height - scrollbar_height
            scrollbar_pos_y = self.rect.y + 10 + (available_track * scroll_percent)
            
            self.scrollbar_rect = pygame.Rect(self.rect.right - self.scrollbar_width - 6, scrollbar_pos_y, self.scrollbar_width, scrollbar_height)
            bar_color = (127, 140, 141) if not self.is_dragging else (189, 195, 199)
            pygame.draw.rect(screen, bar_color, self.scrollbar_rect, border_radius=4)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.scrollbar_rect.collidepoint(mouse_pos) and self.max_scroll_y > 0:
                self.is_dragging = True
                self.drag_start_y = mouse_pos[1]
                self.scroll_start_y = self.scroll_y
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            delta_y = mouse_pos[1] - self.drag_start_y
            view_height = self.rect.height - 20
            scrollbar_height = self.scrollbar_rect.height
            available_track = view_height - scrollbar_height
            if available_track > 0:
                scroll_delta = (delta_y / available_track) * self.max_scroll_y
                self.scroll_y = max(0, min(self.scroll_start_y + scroll_delta, self.max_scroll_y))
            return True
        elif event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(mouse_pos) and self.max_scroll_y > 0:
            self.scroll_y = max(0, min(self.scroll_y - event.y * self.line_height * 2, self.max_scroll_y))
            return True
        return False

class ScrollablePathBox:
    def __init__(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.scroll_x = 0
        self.max_scroll_x = 0
        self.text_width = 0
        self.scrollbar_height = 8
        self.scrollbar_rect = pygame.Rect(x + 5, y + height - self.scrollbar_height - 5, 50, self.scrollbar_height)
        self.is_dragging = False
        self.drag_start_x = 0
        self.scroll_start_x = 0
        self.update_text("Start -> Awaiting search results...")

    def update_text(self, text_string):
        self.text_surf = self.font.render(text_string, True, config.COLOR_TEXT_DARK)
        self.text_width = self.text_surf.get_width()
        view_width = self.rect.width - 30 
        if self.text_width > view_width: self.max_scroll_x = self.text_width - view_width
        else:
            self.max_scroll_x = 0
            self.scroll_x = 0

    def draw(self, screen):
        pygame.draw.rect(screen, (241, 196, 15), self.rect, border_radius=6)
        view_width = self.rect.width - 20
        view_height = self.rect.height - 20
        clip_surface = pygame.Surface((view_width, view_height), pygame.SRCALPHA)
        clip_surface.blit(self.text_surf, (-self.scroll_x, (view_height - self.text_surf.get_height()) // 2 - 2))
        screen.blit(clip_surface, (self.rect.x + 10, self.rect.y + 5))
        
        if self.max_scroll_x > 0:
            ratio = view_width / self.text_width
            scrollbar_width = max(int(view_width * ratio), 30)
            scroll_percent = self.scroll_x / self.max_scroll_x
            available_track = view_width - scrollbar_width
            scrollbar_pos_x = self.rect.x + 10 + (available_track * scroll_percent)
            self.scrollbar_rect = pygame.Rect(scrollbar_pos_x, self.rect.bottom - self.scrollbar_height - 6, scrollbar_width, self.scrollbar_height)
            bar_color = (44, 62, 80) if not self.is_dragging else (52, 73, 94)
            pygame.draw.rect(screen, bar_color, self.scrollbar_rect, border_radius=4)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.scrollbar_rect.collidepoint(mouse_pos) and self.max_scroll_x > 0:
                self.is_dragging = True
                self.drag_start_x = mouse_pos[0]
                self.scroll_start_x = self.scroll_x
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            delta_x = mouse_pos[0] - self.drag_start_x
            view_width = self.rect.width - 20
            scrollbar_width = self.scrollbar_rect.width
            available_track = view_width - scrollbar_width
            if available_track > 0:
                scroll_delta = (delta_x / available_track) * self.max_scroll_x
                self.scroll_x = max(0, min(self.scroll_start_x + scroll_delta, self.max_scroll_x))
            return True
        elif event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(mouse_pos) and self.max_scroll_x > 0:
            self.scroll_x = max(0, min(self.scroll_x - event.y * 30, self.max_scroll_x))
            return True
        return False