"""设置面板。"""
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QButtonGroup,
    QRadioButton,
    QWidget,
    QApplication,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QScreen

from src.core.config import DIALOG_RADIUS, BUTTON_RADIUS, DEFAULT_HOTKEY


class SettingsPanel(QDialog):
    """设置面板：快捷键、显示器、气泡大小。"""

    def __init__(self, current_hotkey: str, on_hotkey_changed=None, parent=None):
        super().__init__(parent)
        self._current_hotkey = current_hotkey
        self._on_hotkey_changed = on_hotkey_changed

        self._setup_ui()
        self._hotkey_input.setText(current_hotkey)

    def _setup_ui(self) -> None:
        self.setWindowTitle("设置")
        self.setFixedSize(400, 340)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("SettingsPanel { background: transparent; }")

        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet(f"""
            #container {{
                background: #ffffff;
                border-radius: {DIALOG_RADIUS}px;
            }}
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        # 标题栏
        header = QHBoxLayout()
        title = QLabel("设  置")
        title.setStyleSheet("font-size:16px; font-weight:600; color:#212121;")
        header.addWidget(title)
        header.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; font-size: 14px; color: #757575; }"
            "QPushButton:hover { color: #212121; }"
        )
        header.addWidget(close_btn)
        layout.addLayout(header)

        # 快捷键
        hotkey_label = QLabel("快捷键")
        hotkey_label.setStyleSheet("font-size:13px; font-weight:500; color:#757575;")
        layout.addWidget(hotkey_label)

        self._hotkey_input = QLineEdit()
        self._hotkey_input.setPlaceholderText("按下新快捷键...")
        self._hotkey_input.setFixedHeight(40)
        self._hotkey_input.setReadOnly(True)
        self._hotkey_input.keyPressEvent = self._on_hotkey_key_press
        self._hotkey_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: {BUTTON_RADIUS}px;
                padding: 0 12px;
                font-size: 13px;
                color: #212121;
            }}
            QLineEdit:focus {{
                border-color: #1976D2;
            }}
        """)
        layout.addWidget(self._hotkey_input)

        # 显示器选择
        display_label = QLabel("显示器")
        display_label.setStyleSheet("font-size:13px; font-weight:500; color:#757575;")
        layout.addWidget(display_label)

        self._display_group = QButtonGroup(self)
        display_row = QVBoxLayout()
        display_row.setSpacing(8)

        screens = QApplication.screens()
        for i, screen in enumerate(screens):
            geo = screen.geometry()
            radio = QRadioButton(f"显示器 {i + 1} ({geo.width()}×{geo.height()})")
            if i == 0:
                radio.setChecked(True)
            self._display_group.addButton(radio, i)
            radio.setStyleSheet("font-size:13px; color:#212121;")
            display_row.addWidget(radio)

        layout.addLayout(display_row)

        # 底部关闭
        layout.addStretch()
        close_btn2 = QPushButton("关  闭")
        close_btn2.setFixedHeight(40)
        close_btn2.clicked.connect(self.close)
        close_btn2.setStyleSheet(f"""
            QPushButton {{
                background: #1976D2;
                color: #ffffff;
                border: none;
                border-radius: {BUTTON_RADIUS}px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: #1565C0;
            }}
        """)
        layout.addWidget(close_btn2)

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(container)

    def _on_hotkey_key_press(self, event) -> None:
        """捕获按键组合作为新快捷键。"""
        from PySide6.QtCore import Qt as QtCore

        modifiers = event.modifiers()
        key = event.key()

        if key in (QtCore.Key.Key_Control, QtCore.Key.Key_Shift, QtCore.Key.Key_Alt, QtCore.Key.Key_Meta):
            return  # 忽略单独的修饰键

        parts = []
        if modifiers & QtCore.KeyboardModifier.ControlModifier:
            parts.append("ctrl")
        if modifiers & QtCore.KeyboardModifier.ShiftModifier:
            parts.append("shift")
        if modifiers & QtCore.KeyboardModifier.AltModifier:
            parts.append("alt")

        key_name = QtCore.Key(key).name.decode() if hasattr(QtCore.Key(key), 'name') else str(key)
        parts.append(key_name.lower())

        new_hotkey = "+".join(parts)
        self._hotkey_input.setText(new_hotkey)

        if self._on_hotkey_changed:
            self._on_hotkey_changed(new_hotkey)
