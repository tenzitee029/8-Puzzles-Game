# Nguyễn Nhật Tiến - 24110351 _ AI
# 8-Puzzles Game

Ứng dụng được xây dựng bằng **Pygame** nhằm mục đích mô phỏng, đánh giá các chiến lược tìm kiếm trí tuệ nhân tạo (AI) khác nhau áp dụng cho bài toán 8-Puzzle kinh điển.

---

## 📂 Kiến Trúc Cấu Trúc Thư Mục

Mã nguồn dự án được tổ chức chặt chẽ theo cấu trúc thư mục phân mảnh (Modular Architecture) giúp cô lập cấu trúc dữ liệu, thành phần giao diện, cấu hình hệ thống và các nhóm giải thuật AI riêng biệt:

- **core/**: Chứa công cụ giả lập trò chơi cốt lõi (game_logic.py quản lý luật trượt ô, tìm nước đi hợp lệ và chi phí).
- **ai/**: Nơi quản lý các tầng thuật toán tìm kiếm AI phân tách độc lập.
- **ui/**: Lớp quản trị giao diện đồ họa trừu tượng (components.py đóng gói logic nút bấm, hộp textbox nhập liệu và hộp combobox khóa 5 dòng hiển thị).
- **config.py**: Quản lý tập trung hệ hằng số hệ thống, bảng màu chủ đạo và khóa tốc độ khung hình (FPS).
- **gui_pygame.py**: Lớp điều phối giao diện tổng, tiếp nhận sự kiện chuột/bàn phím và định tuyến luồng xử lý AI.
- **main.py**: Điểm khởi chạy của toàn bộ chương trình.

---

## 🚀 Hướng Dẫn Cài Đặt Và Khởi Chạy

Chạy file main.py

### Điều kiện tiên quyết

Ứng dụng chạy trên môi trường Python chuẩn và yêu cầu thư viện đồ họa **Pygame**.

```bash
pip install pygame
