"""设置面板。"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QButtonGroup, QRadioButton, QWidget,
    QSlider, QCheckBox, QApplication,
)
from PySide6.QtCore import Qt


class SettingsPanel(QDialog):
    """设置面板：快捷键、显示器、透明度、置顶。"""

    def __init__(self, current_hotkey: str, panel_opacity: float = 1.0,
                 bubble_opacity: float = 1.0,
                 always_on_top: bool = True,
                 selected_screen_name: str | None = None,
                 on_hotkey_changed=None, on_panel_opacity_changed=None,
                 on_bubble_opacity_changed=None,
                 on_pin_changed=None, on_screen_changed=None, parent=None):
        super().__init__(parent)
        self._current_hotkey = current_hotkey
        self._on_hotkey_changed = on_hotkey_changed
        self._on_panel_opacity_changed = on_panel_opacity_changed
        self._on_bubble_opacity_changed = on_bubble_opacity_changed
        self._on_pin_changed = on_pin_changed
        self._on_screen_changed = on_screen_changed
        self._panel_opacity = panel_opacity
        self._bubble_opacity = bubble_opacity
        self._always_on_top = always_on_top
        self._selected_screen_name = selected_screen_name

        self._setup_ui()

    def _setup_ui(self) -> None:
        from src.core.theme import theme

        self.setWindowTitle("设置")
        self.setFixedSize(400, 540)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("SettingsPanel { background: transparent; }")

        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet(theme.dialog_css())

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        # 标题栏
        header = QHBoxLayout()
        title = QLabel("设  置")
        title.setStyleSheet(f"font-size:16px; font-weight:600; color:{theme.color('text_primary')};")
        header.addWidget(title)
        header.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; font-size: 14px; color: {theme.color('text_secondary')}; }}"
            f"QPushButton:hover {{ color: {theme.color('text_primary')}; }}"
        )
        header.addWidget(close_btn)
        layout.addLayout(header)

        # 快捷键
        layout.addWidget(self._section_label("快捷键"))
        self._hotkey_input = QLineEdit()
        self._hotkey_input.setPlaceholderText("按下新快捷键...")
        self._hotkey_input.setFixedHeight(40)
        self._hotkey_input.setReadOnly(True)
        self._hotkey_input.keyPressEvent = self._on_hotkey_key_press
        self._hotkey_input.setText(self._current_hotkey)
        layout.addWidget(self._hotkey_input)

        # 面板和气泡透明度独立调节。
        self._panel_opacity_slider, self._panel_opacity_label = self._add_opacity_control(
            layout,
            "面板透明度",
            self._panel_opacity,
            self._on_panel_slider_change,
        )
        self._bubble_opacity_slider, self._bubble_opacity_label = self._add_opacity_control(
            layout,
            "气泡透明度",
            self._bubble_opacity,
            self._on_bubble_slider_change,
        )

        # 置顶开关
        self._pin_check = QCheckBox("窗口置顶 (Always on Top)")
        self._pin_check.setChecked(self._always_on_top)
        self._pin_check.toggled.connect(self._on_pin_toggle)
        self._pin_check.setStyleSheet(
            f"font-size: 13px; color: {theme.color('text_primary')}; spacing: 8px;"
        )
        layout.addWidget(self._pin_check)

        # 显示器
        layout.addWidget(self._section_label("显示器"))
        screens = QApplication.screens()
        self._display_group = QButtonGroup(self)
        selected_found = False
        for i, screen in enumerate(screens):
            geo = screen.geometry()
            primary_label = " · 主屏" if screen is QApplication.primaryScreen() else ""
            radio = QRadioButton(
                f"显示器 {i + 1} · {screen.name()}"
                f" ({geo.width()}×{geo.height()}){primary_label}"
            )
            is_selected = screen.name() == self._selected_screen_name
            if is_selected:
                selected_found = True
                radio.setChecked(True)
            self._display_group.addButton(radio, i)
            radio.toggled.connect(
                lambda checked, name=screen.name():
                self._on_display_toggle(checked, name)
            )
            radio.setStyleSheet(f"font-size:13px; color:{theme.color('text_primary')};")
            layout.addWidget(radio)

        if screens and not selected_found:
            fallback = QApplication.primaryScreen() or screens[0]
            fallback_index = screens.index(fallback)
            self._display_group.button(fallback_index).setChecked(True)

        layout.addStretch()

        # 关闭按钮
        close_btn2 = QPushButton("关  闭")
        close_btn2.setFixedHeight(40)
        close_btn2.clicked.connect(self.close)
        close_btn2.setStyleSheet(f"""
            QPushButton {{
                background: {theme.color('accent_primary')};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {theme.color('accent_primary_hover')};
            }}
        """)
        layout.addWidget(close_btn2)

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(container)

    def _section_label(self, text: str) -> QLabel:
        from src.core.theme import theme
        label = QLabel(text)
        label.setStyleSheet(
            f"font-size:13px; font-weight:500; color:{theme.color('text_secondary')};"
        )
        return label

    def _add_opacity_control(self, layout, title, value, callback):
        from src.core.theme import theme
        layout.addWidget(self._section_label(title))
        row = QHBoxLayout()
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(20, 100)
        slider.setValue(int(max(0.2, min(1.0, value)) * 100))
        row.addWidget(slider)
        label = QLabel(f"{slider.value()}%")
        label.setFixedWidth(40)
        label.setStyleSheet(
            f"color: {theme.color('text_primary')}; font-size:13px;"
        )
        row.addWidget(label)
        layout.addLayout(row)
        slider.valueChanged.connect(callback)
        return slider, label

    def _on_panel_slider_change(self, value: int) -> None:
        self._panel_opacity_label.setText(f"{value}%")
        if self._on_panel_opacity_changed:
            self._on_panel_opacity_changed(value / 100.0)

    def _on_bubble_slider_change(self, value: int) -> None:
        self._bubble_opacity_label.setText(f"{value}%")
        if self._on_bubble_opacity_changed:
            self._on_bubble_opacity_changed(value / 100.0)

    def _on_pin_toggle(self, checked: bool) -> None:
        if self._on_pin_changed:
            self._on_pin_changed(checked)

    def _on_display_toggle(self, checked: bool, screen_name: str) -> None:
        if checked and self._on_screen_changed:
            self._on_screen_changed(screen_name)

    def _on_hotkey_key_press(self, event) -> None:
        modifiers = event.modifiers()
        key = event.key()

        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return

        parts = []
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append("ctrl")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append("shift")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append("alt")

        key_name = Qt.Key(key).name.decode() if hasattr(Qt.Key(key), 'name') else str(key)
        parts.append(key_name.lower())
        new_hotkey = "+".join(parts)
        self._hotkey_input.setText(new_hotkey)

        if self._on_hotkey_changed:
            self._on_hotkey_changed(new_hotkey)
