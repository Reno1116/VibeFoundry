"""新增待办弹窗。"""
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QPushButton,
    QDateTimeEdit,
    QButtonGroup,
    QWidget,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QDateTime, QTime, Signal

from src.core.config import TIME_PRESETS, MAX_TITLE_LENGTH, DIALOG_RADIUS, INPUT_RADIUS, BUTTON_RADIUS
from src.core.theme import theme


class AddTaskDialog(QDialog):
    """新增待办弹窗。

    使用方式:
        dialog = AddTaskDialog(parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_data = dialog.get_task_data()
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._task_data: dict | None = None
        self._time_chips: list[QPushButton] = []
        self._custom_input: QLineEdit | None = None
        self._is_custom_selected = False

        self._setup_ui()

    # ── UI 搭建 ──

    def _setup_ui(self) -> None:
        self.setWindowTitle("新增待办")
        self.setFixedWidth(400)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(self._dialog_style())

        # 外层容器（圆角 + 投影通过 QSS）
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setObjectName("container")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        # 标题栏
        self._build_header(layout)
        # 任务标题
        self._build_title_input(layout)
        # 优先级
        self._build_priority(layout)
        # 预计耗时
        self._build_time_chips(layout)
        # 截止时间
        self._build_deadline(layout)
        # 确认按钮
        self._build_confirm_button(layout)

        outer.addWidget(container)

    def _build_header(self, layout: QVBoxLayout) -> None:
        header = QHBoxLayout()
        label = QLabel("新增待办")
        label.setStyleSheet(f"font-size:16px; font-weight:600; color:{theme.color('text_primary')};")
        header.addWidget(label)
        header.addStretch()
        layout.addLayout(header)

    def _build_title_input(self, layout: QVBoxLayout) -> None:
        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("输入任务标题...")
        self._title_input.setMaxLength(MAX_TITLE_LENGTH)
        self._title_input.setFixedHeight(40)
        self._title_input.setStyleSheet(self._input_style())
        self._title_input.textChanged.connect(self._validate)
        layout.addWidget(self._title_input)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color:#d32f2f; font-size:11px;")
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)

    def _build_priority(self, layout: QVBoxLayout) -> None:
        label = QLabel("优先级")
        label.setStyleSheet(f"font-size:13px; font-weight:500; color:{theme.color('text_secondary')};")
        layout.addWidget(label)

        group = QButtonGroup(self)
        row = QHBoxLayout()
        row.setSpacing(12)

        priorities = [
            ("high", "高  🔴"),
            ("medium", "中  🟠"),
            ("low", "低  🟢"),
        ]
        for i, (value, text) in enumerate(priorities):
            radio = QRadioButton(text)
            radio.setStyleSheet(self._radio_style())
            if value == "medium":
                radio.setChecked(True)
            group.addButton(radio)
            setattr(self, f"_radio_{value}", radio)
            row.addWidget(radio)

        row.addStretch()
        layout.addLayout(row)

    def _build_time_chips(self, layout: QVBoxLayout) -> None:
        label = QLabel("预计耗时")
        label.setStyleSheet(f"font-size:13px; font-weight:500; color:{theme.color('text_secondary')};")
        layout.addWidget(label)

        row = QHBoxLayout()
        row.setSpacing(8)

        for minutes in TIME_PRESETS:
            btn = QPushButton(self._format_time_label(minutes))
            btn.setFixedWidth(70)
            btn.setFixedHeight(36)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, m=minutes: self._on_time_chip_click(m))
            btn.setStyleSheet(self._chip_style(False))
            self._time_chips.append(btn)
            row.addWidget(btn)

        # 自定义按钮
        custom_btn = QPushButton("自定义")
        custom_btn.setFixedWidth(70)
        custom_btn.setFixedHeight(36)
        custom_btn.setCheckable(True)
        custom_btn.clicked.connect(self._on_custom_chip_click)
        custom_btn.setStyleSheet(self._chip_style(False))
        self._custom_chip_btn = custom_btn
        row.addWidget(custom_btn)

        row.addStretch()
        layout.addLayout(row)

        # 自定义输入框（默认隐藏）
        self._custom_input = QLineEdit()
        self._custom_input.setPlaceholderText("输入分钟数...")
        self._custom_input.setFixedHeight(36)
        self._custom_input.setFixedWidth(120)
        self._custom_input.setVisible(False)
        self._custom_input.setStyleSheet(self._input_style())
        layout.addWidget(self._custom_input)

    def _build_deadline(self, layout: QVBoxLayout) -> None:
        label = QLabel("截止时间（可选）")
        label.setStyleSheet(f"font-size:13px; font-weight:500; color:{theme.color('text_secondary')};")
        layout.addWidget(label)

        self._deadline_edit = QDateTimeEdit()
        self._deadline_edit.setCalendarPopup(True)
        self._deadline_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        # 允许选今天，最小时间为今天 00:00
        today_start = QDateTime.currentDateTime()
        today_start.setTime(QTime(0, 0))
        self._deadline_edit.setMinimumDateTime(today_start)
        # 默认时间为今天 18:30
        default_dt = QDateTime.currentDateTime()
        default_dt.setTime(QTime(18, 30))
        self._deadline_edit.setDateTime(default_dt)
        self._deadline_edit.setSpecialValueText("不设置截止时间")
        self._deadline_edit.setFixedHeight(40)
        self._deadline_edit.setStyleSheet(self._input_style())
        layout.addWidget(self._deadline_edit)

    def _build_confirm_button(self, layout: QVBoxLayout) -> None:
        self._confirm_btn = QPushButton("确  认")
        self._confirm_btn.setFixedHeight(44)
        self._confirm_btn.setEnabled(False)
        self._confirm_btn.setStyleSheet(self._button_style(False))
        self._confirm_btn.clicked.connect(self._on_confirm)
        layout.addWidget(self._confirm_btn)

    # ── 事件处理 ──

    def _on_time_chip_click(self, minutes: int) -> None:
        """预设时长按钮被点击。"""
        self._is_custom_selected = False
        self._custom_chip_btn.setChecked(False)
        if self._custom_input:
            self._custom_input.setVisible(False)

        # 选中的按钮高亮，其他取消
        for btn in self._time_chips:
            btn.setChecked(btn.text() == self._format_time_label(minutes))
            btn.setStyleSheet(self._chip_style(btn.isChecked()))

    def _on_custom_chip_click(self) -> None:
        """自定义按钮被点击。"""
        self._is_custom_selected = not self._is_custom_selected
        self._custom_chip_btn.setChecked(self._is_custom_selected)
        self._custom_chip_btn.setStyleSheet(self._chip_style(self._is_custom_selected))

        if self._custom_input:
            self._custom_input.setVisible(self._is_custom_selected)

        # 取消预设选择
        for btn in self._time_chips:
            btn.setChecked(False)
            btn.setStyleSheet(self._chip_style(False))

    def _validate(self) -> None:
        """校验表单，控制确认按钮状态。"""
        title = self._title_input.text().strip()
        valid = len(title) > 0
        self._confirm_btn.setEnabled(valid)
        self._confirm_btn.setStyleSheet(self._button_style(valid))

        if not valid and self._title_input.text() != "":
            self._error_label.setText("标题不能全为空格")
            self._error_label.setVisible(True)
        else:
            self._error_label.setVisible(False)

    def _on_confirm(self) -> None:
        """点击确认按钮。"""
        title = self._title_input.text().strip()
        if not title:
            self._error_label.setText("标题不能为空")
            self._error_label.setVisible(True)
            return

        # 收集优先级
        if self._radio_high.isChecked():
            priority = "high"
        elif self._radio_low.isChecked():
            priority = "low"
        else:
            priority = "medium"

        # 收集预计耗时
        if self._is_custom_selected and self._custom_input:
            try:
                estimated = int(self._custom_input.text().strip())
            except ValueError:
                estimated = 30
        else:
            estimated = self._get_selected_preset()

        # 收集截止时间
        deadline = None
        if self._deadline_edit.dateTime().isValid():
            dt = self._deadline_edit.dateTime().toPython()
            # 如果设置了具体时间（非最小时间），则采纳
            if dt > datetime.now():
                deadline = dt

        self._task_data = {
            "title": title,
            "priority": priority,
            "estimated_minutes": estimated,
            "deadline": deadline,
        }
        self.accept()

    def _get_selected_preset(self) -> int:
        """返回当前选中的预设时长。"""
        for i, btn in enumerate(self._time_chips):
            if btn.isChecked():
                return TIME_PRESETS[i]
        return TIME_PRESETS[1]  # 默认 30 分钟

    def get_task_data(self) -> dict:
        """返回用户输入的任务数据。"""
        return self._task_data or {}

    # ── 样式 ──

    @staticmethod
    def _format_time_label(minutes: int) -> str:
        if minutes < 60:
            return f"{minutes}m"
        return f"{minutes // 60}h"

    def _dialog_style(self) -> str:
        return f"""
            AddTaskDialog {{
                background: transparent;
            }}
        """ + theme.dialog_css()

    def _input_style(self) -> str:
        return f"""
            QLineEdit {{
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: {INPUT_RADIUS}px;
                padding: 0 12px;
                font-size: 13px;
                color: #212121;
                background: #ffffff;
            }}
            QLineEdit:focus {{
                border-color: #1976D2;
            }}
        """

    def _radio_style(self) -> str:
        return f"""
            QRadioButton {{
                font-size: 13px;
                color: {theme.color('text_primary')};
                spacing: 4px;
            }}
        """

    def _chip_style(self, selected: bool) -> str:
        if selected:
            return f"""
                QPushButton {{
                    background: #1976D2;
                    color: #ffffff;
                    border: 1px solid #1976D2;
                    border-radius: {BUTTON_RADIUS}px;
                    font-size: 12px;
                }}
            """
        return f"""
            QPushButton {{
                background: #ffffff;
                color: #212121;
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: {BUTTON_RADIUS}px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: rgba(0,0,0,0.02);
            }}
        """

    def _button_style(self, enabled: bool) -> str:
        if enabled:
            return f"""
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
            """
        return f"""
            QPushButton {{
                background: rgba(25,118,210,0.42);
                color: rgba(255,255,255,0.7);
                border: none;
                border-radius: {BUTTON_RADIUS}px;
                font-size: 14px;
                font-weight: 600;
            }}
        """
