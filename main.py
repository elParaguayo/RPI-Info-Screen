import imp
import os
import json
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Rectangle, Color

from custom.bglabel import BGLabel, BGLabelButton
from custom.homemenu import NextScreenButton


Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

class HiddenButton(ButtonBehavior, BGLabel):
    def FlashOn(self):
        self.bgcolour = [0, 1, 1, 0.3]

    def FlashOff(self):
        self.bgcolour = [0,0,0,0]

class ScrollableLabel(ScrollView):
    text = StringProperty('')

def getPlugins():
    plugins = []
    possibleplugins = os.listdir(PluginFolder)
    a=1
    for i in possibleplugins:
        location = os.path.join(PluginFolder,i)
        if not os.path.isdir(location) or not PluginScript in os.listdir(location):
            continue
        inf = imp.find_module(MainModule, [location])
        if ScreenConf in os.listdir(location):
            conf = json.load(open(os.path.join(location, ScreenConf)))
            plugin = {"name": i,
                      "info": inf,
                      "id": a,
                      "screen": conf["screen"],
                      "kv": open(os.path.join(location, conf["kv"])).readlines(),
                      "params": conf.get("params", None)}
            plugins.append(plugin)
            a=a+1
    return plugins



class InfoScreen(FloatLayout):
    def __init__(self, **kwargs):
        super(InfoScreen, self).__init__(**kwargs)
        print "Initialised"

        self.index = 0
        self.scrmgr = self.ids.iscreenmgr
        for p in plugins:
            plugin = imp.load_module(MainModule, *p["info"])
            screen = getattr(plugin, p["screen"])
            self.scrmgr.add_widget(screen(name=p["name"],
                                 master=self,
                                 params=p["params"]))


    def next_screen(self, rev=False):
        if rev:
            self.scrmgr.transition.direction = "right"
            inc = -1
        else:
            self.scrmgr.transition.direction = "left"
            inc = 1

        self.index = (self.index + inc) % len(plugins)
        self.scrmgr.current = plugins[self.index]["name"]

class InfoScreenApp(App):
    def build(self):
        Window.size = (800,480)
        return InfoScreen()

if __name__ == "__main__":

    PluginFolder = "./screens"
    PluginScript = "screen.py"
    MainModule = "screen"
    ScreenConf = "conf.json"
    pluginScreens = []

    plugins = getPlugins()
    kv_text = "".join(open("base.kv").readlines()) + "\n"

    for p in plugins:
        kv_text += "".join(p["kv"])

    Builder.load_string(kv_text)


    InfoScreenApp().run()
