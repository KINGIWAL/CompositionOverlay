import sys

from PyQt6.QtCore import Qt, QSignalBlocker
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QSlider,
    QColorDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QMessageBox,
)

from overlay import OverlayWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Composition Overlay")
        self.setMinimumWidth(390)

        self.setStyleSheet("""
            QWidget {
                background-color: #202124;
                color: #eeeeee;
                font-size: 10pt;
            }
            QGroupBox {
                border: 1px solid #45474b;
                border-radius: 7px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton, QComboBox, QSpinBox {
                background-color: #303134;
                border: 1px solid #55575b;
                border-radius: 5px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #414348;
            }
            QPushButton:checked {
                background-color: #526b8d;
                border: 1px solid #8db9f0;
                color: white;
            }
            QPushButton:checked:hover {
                background-color: #607da3;
            }
            QComboBox QAbstractItemView {
                background-color: #303134;
                selection-background-color: #50545b;
            }
            QSlider::groove:horizontal {
                height: 5px;
                background: #505258;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #dddddd;
                width: 13px;
                margin: -5px 0;
                border-radius: 6px;
            }
        """)

        self.overlay = OverlayWindow()

        # Urutan penting: buat UI dahulu, baru hubungkan sinyal.
        self._build_ui()
        self._connect_signals()
        self._sync_initial_state()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(10)

        title = QLabel("COMPOSITION OVERLAY")
        title.setStyleSheet("font-size: 15pt; font-weight: bold; padding: 5px;")
        root.addWidget(title)

        # -----------------------------------------------------
        # Komposisi
        # -----------------------------------------------------
        composition_group = QGroupBox("Komposisi")
        composition_layout = QVBoxLayout(composition_group)
        composition_layout.setSpacing(10)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Jenis komposisi:"))

        self.composition_combo = QComboBox()
        self.composition_combo.addItems([
            "Rule of Thirds",
            "Golden Ratio",
            "Golden Triangle",
            "Center Cross",
        ])
        type_row.addWidget(self.composition_combo, 1)
        composition_layout.addLayout(type_row)

        # Panel Golden Ratio
        self.ratio_panel = QWidget()
        ratio_layout = QVBoxLayout(self.ratio_panel)
        ratio_layout.setContentsMargins(0, 0, 0, 0)
        ratio_layout.setSpacing(6)

        ratio_title = QLabel("Mode Golden Ratio:")
        ratio_title.setStyleSheet("font-weight: bold;")
        ratio_layout.addWidget(ratio_title)

        ratio_buttons = QHBoxLayout()
        self.ratio_grid_button = QPushButton("Grid Rasio Emas")
        self.ratio_spiral_button = QPushButton("Spiral Emas")
        self.ratio_grid_button.setCheckable(True)
        self.ratio_spiral_button.setCheckable(True)
        ratio_buttons.addWidget(self.ratio_grid_button)
        ratio_buttons.addWidget(self.ratio_spiral_button)
        ratio_layout.addLayout(ratio_buttons)

        self.ratio_description = QLabel(
            "Grid dengan garis pembagian berdasarkan rasio emas."
        )
        self.ratio_description.setWordWrap(True)
        self.ratio_description.setStyleSheet("color: #aaaaaa; font-size: 9pt;")
        ratio_layout.addWidget(self.ratio_description)
        composition_layout.addWidget(self.ratio_panel)

        # Panel Golden Triangle
        self.triangle_panel = QWidget()
        triangle_layout = QVBoxLayout(self.triangle_panel)
        triangle_layout.setContentsMargins(0, 0, 0, 0)
        triangle_layout.setSpacing(6)

        triangle_title = QLabel("Mode Golden Triangle:")
        triangle_title.setStyleSheet("font-weight: bold;")
        triangle_layout.addWidget(triangle_title)

        triangle_buttons_layout = QHBoxLayout()
        self.triangle_tl_br_button = QPushButton("↘")
        self.triangle_br_tl_button = QPushButton("↖")
        self.triangle_tr_bl_button = QPushButton("↙")
        self.triangle_bl_tr_button = QPushButton("↗")

        self.triangle_buttons = [
            self.triangle_tl_br_button,
            self.triangle_br_tl_button,
            self.triangle_tr_bl_button,
            self.triangle_bl_tr_button,
        ]

        tooltips = [
            "Diagonal dari kiri atas ke kanan bawah",
            "Arah diagonal kebalikan pertama",
            "Diagonal dari kanan atas ke kiri bawah",
            "Arah diagonal kebalikan ketiga",
        ]
        for button, tooltip in zip(self.triangle_buttons, tooltips):
            button.setCheckable(True)
            button.setMinimumHeight(38)
            button.setToolTip(tooltip)
            triangle_buttons_layout.addWidget(button)

        triangle_layout.addLayout(triangle_buttons_layout)

        self.triangle_description = QLabel(
            "Pilih arah diagonal panduan komposisi."
        )
        self.triangle_description.setWordWrap(True)
        self.triangle_description.setStyleSheet("color: #aaaaaa; font-size: 9pt;")
        triangle_layout.addWidget(self.triangle_description)
        composition_layout.addWidget(self.triangle_panel)

        root.addWidget(composition_group)

        # -----------------------------------------------------
        # Posisi dan ukuran
        # -----------------------------------------------------
        geometry_group = QGroupBox("Posisi dan Ukuran Overlay")
        geometry_layout = QFormLayout(geometry_group)

        self.x_spin = QSpinBox()
        self.x_spin.setRange(-10000, 10000)

        self.y_spin = QSpinBox()
        self.y_spin.setRange(-10000, 10000)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 10000)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 10000)

        geometry_layout.addRow("Posisi X:", self.x_spin)
        geometry_layout.addRow("Posisi Y:", self.y_spin)
        geometry_layout.addRow("Lebar:", self.width_spin)
        geometry_layout.addRow("Tinggi:", self.height_spin)
        root.addWidget(geometry_group)

        # -----------------------------------------------------
        # Pengaturan garis
        # -----------------------------------------------------
        style_group = QGroupBox("Pengaturan Garis")
        style_layout = QFormLayout(style_group)

        self.thickness_spin = QSpinBox()
        self.thickness_spin.setRange(1, 20)
        self.thickness_spin.setValue(2)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(180)

        self.opacity_label = QLabel("180 / 255")
        opacity_row = QHBoxLayout()
        opacity_row.addWidget(self.opacity_slider, 1)
        opacity_row.addWidget(self.opacity_label)

        self.color_button = QPushButton("Pilih Warna Garis")
        self.color_preview = QLabel("WHITE")
        self.color_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.color_preview.setMinimumHeight(28)
        self.color_preview.setStyleSheet(
            "background-color: white; color: black; "
            "border-radius: 4px; padding: 4px;"
        )

        style_layout.addRow("Ketebalan:", self.thickness_spin)
        style_layout.addRow("Opacity:", opacity_row)
        style_layout.addRow("Warna:", self.color_button)
        style_layout.addRow("Pratinjau warna:", self.color_preview)
        root.addWidget(style_group)

        # -----------------------------------------------------
        # Kontrol overlay
        # -----------------------------------------------------
        controls_group = QGroupBox("Kontrol Overlay")
        controls_layout = QVBoxLayout(controls_group)

        geometry_buttons = QHBoxLayout()
        self.reset_button = QPushButton("Reset Posisi/Ukuran")
        self.lock_button = QPushButton("Lock Overlay")
        geometry_buttons.addWidget(self.reset_button)
        geometry_buttons.addWidget(self.lock_button)

        visibility_buttons = QHBoxLayout()
        self.show_button = QPushButton("Tampilkan Overlay")
        self.hide_button = QPushButton("Sembunyikan Overlay")
        visibility_buttons.addWidget(self.show_button)
        visibility_buttons.addWidget(self.hide_button)

        controls_layout.addLayout(geometry_buttons)
        controls_layout.addLayout(visibility_buttons)
        root.addWidget(controls_group)

        note = QLabel("Overlay transparan dan selalu di atas jendela lain.")
        note.setWordWrap(True)
        note.setStyleSheet("color: #aaaaaa; padding: 4px;")
        root.addWidget(note)

    def _connect_signals(self):
        self.composition_combo.currentTextChanged.connect(self.change_composition)

        self.ratio_grid_button.clicked.connect(
            lambda: self.select_ratio_mode("grid")
        )
        self.ratio_spiral_button.clicked.connect(
            lambda: self.select_ratio_mode("spiral")
        )

        self.triangle_tl_br_button.clicked.connect(
            lambda: self.select_triangle_mode("tl_br")
        )
        self.triangle_br_tl_button.clicked.connect(
            lambda: self.select_triangle_mode("br_tl")
        )
        self.triangle_tr_bl_button.clicked.connect(
            lambda: self.select_triangle_mode("tr_bl")
        )
        self.triangle_bl_tr_button.clicked.connect(
            lambda: self.select_triangle_mode("bl_tr")
        )

        self.x_spin.valueChanged.connect(self.change_position)
        self.y_spin.valueChanged.connect(self.change_position)
        self.width_spin.valueChanged.connect(self.change_size)
        self.height_spin.valueChanged.connect(self.change_size)

        self.thickness_spin.valueChanged.connect(self.change_thickness)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        self.color_button.clicked.connect(self.choose_color)

        self.lock_button.clicked.connect(self.toggle_lock)
        self.reset_button.clicked.connect(self.reset_geometry)
        self.show_button.clicked.connect(self.show_overlay)
        self.hide_button.clicked.connect(self.hide_overlay)

        self.overlay.geometryChanged.connect(self.sync_geometry)

    def _sync_initial_state(self):
        renderer = self.overlay.renderer
        renderer.set_composition(self.composition_combo.currentText())
        renderer.set_line_width(self.thickness_spin.value())
        renderer.set_line_opacity(self.opacity_slider.value())

        self.select_ratio_mode("grid")
        self.select_triangle_mode("tl_br")

        self.sync_geometry(
            self.overlay.x(),
            self.overlay.y(),
            self.overlay.width(),
            self.overlay.height(),
        )
        self.update_composition_panels()

        # Sinkronkan status lock jika overlay sudah memiliki status awal.
        locked = self.overlay.is_locked()
        self.lock_button.setText("Unlock Overlay" if locked else "Lock Overlay")
        for control in (
            self.x_spin, self.y_spin, self.width_spin, self.height_spin
        ):
            control.setEnabled(not locked)

    # ---------------------------------------------------------
    # Komposisi
    # ---------------------------------------------------------
    def change_composition(self, composition):
        self.overlay.renderer.set_composition(composition)
        self.update_composition_panels()

    def update_composition_panels(self):
        composition = self.composition_combo.currentText()
        self.ratio_panel.setVisible(composition == "Golden Ratio")
        self.triangle_panel.setVisible(composition == "Golden Triangle")

    def select_ratio_mode(self, mode):
        self.overlay.renderer.set_golden_ratio_mode(mode)
        self.ratio_grid_button.setChecked(mode == "grid")
        self.ratio_spiral_button.setChecked(mode == "spiral")

        if mode == "grid":
            self.ratio_description.setText(
                "Grid dengan garis pembagian berdasarkan rasio emas."
            )
        else:
            self.ratio_description.setText(
                "Spiral emas sebagai panduan menuju titik fokus."
            )

    def select_triangle_mode(self, mode):
        self.overlay.renderer.set_golden_triangle_mode(mode)

        modes = ["tl_br", "br_tl", "tr_bl", "bl_tr"]
        descriptions = [
            "Diagonal dari kiri atas ke kanan bawah.",
            "Arah diagonal kebalikan dari mode pertama.",
            "Diagonal dari kanan atas ke kiri bawah.",
            "Arah diagonal kebalikan dari mode ketiga.",
        ]

        for button, button_mode in zip(self.triangle_buttons, modes):
            button.setChecked(button_mode == mode)

        if mode in modes:
            self.triangle_description.setText(descriptions[modes.index(mode)])

    # ---------------------------------------------------------
    # Posisi dan ukuran
    # ---------------------------------------------------------
    def change_position(self, *_):
        if self.overlay.is_locked():
            return
        self.overlay.set_position(self.x_spin.value(), self.y_spin.value())

    def change_size(self, *_):
        if self.overlay.is_locked():
            return
        self.overlay.set_overlay_size(
            self.width_spin.value(), self.height_spin.value()
        )

    def sync_geometry(self, x, y, width, height):
        blockers = [
            QSignalBlocker(self.x_spin),
            QSignalBlocker(self.y_spin),
            QSignalBlocker(self.width_spin),
            QSignalBlocker(self.height_spin),
        ]
        self.x_spin.setValue(x)
        self.y_spin.setValue(y)
        self.width_spin.setValue(width)
        self.height_spin.setValue(height)
        del blockers

    # ---------------------------------------------------------
    # Pengaturan garis
    # ---------------------------------------------------------
    def change_thickness(self, value):
        self.overlay.renderer.set_line_width(value)

    def change_opacity(self, value):
        self.overlay.renderer.set_line_opacity(value)
        self.opacity_label.setText(f"{value} / 255")

    def choose_color(self):
        current_color = self.overlay.renderer.line_color
        color = QColorDialog.getColor(
            current_color, self, "Pilih Warna Garis"
        )
        if not color.isValid():
            return

        self.overlay.renderer.set_line_color(color)
        self.color_preview.setText(color.name().upper())
        text_color = "black" if color.lightness() > 128 else "white"
        self.color_preview.setStyleSheet(
            f"background-color: {color.name()}; color: {text_color}; "
            "border-radius: 4px; padding: 4px;"
        )

    # ---------------------------------------------------------
    # Lock dan reset
    # ---------------------------------------------------------
    def toggle_lock(self):
        locked = not self.overlay.is_locked()
        self.overlay.set_locked(locked)
        self.lock_button.setText("Unlock Overlay" if locked else "Lock Overlay")

        for control in (
            self.x_spin, self.y_spin, self.width_spin, self.height_spin
        ):
            control.setEnabled(not locked)

    def reset_geometry(self):
        if self.overlay.is_locked():
            QMessageBox.information(
                self,
                "Overlay Terkunci",
                "Unlock overlay terlebih dahulu sebelum reset.",
            )
            return

        self.overlay.set_position(100, 100)
        self.overlay.set_overlay_size(800, 450)
        self.sync_geometry(
            self.overlay.x(),
            self.overlay.y(),
            self.overlay.width(),
            self.overlay.height(),
        )

    # ---------------------------------------------------------
    # Visibilitas dan penutupan
    # ---------------------------------------------------------
    def show_overlay(self):
        self.overlay.show()
        self.overlay.raise_()

    def hide_overlay(self):
        self.overlay.hide()

    def closeEvent(self, event):
        self.overlay.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.show_overlay()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
