"""面板和气泡透明度独立性回归测试。"""
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage

from src.models.task import Task
from src.ui.bubble_panel import BubblePanel


class FakeStore:
    def __init__(self):
        self.pending_tasks = [Task("test")]

    def on_change(self, callback):
        self.callback = callback


class OpacityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = BubblePanel(
            FakeStore(), panel_opacity=0.4, bubble_opacity=0.7
        )
        self.panel.refresh()

    def tearDown(self):
        self.panel.deleteLater()
        self.app.processEvents()

    def test_panel_and_bubble_opacity_are_independent(self):
        bubble = next(iter(self.panel._bubble_widgets.values()))
        self.assertTrue(
            self.panel.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        )
        self.assertEqual(self.panel.windowOpacity(), 1.0)
        self.assertEqual(bubble._opacity_effect.opacity(), 0.7)

        self.panel.set_panel_opacity(0.3)
        self.assertEqual(bubble._opacity_effect.opacity(), 0.7)
        self.assertEqual(self.panel._panel_background.alpha(), 77)

        self.panel.set_bubble_opacity(0.6)
        self.assertEqual(self.panel._panel_opacity, 0.3)
        self.assertEqual(bubble._opacity_effect.opacity(), 0.6)
        self.assertEqual(self.panel.windowOpacity(), 1.0)

    def test_css_rgba_alpha_is_multiplied(self):
        self.assertEqual(
            BubblePanel._color_with_opacity("rgba(0,0,0,0.08)", 0.5),
            "rgba(0,0,0,10)",
        )

    def test_accent_strip_does_not_move_when_bubble_opacity_changes(self):
        bubble = next(iter(self.panel._bubble_widgets.values()))
        bubble.resize(300, 72)
        bubble.show()
        self.app.processEvents()

        positions = []
        for opacity in (1.0, 0.8, 0.5, 0.2, 1.0):
            bubble.set_opacity(opacity)
            self.app.processEvents()
            image = bubble.grab().toImage().convertToFormat(
                QImage.Format.Format_ARGB32
            )
            blue_x = []
            for y in range(image.height()):
                for x in range(image.width()):
                    color = image.pixelColor(x, y)
                    if (
                        color.blue() > 150
                        and color.blue() > color.red() * 1.3
                        and color.blue() > color.green() * 1.05
                        and color.alpha() > 10
                    ):
                        blue_x.append(x)
            positions.append((min(blue_x), max(blue_x)))

        self.assertEqual(positions, [(0, 3)] * len(positions))


if __name__ == "__main__":
    unittest.main()
