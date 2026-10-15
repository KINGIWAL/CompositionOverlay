import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen, QPainterPath
from PyQt6.QtWidgets import QWidget


class CompositionRenderer(QWidget):
    """
    Renderer panduan komposisi.

    Untuk menambah pola sederhana, tambahkan satu entri ke COMPOSITIONS.
    Jenis yang tersedia: grid, cross, diagonals, golden_ratio, golden_triangle.
    """

    # Daftar pola terpusat. Pola grid baru hanya perlu mengubah divisions.
    # Jenis khusus (spiral dan triangle) tetap memakai fungsi gambar khusus.
    COMPOSITIONS = {
        "Rule of Thirds": {
            "type": "grid",
            "divisions": 3,
        },
        "Rule of Sixths": {
            "type": "grid",
            "divisions": 6,
        },
        "Golden Ratio": {
            "type": "golden_ratio",
        },
        "Golden Triangle": {
            "type": "golden_triangle",
        },
        "Center Cross": {
            "type": "cross",
        },
        "Diagonal Grid": {
            "type": "diagonals",
        },
        "Fibonacci Grid": {
            "type": "fibonacci_grid",
        },
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.composition = "Rule of Thirds"
        self.line_color = QColor("white")
        self.line_width = 2
        self.line_opacity = 180
        self.rotation_angle = 0
        self.golden_ratio_mode = "grid"
        self.golden_triangle_mode = "tl_br"

        self.flip_horizontal = False
        self.flip_vertical = False
        
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    @classmethod
    def composition_type(cls, name):
        """Mengembalikan jenis pola untuk dipakai antarmuka."""
        config = cls.COMPOSITIONS.get(name, {})
        return config.get("type", "grid")

    def set_composition(self, composition):
        if composition in self.COMPOSITIONS:
            self.composition = composition
        else:
            self.composition = "Rule of Thirds"
        self.update()

    def set_line_color(self, color):
        self.line_color = QColor(color)
        self.update()

    def set_line_width(self, width):
        self.line_width = max(1, int(width))
        self.update()

    def set_line_opacity(self, opacity):
        self.line_opacity = max(0, min(255, int(opacity)))
        self.update()

    def set_rotation(self, angle):
        """Memutar semua panduan komposisi berdasarkan derajat."""
        self.rotation_angle = int(angle) % 360
        self.update()

    def set_golden_ratio_mode(self, mode):
        mode = str(mode).lower().strip()
        if mode in ("grid", "spiral"):
            self.golden_ratio_mode = mode
            self.update()

    def set_golden_triangle_mode(self, mode):
        aliases = {
            "diagonal_1": "tl_br",
            "diagonal_2": "tr_bl",
            "reverse_1": "bl_tr",
            "reverse_2": "br_tl",
        }
        mode = aliases.get(str(mode).lower().strip(), str(mode).lower().strip())
        if mode in ("tl_br", "tr_bl", "bl_tr", "br_tl"):
            self.golden_triangle_mode = mode
            self.update()

    def paintEvent(self, event):
        width, height = self.width(), self.height()
        if width <= 1 or height <= 1:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        color = QColor(self.line_color)
        color.setAlpha(self.line_opacity)
        pen = QPen(color)
        pen.setWidthF(float(self.line_width))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        # Rotasi diterapkan pada seluruh pola agar berlaku untuk semua jenis.
        if (
            self.rotation_angle % 360
            or self.flip_horizontal
            or self.flip_vertical
        ):
            painter.translate(width / 2.0, height / 2.0)

            painter.rotate(self.rotation_angle)

            scale_x = -1 if self.flip_horizontal else 1
            scale_y = -1 if self.flip_vertical else 1
            painter.scale(scale_x, scale_y)

            painter.translate(-width / 2.0, -height / 2.0)


        margin = max(1.0, self.line_width / 2.0)
        left, top = margin, margin
        right = max(left + 1, width - margin)
        bottom = max(top + 1, height - margin)
        rect_width, rect_height = right - left, bottom - top

        config = self.COMPOSITIONS.get(
            self.composition, self.COMPOSITIONS["Rule of Thirds"]
        )
        kind = config["type"]

        if kind == "grid":
            self._draw_grid(
                painter, left, top, right, bottom,
                int(config.get("divisions", 3))
            )
        elif kind == "cross":
            self._draw_center_cross(painter, left, top, right, bottom)
        elif kind == "diagonals":
            self._draw_diagonals(painter, left, top, right, bottom)
        elif kind == "golden_ratio":
            if self.golden_ratio_mode == "spiral":
                self._draw_golden_spiral(
                    painter, left, top, rect_width, rect_height
                )
            else:
                self._draw_golden_ratio_grid(
                    painter, left, top, right, bottom
                )
        elif kind == "golden_triangle":
            self._draw_golden_triangle(painter, left, top, right, bottom)
        elif kind == "fibonacci_grid":
            self._draw_fibonacci_grid(
                painter, left, top, right, bottom
                )

        painter.end()

    def _draw_grid(self, painter, left, top, right, bottom, divisions=3):
        """Grid umum. Contoh: divisions=3 menghasilkan Rule of Thirds."""
        divisions = max(2, min(20, int(divisions)))
        width, height = right - left, bottom - top
        for i in range(1, divisions):
            x = left + width * i / divisions
            y = top + height * i / divisions
            painter.drawLine(QPointF(x, top), QPointF(x, bottom))
            painter.drawLine(QPointF(left, y), QPointF(right, y))

    def _draw_center_cross(self, painter, left, top, right, bottom):
        center_x = (left + right) / 2.0
        center_y = (top + bottom) / 2.0
        painter.drawLine(QPointF(center_x, top), QPointF(center_x, bottom))
        painter.drawLine(QPointF(left, center_y), QPointF(right, center_y))

    def _draw_diagonals(self, painter, left, top, right, bottom):
        painter.drawLine(QPointF(left, top), QPointF(right, bottom))
        painter.drawLine(QPointF(right, top), QPointF(left, bottom))

    def _draw_golden_ratio_grid(self, painter, left, top, right, bottom):
        width, height = right - left, bottom - top
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        small_ratio = 1.0 / (phi * phi)
        large_ratio = 1.0 / phi
        for ratio in (small_ratio, large_ratio):
            x = left + width * ratio
            y = top + height * ratio
            painter.drawLine(QPointF(x, top), QPointF(x, bottom))
            painter.drawLine(QPointF(left, y), QPointF(right, y))

    def _draw_golden_spiral(self, painter, left, top, width, height):
        if width <= 2 or height <= 2:
            return

        phi = (1.0 + math.sqrt(5.0)) / 2.0
        growth = math.log(phi) / (math.pi / 2.0)
        theta_start, theta_end, steps = -4.0 * math.pi, 2.0 * math.pi, 700
        raw_points = []

        for i in range(steps + 1):
            theta = theta_start + (theta_end - theta_start) * i / steps
            radius = math.exp(growth * theta)
            raw_points.append((radius * math.cos(theta), radius * math.sin(theta)))

        min_x = min(point[0] for point in raw_points)
        max_x = max(point[0] for point in raw_points)
        min_y = min(point[1] for point in raw_points)
        max_y = max(point[1] for point in raw_points)
        span_x = max(max_x - min_x, 1e-9)
        span_y = max(max_y - min_y, 1e-9)

        padding = max(4.0, float(self.line_width) * 2.0)
        usable_width = max(1.0, width - padding * 2.0)
        usable_height = max(1.0, height - padding * 2.0)
        scale = min(usable_width / span_x, usable_height / span_y)
        drawn_width, drawn_height = span_x * scale, span_y * scale
        offset_x = left + (width - drawn_width) / 2.0
        offset_y = top + (height - drawn_height) / 2.0

        path = QPainterPath()
        for i, (x, y) in enumerate(raw_points):
            point = QPointF(
                offset_x + (x - min_x) * scale,
                offset_y + (y - min_y) * scale,
            )
            if i == 0:
                path.moveTo(point)
            else:
                path.lineTo(point)
        painter.drawPath(path)

    def _draw_golden_triangle(self, painter, left, top, right, bottom):
        corners = {
            "tl": QPointF(left, top),
            "tr": QPointF(right, top),
            "bl": QPointF(left, bottom),
            "br": QPointF(right, bottom),
        }
        # Mode menentukan diagonal utama dan sudut pendamping.
        variants = {
            "tl_br": ("tl", "br", "tr"),
            "br_tl": ("tl", "br", "bl"),
            "tr_bl": ("tr", "bl", "tl"),
            "bl_tr": ("tr", "bl", "br"),
        }
        start_key, end_key, corner_key = variants.get(
            self.golden_triangle_mode, ("tl", "br", "tr")
        )
        start, end, corner = (
            corners[start_key], corners[end_key], corners[corner_key]
        )
        painter.drawLine(start, end)

        dx, dy = end.x() - start.x(), end.y() - start.y()
        length_squared = dx * dx + dy * dy
        if length_squared <= 0:
            return

        t = (
            (corner.x() - start.x()) * dx
            + (corner.y() - start.y()) * dy
        ) / length_squared
        t = max(0.0, min(1.0, t))
        projection = QPointF(
            start.x() + t * dx,
            start.y() + t * dy,
        )
        painter.drawLine(corner, projection)

    def _draw_fibonacci_grid(self, painter, left, top, right, bottom):
        """Membuat pembagian persegi panjang bertahap seperti referensi."""
        width = right - left
        height = bottom - top

        if width <= 1 or height <= 1:
            return

        # Pembagian utama.
        split_x = left + width * 0.382
        split_y = top + height * 0.5

        painter.drawLine(
            QPointF(split_x, top),
            QPointF(split_x, bottom)
        )
        painter.drawLine(
            QPointF(left, split_y),
            QPointF(right, split_y)
        )

        # Pembagian bertingkat di area kiri atas.
        x1 = left + (split_x - left) * 0.5
        y1 = top + (split_y - top) * 0.5

        painter.drawLine(
            QPointF(x1, top),
            QPointF(x1, split_y)
        )
        painter.drawLine(
            QPointF(left, y1),
            QPointF(split_x, y1)
        )

        # Pembagian kecil tambahan di dekat pertemuan garis.
        small_w = split_x - x1
        small_h = split_y - y1

        x2 = x1 + small_w * 0.5
        y2 = y1 + small_h * 0.5

        painter.drawLine(
            QPointF(x2, y1),
            QPointF(x2, split_y)
        )
        painter.drawLine(
            QPointF(x1, y2),
            QPointF(split_x, y2)
        )
    def set_flip_horizontal(self, enabled):
        self.flip_horizontal = bool(enabled)
        self.update()
    
    def set_flip_vertical(self, enabled):
        self.flip_vertical = bool(enabled)
        self.update()