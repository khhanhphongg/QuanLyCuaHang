"""Gợi ý tìm kiếm theo lúc gõ cho các ô Entry của Tkinter."""

from tkinter import END, Listbox, SOLID, Toplevel


class SearchSuggest:
    """Hiển thị popup gợi ý nhỏ, có debounce và hỗ trợ bàn phím."""

    def __init__(self, root, entry, fetch_callback, select_callback=None, min_chars=1, delay_ms=120, max_items=8):
        self.root = root
        self.entry = entry
        self.fetch_callback = fetch_callback
        self.select_callback = select_callback
        self.min_chars = min_chars
        self.delay_ms = delay_ms
        self.max_items = max_items

        self.popup = None
        self.listbox = None
        self.results = []
        self.after_id = None

        self.entry.bind("<KeyRelease>", self._on_key_release, add="+")
        self.entry.bind("<Down>", self._on_entry_down, add="+")
        self.entry.bind("<Return>", self._on_entry_return, add="+")
        self.entry.bind("<Escape>", self._on_escape, add="+")
        self.entry.bind("<FocusOut>", self._on_focus_out, add="+")

    def _on_key_release(self, event):
        """Debounce việc lấy gợi ý để tránh query mỗi phím quá dày."""
        if event.keysym in {
            "Up", "Down", "Left", "Right", "Return", "Escape", "Tab",
            "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R",
        }:
            return

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        term = self.entry.get().strip()
        if len(term) < self.min_chars:
            self.hide()
            return

        self.after_id = self.root.after(self.delay_ms, self._load_suggestions)

    def _load_suggestions(self):
        """Tải danh sách gợi ý mới nhất."""
        self.after_id = None
        term = self.entry.get().strip()
        if len(term) < self.min_chars:
            self.hide()
            return

        try:
            suggestions = self.fetch_callback(term) or []
        except Exception:
            suggestions = []

        normalized = []
        for item in suggestions[:self.max_items]:
            if isinstance(item, (tuple, list)) and len(item) >= 2:
                normalized.append((str(item[0]), str(item[1])))
            else:
                text = str(item)
                normalized.append((text, text))

        self.results = normalized
        if not self.results:
            self.hide()
            return

        self._show_popup()

    def _show_popup(self):
        """Hiển thị popup ngay bên dưới ô tìm kiếm."""
        if self.popup is None or not self.popup.winfo_exists():
            self.popup = Toplevel(self.root)
            self.popup.overrideredirect(True)
            self.popup.transient(self.root)
            self.popup.configure(bg="#D0D5DD")

            self.listbox = Listbox(
                self.popup,
                activestyle="none",
                bd=0,
                highlightthickness=0,
                relief=SOLID,
                selectmode="browse",
            )
            self.listbox.pack(fill="both", expand=True, padx=1, pady=1)
            self.listbox.bind("<ButtonRelease-1>", self._choose_from_list, add="+")
            self.listbox.bind("<Double-Button-1>", self._choose_from_list, add="+")
            self.listbox.bind("<Return>", self._choose_from_list, add="+")
            self.listbox.bind("<Escape>", self._on_escape, add="+")
            self.listbox.bind("<FocusOut>", self._on_focus_out, add="+")
            self.listbox.bind("<Up>", self._on_listbox_up, add="+")

        self.listbox.delete(0, END)
        for display_text, _ in self.results:
            self.listbox.insert(END, display_text)

        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height() + 1
        width = max(self.entry.winfo_width(), 220)
        height = max(28, min(len(self.results), self.max_items) * 24)
        self.popup.geometry(f"{width}x{height}+{x}+{y}")
        self.popup.deiconify()
        self.popup.lift()

    def _on_entry_down(self, event):
        """Chuyển focus xuống list gợi ý bằng phím xuống."""
        if not self.results or self.listbox is None or self.popup is None or not self.popup.winfo_exists():
            return None

        self.listbox.focus_set()
        self.listbox.selection_clear(0, END)
        self.listbox.selection_set(0)
        self.listbox.activate(0)
        return "break"

    def _on_entry_return(self, event):
        """Nếu đang mở gợi ý thì Enter chọn luôn kết quả đầu tiên."""
        if not self.results or self.listbox is None or self.popup is None or not self.popup.winfo_exists():
            return None

        current = self.listbox.curselection()
        if not current:
            current = (0,)
        self._apply_selection(current[0])
        return "break"

    def _choose_from_list(self, event=None):
        """Chọn gợi ý bằng chuột hoặc Enter trên listbox."""
        if self.listbox is None:
            return None

        current = self.listbox.curselection()
        if not current:
            current = (self.listbox.index("active"),)
        self._apply_selection(current[0])
        return "break"

    def _apply_selection(self, index):
        """Đổ giá trị được chọn vào Entry và gọi callback."""
        if index < 0 or index >= len(self.results):
            return

        _, value = self.results[index]
        self.entry.delete(0, END)
        self.entry.insert(0, value)
        self.entry.icursor(END)
        self.entry.focus_set()
        self.hide()

        if self.select_callback is not None:
            self.select_callback(value)

    def _on_listbox_up(self, event):
        """Quay lại ô Entry khi đang ở dòng đầu và bấm Up."""
        if self.listbox is None:
            return None

        current = self.listbox.curselection()
        if current and current[0] == 0:
            self.entry.focus_set()
            self.hide()
            return "break"
        return None

    def _on_escape(self, event=None):
        """Ẩn popup gợi ý."""
        self.hide()
        return "break"

    def _on_focus_out(self, event=None):
        """Đợi ngắn trước khi ẩn để không cắt mất click chọn."""
        self.root.after(120, self._hide_if_focus_elsewhere)

    def _hide_if_focus_elsewhere(self):
        """Giữ popup nếu focus đang ở entry hoặc list gợi ý."""
        focus_widget = self.root.focus_get()
        if focus_widget in (self.entry, self.listbox):
            return
        self.hide()

    def hide(self):
        """Ẩn popup hiện tại và hủy pending debounce."""
        self.results = []

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        if self.popup is not None and self.popup.winfo_exists():
            self.popup.withdraw()
