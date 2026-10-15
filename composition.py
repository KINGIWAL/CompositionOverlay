
import math

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen, QPainterPath
from PyQt6.QtWidgets import QWidget


class CompositionRenderer(QWidget):
    """
    Menggambar panduan komposisi transparan.

    Komposisi yang didukung:
    - Rule of Thirds
    - Golden Ratio (grid atau spiral)
    - Golden Triangle (4 arah diagonal)
    - Center Cross
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.composition = "Rule of Thirds"

        self.line_color = QColor("white")
        self.line_width = 2
        self.line_opacity = 180

        # Mode Golden Ratio: "grid" atau "spiral"
        self.golden_ratio_mode = "grid"

        # Mode Golden Triangle:
        # "tl_br", "tr_bl", "bl_tr", "br_tl"
        self.golden_triangle_mode = "tl_br"

        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground, True
        )

    # ---------------------------------------------------------
    # Pengaturan komposisi
    # ---------------------------------------------------------

    def set_composition(self, composition):
        self.composition = composition
        self.update()

    def set_line_color(self, color):
        if isinstance(color, QColor):
            self.line_color = QColor(color)
        else:
            self.line_color = QColor(color)
        self.update()

    def set_line_width(self, width):
        self.line_width = max(1, int(width))
        self.update()

    def set_line_opacity(self, opacity):
        self.line_opacity = max(0, min(255, int(opacity)))
        self.update()

    def set_golden_ratio_mode(self, mode):
        """
        mode: 'grid' atau 'spiral'
        """
        mode = str(mode).lower().strip()

        if mode in ("grid", "spiral"):
            self.golden_ratio_mode = mode
            self.update()

    def set_golden_triangle_mode(self, mode):
        """
        Pilihan:
        tl_br = diagonal kiri atas ke kanan bawah
        tr_bl = diagonal kanan atas ke kiri bawah
        bl_tr = kebalikan orientasi diagonal kiri atas ke kanan bawah
        br_tl = kebalikan orientasi diagonal kanan atas ke kiri bawah

        Alias yang diterima:
        'diagonal_1', 'diagonal_2', 'reverse_1', 'reverse_2'
        """
        aliases = {
            "diagonal_1": "tl_br",
            "diagonal_2": "tr_bl",
            "reverse_1": "bl_tr",
            "reverse_2": "br_tl",
        }

        mode = str(mode).lower().strip()
        mode = aliases.get(mode, mode)

        valid_modes = ("tl_br", "tr_bl", "bl_tr", "br_tl")

        if mode in valid_modes:
            self.golden_triangle_mode = mode
            self.update()

    # ---------------------------------------------------------
    # Proses menggambar
    # ---------------------------------------------------------

    def paintEvent(self, event):
        width = self.width()
        height = self.height()

        if width <= 1 or height <= 1:
            return

        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing, True
        )

        color = QColor(self.line_color)
        color.setAlpha(self.line_opacity)

        pen = QPen(color)
        pen.setWidthF(float(self.line_width))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        painter.setPen(pen)

        # Sedikit inset agar garis tepi tidak terpotong.
        margin = max(1.0, self.line_width / 2.0)
        left = margin
        top = margin
        right = max(left + 1, width - margin)
        bottom = max(top + 1, height - margin)

        rect_width = right - left
        rect_height = bottom - top

        composition = str(self.composition).strip().lower()

        if composition in ("rule of thirds", "rule of thirds grid"):
            self._draw_rule_of_thirds(
                painter, left, top, right, bottom
            )

        elif composition in (
            "golden ratio",
            "golden ratio grid",
            "golden spiral",
        ):
            if composition == "golden spiral":
                self.golden_ratio_mode = "spiral"

            if self.golden_ratio_mode == "spiral":
                self._draw_golden_spiral(
                    painter, left, top, rect_width, rect_height
                )
            else:
                self._draw_golden_ratio_grid(
                    painter, left, top, right, bottom
                )

        elif composition in (
            "golden triangle",
            "golden triangles",
        ):
            self._draw_golden_triangle(
                painter, left, top, right, bottom
            )

        elif composition in ("center cross", "center"):
            self._draw_center_cross(
                painter, left, top, right, bottom
            )

        painter.end()

    # ---------------------------------------------------------
    # Rule of Thirds
    # ---------------------------------------------------------

    def _draw_rule_of_thirds(
        self, painter, left, top, right, bottom
    ):
        width = right - left
        height = bottom - top

        x1 = left + width / 3.0
        x2 = left + width * 2.0 / 3.0

        y1 = top + height / 3.0
        y2 = top + height * 2.0 / 3.0

        painter.drawLine(
            QPointF(x1, top), QPointF(x1, bottom)
        )
        painter.drawLine(
            QPointF(x2, top), QPointF(x2, bottom)
        )
        painter.drawLine(
            QPointF(left, y1), QPointF(right, y1)
        )
        painter.drawLine(
            QPointF(left, y2), QPointF(right, y2)
        )

    # ---------------------------------------------------------
    # Golden Ratio Grid
    # ---------------------------------------------------------

    def _draw_golden_ratio_grid(
        self, painter, left, top, right, bottom
    ):
        """
        Grid rasio emas.

        Garis berada pada sekitar 0.382 dan 0.618 dari bidang.
        Kedua sisi membentuk pembagian yang tidak sama besar.
        """
        width = right - left
        height = bottom - top

        phi = (1.0 + math.sqrt(5.0)) / 2.0
        small_ratio = 1.0 / (phi * phi)  # sekitar 0.382
        large_ratio = 1.0 / phi          # sekitar 0.618

        x1 = left + width * small_ratio
        x2 = left + width * large_ratio

        y1 = top + height * small_ratio
        y2 = top + height * large_ratio

        painter.drawLine(
            QPointF(x1, top), QPointF(x1, bottom)
        )
        painter.drawLine(
            QPointF(x2, top), QPointF(x2, bottom)
        )
        painter.drawLine(
            QPointF(left, y1), QPointF(right, y1)
        )
        painter.drawLine(
            QPointF(left, y2), QPointF(right, y2)
        )

    # ---------------------------------------------------------
    # Golden Spiral
    # ---------------------------------------------------------

    def _draw_golden_spiral(
        self, painter, left, top, width, height
    ):
        """
        Menggambar spiral logaritmik emas.

        Radius bertambah dengan faktor rasio emas setiap 90 derajat.
        Spiral dipusatkan dan diskalakan agar tetap berada di overlay.
        """
        if width <= 2 or height <= 2:
            return

        phi = (1.0 + math.sqrt(5.0)) / 2.0
        growth = math.log(phi) / (math.pi / 2.0)

        # Buat spiral cukup panjang agar tampak jelas.
        theta_start = -4.0 * math.pi
        theta_end = 2.0 * math.pi
        steps = 700

        raw_points = []

        for i in range(steps + 1):
            theta = theta_start + (
                (theta_end - theta_start) * i / steps
            )

            radius = math.exp(growth * theta)
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)

            raw_points.append((x, y))

        # Normalisasi terhadap kotak pembatas supaya spiral
        # menyesuaikan bentuk overlay tanpa terpotong.
        min_x = min(p[0] for p in raw_points)
        max_x = max(p[0] for p in raw_points)
        min_y = min(p[1] for p in raw_points)
        max_y = max(p[1] for p in raw_points)

        span_x = max(max_x - min_x, 1e-9)
        span_y = max(max_y - min_y, 1e-9)

        padding = max(4.0, float(self.line_width) * 2.0)
        usable_width = max(1.0, width - padding * 2.0)
        usable_height = max(1.0, height - padding * 2.0)

        scale = min(
            usable_width / span_x,
            usable_height / span_y,
        )

        drawn_width = span_x * scale
        drawn_height = span_y * scale

        offset_x = left + (width - drawn_width) / 2.0
        offset_y = top + (height - drawn_height) / 2.0

        path = QPainterPath()

        for i, (x, y) in enumerate(raw_points):
            px = offset_x + (x - min_x) * scale
            py = offset_y + (y - min_y) * scale

            point = QPointF(px, py)

            if i == 0:
                path.moveTo(point)
            else:
                path.lineTo(point)

        painter.drawPath(path)

    # ---------------------------------------------------------
    # Golden Triangle
    # ---------------------------------------------------------

    def _draw_golden_triangle(
        self, painter, left, top, right, bottom
    ):
        """
        Menggambar panduan diagonal fotografi.

        Diagonal utama dipilih berdasarkan mode. Garis pendamping
        ditarik tegak lurus dari dua sudut lainnya menuju diagonal.
        """
        corners = {
            "tl": QPointF(left, top),
            "tr": QPointF(right, top),
            "bl": QPointF(left, bottom),
            "br": QPointF(right, bottom),
        }

        diagonal_pairs = {
            "tl_br": ("tl", "br"),
            "tr_bl": ("tr", "bl"),
            "bl_tr": ("bl", "tr"),
            "br_tl": ("br", "tl"),
        }

        start_key, end_key = diagonal_pairs.get(
            self.golden_triangle_mode, ("tl", "br")
        )

        start = corners[start_key]
        end = corners[end_key]

        # Diagonal utama.
        painter.drawLine(start, end)

        # Proyeksikan dua sudut lain ke diagonal utama.
        other_keys = [
            key for key in ("tl", "tr", "bl", "br")
            if key not in (start_key, end_key)
        ]

        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length_squared = dx * dx + dy * dy

        if length_squared <= 0:
            return

        for key in other_keys:
            corner = corners[key]

            # t adalah posisi proyeksi pada garis diagonal.
            t = (
                (corner.x() - start.x()) * dx
                + (corner.y() - start.y()) * dy
            ) / length_squared

            # Batasi proyeksi pada segmen diagonal.
            t = max(0.0, min(1.0, t))

            projection = QPointF(
                start.x() + t * dx,
                start.y() + t * dy,
            )

            painter.drawLine(corner, projection)

    # ---------------------------------------------------------
    # Center Cross
    # ---------------------------------------------------------

    def _draw_center_cross(
        self, painter, left, top, right, bottom
    ):
        center_x = (left + right) / 2.0
        center_y = (top + bottom) / 2.0

        painter.drawLine(
            QPointF(center_x, top),
            QPointF(center_x, bottom),
        )
        painter.drawLine(
            QPointF(left, center_y),
            QPointF(right, center_y),
        )



    def _draw_golden_triangle(
        self, painter, left, top, right, bottom
    ):
        corners = {
            "tl": QPointF(left, top),
            "tr": QPointF(right, top),
            "bl": QPointF(left, bottom),
            "br": QPointF(right, bottom),
        }

        # Setiap mode menentukan diagonal utama dan sudut
        # yang dihubungkan ke diagonal dengan garis tegak lurus.
        variants = {
            "tl_br": ("tl", "br", "tr"),
            "br_tl": ("tl", "br", "bl"),
            "tr_bl": ("tr", "bl", "tl"),
            "bl_tr": ("tr", "bl", "br"),
        }

        start_key, end_key, corner_key = variants.get(
            self.golden_triangle_mode, ("tl", "br", "tr")
        )

        start = corners[start_key]
        end = corners[end_key]
        corner = corners[corner_key]

        # Diagonal utama.
        painter.drawLine(start, end)

        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length_squared = dx * dx + dy * dy

        if length_squared <= 0:
            return

        # Proyeksi sudut ke diagonal untuk menghasilkan
        # garis pendamping yang tegak lurus.
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
