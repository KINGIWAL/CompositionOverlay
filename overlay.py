
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QSizeGrip

from composition import CompositionRenderer


class OverlayWindow(QWidget):
    # Mengirim perubahan posisi dan ukuran ke panel utama
    geometryChanged = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Composition Overlay")

        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            True
        )

        # Ukuran awal: Landscape
        self.orientation = "Landscape"
        self.setMinimumSize(426, 240)
        self.setGeometry(100, 100, 800, 450)

        self._drag_position = None
        self._locked = False

        # Renderer untuk menggambar garis komposisi
        self.renderer = CompositionRenderer(self)

        # Sudut untuk mengubah ukuran overlay
        self.grip = QSizeGrip(self)
        self.grip.setToolTip(
            "Tarik untuk mengubah ukuran overlay"
        )

        self.update_children_geometry()

    def update_children_geometry(self):
        # Renderer mengikuti ukuran overlay
        self.renderer.setGeometry(self.rect())

        # Posisikan grip di sudut kanan bawah
        self.grip.move(
            self.width() - self.grip.width(),
            self.height() - self.grip.height()
        )

        self.grip.raise_()

    def resizeEvent(self, event):
        self.update_children_geometry()
        super().resizeEvent(event)
        self.emit_geometry()

    def moveEvent(self, event):
        super().moveEvent(event)
        self.emit_geometry()

    def emit_geometry(self):
        self.geometryChanged.emit(
            self.x(),
            self.y(),
            self.width(),
            self.height()
        )

    def set_position(self, x, y):
        self.move(int(x), int(y))

    def set_overlay_size(self, width, height):
        self.resize(int(width), int(height))

    def set_locked(self, locked):
        self._locked = bool(locked)
        self._drag_position = None

        # Saat terkunci, sudut pengubah ukuran disembunyikan
        self.grip.setVisible(not self._locked)

        self.setToolTip(
            "Overlay terkunci"
            if self._locked
            else "Overlay dapat dipindahkan"
        )

    def is_locked(self):
        return self._locked

    def mousePressEvent(self, event):
        if (
            not self._locked
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            not self._locked
            and self._drag_position is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self._drag_position
            )
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_position = None
        super().mouseReleaseEvent(event)

    def set_flip_horizontal(self, enabled):
        self.renderer.set_flip_horizontal(enabled)

    def set_flip_vertical(self, enabled):
        self.renderer.set_flip_vertical(enabled)

    def set_orientation(self, orientation):
        """Mengubah orientasi overlay menjadi Landscape atau Portrait."""
        if orientation not in ("Landscape", "Portrait"):
            return

        self.orientation = orientation

        if orientation == "Portrait":
            # Rasio 9:16
            self.setMinimumSize(240, 426)
            self.resize(450, 800)
        else:
            # Rasio 16:9
            self.setMinimumSize(426, 240)
            self.resize(800, 450)

        self.update_children_geometry()
        self.emit_geometry()
