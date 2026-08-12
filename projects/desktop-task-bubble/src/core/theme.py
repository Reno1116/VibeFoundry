"""深浅主题管理器。

使用 darkdetect 检测系统主题，提供颜色变量映射。
"""

import darkdetect


class ThemeManager:
    """管理系统主题状态，提供颜色变量。"""

    THEME_LIGHT = "light"
    THEME_DARK = "dark"

    # 浅色主题色表
    _light = {
        "bubble_bg": "#ffffff",
        "bubble_bg_overtime": "#b71c1c",  # 超时整卡
        "dialog_bg": "#ffffff",
        "sidebar_bg": "rgba(0,0,0,0.02)",
        "text_primary": "#212121",
        "text_secondary": "#757575",
        "text_inverse": "#ffffff",
        "text_hint": "#9E9E9E",
        "border_subtle": "rgba(0,0,0,0.08)",
        "menu_bg": "#ffffff",
        "menu_hover": "rgba(0,0,0,0.04)",
        "panel_bg": "#f5f5f5",
        "shadow_bubble": "rgba(0,0,0,20)",
        "shadow_dialog": "rgba(0,0,0,38)",
        "shadow_menu": "rgba(0,0,0,30)",
        "accent_primary": "#1976D2",
        "accent_primary_hover": "#1565C0",
        "danger": "#d32f2f",
        "input_border": "rgba(0,0,0,0.08)",
        "input_focus": "#1976D2",
    }

    # 深色主题色表
    _dark = {
        "bubble_bg": "#2D2D2D",
        "bubble_bg_overtime": "#b71c1c",
        "dialog_bg": "#1E1E1E",
        "sidebar_bg": "rgba(255,255,255,0.02)",
        "text_primary": "#EEEEEE",
        "text_secondary": "#9E9E9E",
        "text_inverse": "#ffffff",
        "text_hint": "#757575",
        "border_subtle": "rgba(255,255,255,0.08)",
        "menu_bg": "#2D2D2D",
        "menu_hover": "rgba(255,255,255,0.06)",
        "panel_bg": "#121212",
        "shadow_bubble": "rgba(0,0,0,40)",
        "shadow_dialog": "rgba(0,0,0,60)",
        "shadow_menu": "rgba(0,0,0,50)",
        "accent_primary": "#42A5F5",
        "accent_primary_hover": "#64B5F6",
        "danger": "#EF5350",
        "input_border": "rgba(255,255,255,0.12)",
        "input_focus": "#42A5F5",
    }

    def __init__(self):
        self._current = self.detect()

    def detect(self) -> str:
        """检测当前系统主题。"""
        theme = darkdetect.theme()
        return self.THEME_DARK if theme and "Dark" in theme else self.THEME_LIGHT

    def refresh(self) -> str:
        """刷新主题检测，如已变化则返回新主题名，否则返回 None。"""
        new_theme = self.detect()
        if new_theme != self._current:
            self._current = new_theme
            return new_theme
        return None

    @property
    def current(self) -> str:
        return self._current

    @property
    def is_dark(self) -> bool:
        return self._current == self.THEME_DARK

    def color(self, key: str) -> str:
        """根据当前主题返回颜色值。"""
        table = self._dark if self.is_dark else self._light
        return table.get(key, self._light.get(key, "#000000"))

    def bubble_bg(self, is_overtime: bool = False) -> str:
        return self.color("bubble_bg_overtime") if is_overtime else self.color("bubble_bg")

    def dialog_css(self, extra: str = "") -> str:
        """返回弹窗容器的主题 CSS。"""
        return f"""
            #container {{
                background: {self.color('dialog_bg')};
                border-radius: 12px;
            }}
            QLabel {{
                color: {self.color('text_primary')};
            }}
            QLineEdit {{
                border: 1px solid {self.color('border_subtle')};
                border-radius: 8px;
                padding: 0 12px;
                font-size: 13px;
                color: {self.color('text_primary')};
                background: {self.color('dialog_bg')};
            }}
            QLineEdit:focus {{
                border-color: {self.color('accent_primary')};
            }}
            QRadioButton {{
                font-size: 13px;
                color: {self.color('text_primary')};
                spacing: 4px;
            }}
            QDateTimeEdit {{
                border: 1px solid {self.color('border_subtle')};
                border-radius: 8px;
                padding: 0 12px;
                font-size: 13px;
                color: {self.color('text_primary')};
                background: {self.color('dialog_bg')};
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.color('border_subtle')};
                border-radius: 3px;
            }}
            QMenu {{
                background: {self.color('menu_bg')};
                border-radius: 8px;
                padding: 4px;
                min-width: 160px;
            }}
            QMenu::item {{
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 13px;
                color: {self.color('text_primary')};
            }}
            QMenu::item:selected {{
                background: {self.color('menu_hover')};
            }}
            QMenu::separator {{
                height: 1px;
                background: {self.color('border_subtle')};
                margin: 4px 8px;
            }}
            {extra}
        """

    def bubble_css(self, bg_color: str) -> str:
        """返回单个气泡的主题 CSS。"""
        text = self.color("text_primary")
        return f"""
            BubbleWidget {{
                background: {bg_color};
                border-radius: 12px;
            }}
            QLabel {{
                color: {text};
            }}
        """


# 全局单例
theme = ThemeManager()
