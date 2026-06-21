"""Minimal Kivy app test — build xong mới add code phức tạp."""

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel


class TestApp(MDApp):
    def build(self):
        return MDLabel(text="ECBA App OK!", halign="center")


if __name__ == "__main__":
    TestApp().run()
