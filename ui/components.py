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
        
        # Cấu hình giới hạn cuộn hiển thị tối đa 5 mục
        self.max_visible_items = 5
        self.item_height = height
        self.dropdown_max_height = self.max_visible_items * self.item_height
        
        self.scroll_y = 0
        self.max_scroll_y = max(0, (len(self.options) - self.max_visible_items) * self.item_height)
        
        # Cấu hình thanh trượt bên trong danh sách xổ xuống
        self.scrollbar_width = 6
        self.is_dragging = False
        self.drag_start_y = 0
        self.scroll_start_y = 0
        self.scrollbar_rect = pygame.Rect(0, 0, 0, 0)

    def draw(self, screen):
        # 1. Vẽ hộp hiển thị lựa chọn hiện tại đang đóng/mở
        pygame.draw.rect(screen, (248, 249, 250), self.rect, border_radius=4)
        pygame.draw.rect(screen, (189, 195, 199), self.rect, width=2, border_radius=4)
        
        txt_surf = self.font.render(self.options[self.selected_index], True, config.COLOR_TEXT_DARK)
        screen.blit(txt_surf, (self.rect.x + 10, self.rect.y + (self.rect.height - txt_surf.get_height())//2))
        
        arrow_surf = self.font.render("▼" if not self.is_open else "▲", True, config.COLOR_TEXT_DARK)
        screen.blit(arrow_surf, (self.rect.right - 25, self.rect.y + (self.rect.height - arrow_surf.get_height())//2))
        
        # 2. Nếu đang mở, tiến hành vẽ danh sách con giới hạn chiều cao bằng Sub-surface
        if self.is_open:
            actual_items_height = len(self.options) * self.item_height
            view_height = min(actual_items_height, self.dropdown_max_height)
            
            # Định vị khu vực dropdown bao quanh
            dropdown_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, view_height)
            
            # Khởi tạo mặt nạ phụ cắt vùng tràn (Clip Surface)
            clip_surface = pygame.Surface((self.rect.width, view_height), pygame.SRCALPHA)
            pygame.draw.rect(clip_surface, config.COLOR_CARD, (0, 0, self.rect.width, view_height))
            
            # Tính toán vị trí chuột tương đối để xử lý Hover khi có dịch chuyển cuộn trục Y
            mouse_pos = pygame.mouse.get_pos()
            relative_mouse_y = mouse_pos[1] - self.rect.bottom + self.scroll_y
            
            self.hovered_index = -1
            if dropdown_rect.collidepoint(mouse_pos) and not self.is_dragging:
                self.hovered_index = int(relative_mouse_y // self.item_height)
                if self.hovered_index >= len(self.options) or self.hovered_index < 0:
                    self.hovered_index = -1

            # Vẽ danh sách các mục thuật toán lên Surface con
            for i, option in enumerate(self.options):
                item_y_pos = i * self.item_height - self.scroll_y
                item_rect = pygame.Rect(0, item_y_pos, self.rect.width, self.item_height)
                
                # Đổ màu nền nếu đang di chuột qua mục đó
                if i == self.hovered_index:
                    pygame.draw.rect(clip_surface, (220, 225, 230), item_rect)
                    
                pygame.draw.rect(clip_surface, (210, 215, 220), item_rect, width=1)
                opt_surf = self.font.render(option, True, config.COLOR_TEXT_DARK)
                clip_surface.blit(opt_surf, (10, item_y_pos + (self.item_height - opt_surf.get_height())//2))
                
            # 3. Tính toán và vẽ cục kéo trượt (Scrollbar) nếu tổng số lượng vượt quá 5 mục
            if self.max_scroll_y > 0:
                ratio = view_height / actual_items_height
                scrollbar_height = max(int(view_height * ratio), 20)
                
                scroll_percent = self.scroll_y / self.max_scroll_y
                available_track = view_height - scrollbar_height
                scrollbar_y_pos = available_track * scroll_percent
                
                # Định dạng vùng nhận diện nút kéo trượt thực tế trên màn hình chính
                self.scrollbar_rect = pygame.Rect(
                    self.rect.right - self.scrollbar_width - 4,
                    self.rect.bottom + scrollbar_y_pos,
                    self.scrollbar_width,
                    scrollbar_height
                )
                
                # Vẽ thanh trượt đè lên trên bề mặt danh sách xổ xuống
                pygame.draw.rect(clip_surface, (127, 140, 141), (self.rect.width - self.scrollbar_width - 4, scrollbar_y_pos, self.scrollbar_width, scrollbar_height), border_radius=3)
            
            # Đẩy toàn bộ dropdown lên màn hình
            screen.blit(clip_surface, (self.rect.x, self.rect.bottom))
            pygame.draw.rect(screen, (189, 195, 199), dropdown_rect, width=2, border_radius=2)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        actual_items_height = len(self.options) * self.item_height
        view_height = min(actual_items_height, self.dropdown_max_height)
        dropdown_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, view_height)
        
        # Bắt sự kiện kéo chuột trên thanh cuộn của ComboBox
        if self.is_open and self.max_scroll_y > 0:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.scrollbar_rect.collidepoint(mouse_pos):
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
                scrollbar_height = self.scrollbar_rect.height
                available_track = view_height - scrollbar_height
                if available_track > 0:
                    scroll_delta = (delta_y / available_track) * self.max_scroll_y
                    self.scroll_y = max(0, min(self.scroll_start_y + scroll_delta, self.max_scroll_y))
                return True
                
            # Hỗ trợ dùng con lăn chuột ngay trên danh sách xổ xuống
            elif event.type == pygame.MOUSEWHEEL and dropdown_rect.collidepoint(mouse_pos):
                self.scroll_y = max(0, min(self.scroll_y - event.y * self.item_height, self.max_scroll_y))
                return True

        # Bắt sự kiện Click chọn mục mở rộng hoặc đóng danh sách
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_dragging:
                return False
                
            if self.rect.collidepoint(mouse_pos):
                self.is_open = not self.is_open
                return True
            elif self.is_open:
                if dropdown_rect.collidepoint(mouse_pos):
                    # Tính toán chính xác vị trí mục được click sau khi cuộn
                    relative_mouse_y = mouse_pos[1] - self.rect.bottom + self.scroll_y
                    clicked_idx = int(relative_mouse_y // self.item_height)
                    if 0 <= clicked_idx < len(self.options):
                        self.selected_index = clicked_idx
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