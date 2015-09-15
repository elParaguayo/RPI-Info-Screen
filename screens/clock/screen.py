from kivy.properties import DictProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from datetime import datetime
from time import sleep



class ClockScreen(Screen):
    timedata = DictProperty(None)

    def __init__(self, **kwargs):
        self.get_time()
        self.master = kwargs["master"]
        super(ClockScreen, self).__init__(**kwargs)

    def get_time(self):
        n = datetime.now()
        self.timedata["h"] = n.hour
        self.timedata["m"] = n.minute
        self.timedata["s"] = n.second

    def update(self, dt):
        self.get_time()

    def on_enter(self):
        Clock.schedule_interval(self.update, 1)

    def on_pre_enter(self):
        self.get_time()

    def on_pre_leave(self):
        Clock.unschedule(self.update)

    # def on_touch_down(self, i):
    #     self.manager.current = self.master.next_screen()
