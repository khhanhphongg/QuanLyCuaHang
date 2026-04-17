"""Định nghĩa bảng màu, font và cấu hình ttk dùng chung cho toàn bộ UI."""

import platform
from tkinter import ttk


# Chọn font mặc định theo hệ điều hành để đảm bảo hiển thị ổn định.
if platform.system() == "Windows":
    FONT_FAMILY = "Segoe UI"
    MONO_FAMILY = "Consolas"
elif platform.system() == "Darwin":
    FONT_FAMILY = "Helvetica Neue"
    MONO_FAMILY = "Menlo"
else:
    FONT_FAMILY = "DejaVu Sans"
    MONO_FAMILY = "DejaVu Sans Mono"


# Bảng màu chuẩn hoá cho các thành phần UI (Premium & Sleek).
COLORS = {
    "bg": "#EEF2F6", # Nền xanh nhạt sang trọng
    "surface": "#FFFFFF", # Màu nền thẻ (card)
    "surface_muted": "#F3F6F9", # Màu nền nhẹ cho vùng phụ
    "border": "#D1D5DB", # Viền mềm mại
    "text": "#111827", # Text chính đậm, dễ đọc
    "text_muted": "#4B5563", # Text phụ nhìn dịu
    "primary": "#3B82F6", # Xanh dương primary hiện đại
    "primary_hover": "#2563EB", 
    "success": "#10B981", # Xanh lá tươi
    "success_hover": "#059669",
    "warning": "#F59E0B", # Cam nhe
    "warning_hover": "#D97706",
    "danger": "#EF4444", # Đỏ cảnh báo nổi bật
    "danger_hover": "#DC2626",
    "info": "#06B6D4",
    "info_hover": "#0891B2",
    "input_bg": "#F9FAFB", # Nền input
    "table_head": "#E5E7EB", # Tiêu đề bảng
    "row_selected": "#BFDBFE", # Dòng đang chọn ánh xanh dương
    "neutral_btn": "#E5E7EB",
    "neutral_btn_hover": "#D1D5DB",
    "primary_soft": "#DBEAFE",
    "success_soft": "#D1FAE5",
    "warning_soft": "#FEF3C7",
    "danger_soft": "#FEE2E2",
    "disabled_bg": "#F3F4F6",
    "accent": "#8B5CF6",          # Tím accent hiện đại
    "accent_dark": "#7C3AED",     # Tím đậm hover
}

# Các cấp độ chữ dùng trong toàn ứng dụng.
FONTS = {
    "title_large": (FONT_FAMILY, 28, "bold"),
    "title": (FONT_FAMILY, 22, "bold"),
    "section": (FONT_FAMILY, 15, "bold"),
    "subtitle": (FONT_FAMILY, 13, "bold"),
    "body": (FONT_FAMILY, 12),
    "body_bold": (FONT_FAMILY, 12, "bold"),
    "small": (FONT_FAMILY, 11),
    "table": (FONT_FAMILY, 11),
    "table_heading": (FONT_FAMILY, 12, "bold"),
    "mono": (MONO_FAMILY, 11),
}


def apply_ttk_theme():
    """Thiết lập style cho các widget ttk (Treeview, Combobox)."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(
        "Treeview.Heading",
        font=FONTS["table_heading"],
        background=COLORS["table_head"],
        foreground=COLORS["text"],
        relief="flat",
    )
    style.configure(
        "Treeview",
        font=FONTS["table"],
        background=COLORS["surface"],
        fieldbackground=COLORS["surface"],
        rowheight=28,
        borderwidth=0,
    )
    style.map(
        "Treeview",
        background=[("selected", COLORS["row_selected"])],
        foreground=[("selected", COLORS["text"])],
    )
    style.configure(
        "TCombobox",
        padding=3,
        foreground=COLORS["text"],
        fieldbackground=COLORS["input_bg"],
        background=COLORS["input_bg"],
    )
