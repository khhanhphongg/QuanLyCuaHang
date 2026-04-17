"""Tự động co giãn các widget theo kích thước cửa sổ."""


class AutoScale:
    """Theo dõi resize và áp dụng tỉ lệ mới cho các widget dùng place()."""
    def __init__(self, root, base_width, base_height):
        self.root = root
        self.base_width = base_width
        self.base_height = base_height
        self.widgets = []
        self.ready = False
        self.destroyed = False
        self._init_after_id = None
        self._resize_after_id = None
        self._pending_size = None
        self._last_applied_size = None

        self.root.update_idletasks()
        self._collect_widgets(self.root)
        self.root.bind("<Configure>", self._on_resize)
        self.root.bind("<Destroy>", self._on_destroy, add="+")
        self._init_after_id = self.root.after(50, self._init_scale)

    def _init_scale(self):
        """Khởi động scale ban đầu sau khi cửa sổ ổn định."""
        self._init_after_id = None
        if self.destroyed or not self.root.winfo_exists():
            return
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        if width < 100 or height < 100:
            self._init_after_id = self.root.after(50, self._init_scale)
            return
        self.ready = True
        self._apply_scale(width, height)

    def _collect_widgets(self, widget):
        """Thu thập thông số place() ban đầu để dùng khi scale."""
        if widget.winfo_manager() == "place":
            info = widget.place_info()
            record = {
                "x": self._to_float(info.get("x")),
                "y": self._to_float(info.get("y")),
                "width": self._to_float(info.get("width")),
                "height": self._to_float(info.get("height")),
                "relx": info.get("relx", ""),
                "rely": info.get("rely", ""),
                "relwidth": info.get("relwidth", ""),
                "relheight": info.get("relheight", ""),
                "anchor": info.get("anchor", ""),
            }
            self.widgets.append((widget, record))

        for child in widget.winfo_children():
            self._collect_widgets(child)

    def _on_resize(self, event):
        """Lắng nghe resize và áp dụng tỉ lệ mới khi đã sẵn sàng."""
        if self.destroyed or not self.root.winfo_exists():
            return
        if event.widget != self.root:
            return

        if not self.ready:
            return

        if self.base_width == 0 or self.base_height == 0:
            return

        if event.width < 100 or event.height < 100:
            return

        self._pending_size = (event.width, event.height)
        if self._resize_after_id is not None:
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(16, self._flush_resize)

    def _flush_resize(self):
        """Gộp nhiều sự kiện resize liên tiếp để tránh lag khi nhập."""
        self._resize_after_id = None
        if self.destroyed or not self.root.winfo_exists():
            return
        if not self._pending_size:
            return

        width, height = self._pending_size
        self._pending_size = None
        self._apply_scale(width, height)

    def _apply_scale(self, width, height):
        """Tính tỉ lệ và cập nhật toạ độ/kích thước cho từng widget."""
        if self.destroyed or not self.root.winfo_exists():
            return
        if self._last_applied_size == (width, height):
            return
        self._last_applied_size = (width, height)

        scale_x = width / self.base_width
        scale_y = height / self.base_height

        for widget, record in self.widgets:
            if not widget.winfo_exists():
                continue

            place_args = {}
            if record["x"] is not None:
                place_args["x"] = int(record["x"] * scale_x)
            if record["y"] is not None:
                place_args["y"] = int(record["y"] * scale_y)
            if record["width"] is not None:
                place_args["width"] = int(record["width"] * scale_x)
            if record["height"] is not None:
                place_args["height"] = int(record["height"] * scale_y)

            # Giữ nguyên các thuộc tính tương đối nếu có.
            if record["relx"] != "":
                place_args["relx"] = record["relx"]
            if record["rely"] != "":
                place_args["rely"] = record["rely"]
            if record["relwidth"] != "":
                place_args["relwidth"] = record["relwidth"]
            if record["relheight"] != "":
                place_args["relheight"] = record["relheight"]
            if record["anchor"] != "":
                place_args["anchor"] = record["anchor"]

            if place_args:
                widget.place_configure(**place_args)

    def _on_destroy(self, event):
        """Hủy callback treo khi cửa sổ gốc bị đóng."""
        if event.widget != self.root or self.destroyed:
            return

        self.destroyed = True
        self._pending_size = None
        if self._init_after_id is not None:
            try:
                self.root.after_cancel(self._init_after_id)
            except Exception:
                pass
            self._init_after_id = None
        if self._resize_after_id is not None:
            try:
                self.root.after_cancel(self._resize_after_id)
            except Exception:
                pass
            self._resize_after_id = None

    def _to_float(self, value):
        """Chuyển chuỗi toạ độ từ place_info về số."""
        if value in (None, ""):
            return None
        try:
            return float(value)
        except Exception:
            return None
