from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, DictProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import sys
import os
from datetime import datetime
from kivy.animation import Animation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from resources.londonunderground import TubeStatus

LINES = ['BAK',
         'CEN',
         'CIR',
         'DIS',
         'DLR',
         'HAM',
         'JUB',
         'MET',
         'NOR',
         'OVE',
         'PIC',
         'TFL',
         'VIC',
         'WAT']


class TubeScreen(Screen):
    # Column 1
    tube = DictProperty({"DLR":"TEST"})
    bakerloo = ObjectProperty(None)
    central = ObjectProperty(None)
    circle = ObjectProperty(None)
    district = ObjectProperty(None)
    hammersmith = ObjectProperty(None)
    jubilee = ObjectProperty(None)
    metropolitan = ObjectProperty(None)

    # Column 2
    northern = ObjectProperty(None)
    piccadilly = ObjectProperty(None)
    victoria = ObjectProperty(None)
    waterloo = ObjectProperty(None)
    overground = ObjectProperty(None)
    rail = ObjectProperty(None)
    dlr = ObjectProperty(None)



    def __init__(self, **kwargs):
        self.master = kwargs["master"]
        self.a = 0
        self.params = kwargs["params"]
        self.build_dict()

        super(TubeScreen, self).__init__(**kwargs)

    def hex_to_kcol(self, hexcol):
        if hexcol.startswith("#"):
            hexcol = hexcol[1:7]

        return [self._HEXDEC[hexcol[0:2]]/255.,
                self._HEXDEC[hexcol[2:4]]/255.,
                self._HEXDEC[hexcol[4:6]]/255.,
                1]

    def build_dict(self):
        _NUMERALS = '0123456789abcdefABCDEF'
        self._HEXDEC = {v: int(v, 16) for v in (x+y for x in _NUMERALS for y in _NUMERALS)}
        for l in LINES:
            self.tube[l] = "Loading data..."
        coldict = self.params["colours"]
        self.coldict = {x[:3].upper(): coldict[x] for x in coldict}
        for c in self.coldict:
            self.coldict[c]["background"] = self.hex_to_kcol(self.coldict[c]["background"])
            self.coldict[c]["text"] = self.hex_to_kcol(self.coldict[c]["text"])
        self.tube["colours"] = self.coldict
        self.tube["update"] = "Waiting for data..."


    def update(self, dt):
        raw = TubeStatus()

        temp = {x["name"][:3].upper(): x["status"]
                     for x in raw}
        for k in temp:
            self.tube[k] = temp[k]

        self.tube["detail"] = {x["name"][:3].upper(): x["detail"]
                               for x in raw}
        self.tube["name"] = {x["name"][:3].upper(): x["name"]
                               for x in raw}
        self.tube["colours"] = self.coldict

        updt = datetime.now().strftime("%H:%M")
        self.tube["update"] = "Last updated at {}".format(updt)

    # def on_touch_down(self, i):
    #     self.manager.current = self.master.next_screen()

    def on_enter(self):
        self.update(None)
        Clock.schedule_interval(self.update, 5 * 60)

    def show_info(self, line):
        w = TubeDetail(line=self.tube["name"][line],
                       detail=self.tube["detail"][line],
                       bg=self.tube["colours"][line]["background"],
                       fg=self.tube["colours"][line]["text"])
        self.ids.tubefloat.add_widget(w)

class TubeDetail(BoxLayout):
    line = StringProperty("")
    detail = StringProperty("")
    bg = ListProperty([])
    fg = ListProperty([])

    def _init__(self, **kwargs):
        super(TubeDetail, self).__init__(**kwargs)
        self.line = kwargs["line"]
        self.detail = kwargs["detail"]
        self.bg = kwargs["bg"]
        self.fg = kwargs["fg"]
