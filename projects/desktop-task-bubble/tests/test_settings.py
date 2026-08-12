"""应用设置和屏幕选择回归测试。"""
import json
import tempfile
import unittest
from pathlib import Path

from src.core.settings import AppSettings
from src.ui.bubble_panel import resolve_screen


class FakeScreen:
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name


class AppSettingsTest(unittest.TestCase):
    def test_screen_name_is_saved_and_restored(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            AppSettings(path).set_screen_name("DELL P2422H (1)")

            restored = AppSettings(path)

            self.assertEqual(restored.screen_name, "DELL P2422H (1)")
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8"))["screen_name"],
                "DELL P2422H (1)",
            )

    def test_corrupt_settings_use_default(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text("not json", encoding="utf-8")

            self.assertIsNone(AppSettings(path).screen_name)

    def test_opacities_are_saved_independently_and_restored(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            settings = AppSettings(path)
            settings.set_panel_opacity(0.35)
            settings.set_bubble_opacity(0.8)

            restored = AppSettings(path)

            self.assertEqual(restored.panel_opacity, 0.35)
            self.assertEqual(restored.bubble_opacity, 0.8)

    def test_opacity_defaults_and_values_are_clamped(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            settings = AppSettings(path)
            self.assertEqual(settings.panel_opacity, 1.0)
            self.assertEqual(settings.bubble_opacity, 1.0)

            settings.set_panel_opacity(0.1)
            settings.set_bubble_opacity(2.0)

            self.assertEqual(settings.panel_opacity, 0.2)
            self.assertEqual(settings.bubble_opacity, 1.0)

    def test_resolve_screen_matches_name_and_falls_back(self):
        primary = FakeScreen("primary")
        secondary = FakeScreen("secondary")
        screens = [primary, secondary]

        self.assertIs(resolve_screen(screens, "secondary", primary), secondary)
        self.assertIs(resolve_screen(screens, "disconnected", primary), primary)
        self.assertIs(resolve_screen(screens, None, primary), primary)


if __name__ == "__main__":
    unittest.main()
