from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, DictProperty, ListProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import Color
from datetime import datetime
from time import sleep
from kivy.uix.screenmanager import Screen

class DummyScreen(Screen):
    def __init__(self, **kwargs):
        self.master = kwargs["master"]
        super(DummyScreen, self).__init__(**kwargs)

    # def on_touch_down(self, i):
    #     self.manager.current = self.master.next_screen()
