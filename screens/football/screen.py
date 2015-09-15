from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, DictProperty, ListProperty, StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import Color
from datetime import datetime
from time import sleep
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.label import Label
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from footballresources.footballscores import FootballMatch, League
from custom.bglabel import BGLabel

EVT_GOAL = 0
EVT_KICK_OFF = 1
EVT_HALF_TIME = 2
EVT_FULL_TIME = 3
EVT_YELLOW_CARD = 4
EVT_RED_CARD = 5

EVT_LOOKUP = {EVT_GOAL: {"text": "GOAL!", "size": 200},
              EVT_KICK_OFF: {"text": "KICK\nOFF", "size": 175},
              EVT_HALF_TIME: {"text": "HALF\nTIME", "size": 175},
              EVT_FULL_TIME: {"text": "FULL\nTIME", "size": 175}
              }

OBJ_MATCH = 0
OBJ_LEAGUE = 1

class FootballEvent(BGLabel):
    event_text = StringProperty("")

    def __init__(self, **kwargs):
        super(FootballEvent, self).__init__(**kwargs)
        self.event_text = kwargs["eventtext"]

class FootballNoMatch(BoxLayout):
    teamname = StringProperty("")
    def __init__(self, **kwargs):
        super (FootballNoMatch, self).__init__(**kwargs)
        self.teamname = kwargs["teamname"]

class FootballBase(Screen):
    teamname = StringProperty("")

    def __init__(self,**kwargs):
        super (FootballBase, self).__init__(**kwargs)
        self.team = kwargs["team"]
        self.teamname = self.team
        self.running = False
        self.no_match = None
        self.scr_match = None
        self.timer = None

    def on_enter(self):
        Clock.schedule_once(self.getMatchObject, 0.5)
        #Clock.schedule_once(self.update, 0.5)
        self.timer = Clock.schedule_interval(self.update, 10)

    def on_leave(self):
        Clock.unschedule(self.timer)

    def getMatchObject(self, *args):
        if not self.running:
            self.matchobject = FootballMatch(self.team, detailed=True)
            self.running = True
        self.checkscreen()

    def checkscreen(self):
        try:
            loading = self.ids.lbl_load
            self.ids.base_float.remove_widget(loading)
        except:
            pass

        if self.matchobject.MatchFound:
            if self.no_match or not self.scr_match:
                if self.no_match:
                    self.ids.base_float.remove_widget(self.ids.no_match)
                    self.no_match = None
                self.scr_match = FootballMatchScreen(mo=self.matchobject,
                                                 id="scr_match")
                self.ids.base_float.add_widget(self.scr_match)
            else:
                if self.scr_match:
                    self.scr_match.update(self.matchobject)

        else:
            if self.scr_match or not self.no_match:
                if self.scr_match:
                    self.ids.base_floatremove_widget(self.ids.scr_match)
                    self.scr_match = None
                self.no_match = FootballNoMatch(teamname=self.team,
                                                    id="no_match")
                self.ids.base_float.add_widget(self.no_match)

    def notifyEvent(self, event_type=EVT_HALF_TIME):
            t = EVT_LOOKUP[event_type]
            g = FootballEvent(eventtext=t["text"])
            self.ids.base_float.add_widget(g)
            in_anim = Animation(font_size=t["size"], d=1, t="out_back")
            in_anim &= Animation(bgcolour=[0,0,0,1], d=1, t="out_expo")
            out_anim = Animation(font_size=0, d=1, t="out_back")
            out_anim &= Animation(bgcolour=[0,0,0,0], d=1, t="out_expo")
            anim = in_anim + Animation(d=2.) + out_anim
            anim.bind(on_complete=self.notifyComplete)
            anim.start(g)

    def notifyComplete(self, anim, widget):
        anim.unbind()
        self.ids.base_float.remove_widget(widget)

    def update(self, *args):
        self.matchobject.Update()
        if self.matchobject.Goal:
            self.notifyEvent(event_type=EVT_GOAL)

        elif self.matchobject.StatusChanged:
            status = self.matchobject.Status
            if status == "FT":
                self.notifyEvent(event_type=EVT_FULL_TIME)
            elif status == "HT":
                self.notifyEvent(event_type=EVT_HALF_TIME)
            elif status == "L":
                self.notifyEvent(event_type=EVT_KICK_OFF)

        self.checkscreen()

class LeagueBase(Screen):
    leaguename = StringProperty("")

    def __init__(self,**kwargs):
        super (LeagueBase, self).__init__(**kwargs)
        self.leagueid = kwargs["league"]
        self.leaguename = "Retrieving league information."
        self.running = False
        self.timer = None
        self.leaguestack = None
        self.leaguebox = self.ids.league_box

    def on_enter(self):
        Clock.schedule_once(self.getLeagueObject, 0.5)
        self.timer = Clock.schedule_interval(self.update, 30)

    def getLeagueObject(self, *args):
        if not self.running:
            self.leagueobject = League(self.leagueid, detailed=False)
            self.running = True
        self.checkscreen()

    def update(self, *args):
        self.leagueobject.Update()

        self.checkscreen()

        if self.leagueobject.Goal:
            self.notifyEvent(event_type=EVT_GOAL)

        elif self.leagueobject.StatusChanged:
            s = set([x.Status for x in self.leagueobject.LeagueMatches
                    if x.StatusChanged])
            for status in s:
                if status == "FT":
                    self.notifyEvent(event_type=EVT_FULL_TIME)
                elif status == "HT":
                    self.notifyEvent(event_type=EVT_HALF_TIME)
                elif status == "L":
                    self.notifyEvent(event_type=EVT_KICK_OFF)



    def checkscreen(self):
        if self.leagueobject:
            if not self.leaguestack:
                self.leaguestack = self.createStack()
                self.leaguename = self.leagueobject.LeagueName
                self.leaguebox.add_widget(self.leaguestack)

            else:
                newstack = self.createStack()
                self.leaguebox.remove_widget(self.leaguestack)
                self.leaguestack = newstack
                self.leaguebox.add_widget(self.leaguestack)

    def createStack(self):
        stack = StackLayout(orientation="tb-lr",
                            size_hint_y=0.8)
        for l in self.leagueobject.LeagueMatches:
            lg = LeagueGame(match=l)
            stack.add_widget(lg)
        return stack

    def notifyEvent(self, event_type=EVT_HALF_TIME):
        t = EVT_LOOKUP[event_type]
        g = FootballEvent(eventtext=t["text"])
        self.ids.base_float.add_widget(g)
        in_anim = Animation(font_size=t["size"], d=1, t="out_back")
        in_anim &= Animation(bgcolour=[0,0,0,1], d=1, t="out_expo")
        out_anim = Animation(font_size=0, d=1, t="out_back")
        out_anim &= Animation(bgcolour=[0,0,0,0], d=1, t="out_expo")
        anim = in_anim + Animation(d=2.) + out_anim
        anim.bind(on_complete=self.notifyComplete)
        anim.start(g)

    def notifyComplete(self, anim, widget):
        anim.unbind()
        self.ids.base_float.remove_widget(widget)



class LeagueGame(BoxLayout):
    hometeam = StringProperty("")
    awayteam = StringProperty("")
    homescore = StringProperty("")
    awayscore =  StringProperty("")
    status = StringProperty("")
    homebg = ListProperty([0.1, 0.1, 0.1, 1])
    awaybg = ListProperty([0.1, 0.1, 0.1, 1])

    def __init__(self, **kwargs):
        super(LeagueGame, self).__init__(**kwargs)
        m = kwargs["match"]
        self.hometeam = m.HomeTeam
        self.awayteam = m.AwayTeam
        self.homescore = str(m.HomeScore)
        self.awayscore = str(m.AwayScore)
        self.status = m.Status
        if m.HomeGoal:
            self.homebg = [0, 0.8, 0, 1]
        if m.AwayGoal:
            self.awaybg = [0, 0.8, 0, 1]

        if m.Status == "FT":
            self.homebg = [0.1, 0.1, 0.5, 1]
            self.awaybg = [0.1, 0.1, 0.5, 1]


class FootballMatchScreen(FloatLayout):
    hometeam = StringProperty("")
    awayteam = StringProperty("")
    homescore = StringProperty("")
    awayscore = StringProperty("")
    homebadge = StringProperty("")
    awaybadge = StringProperty("")
    status = StringProperty("")

    def __init__(self, **kwargs):
        super (FootballMatchScreen, self).__init__(**kwargs)
        self.matchobject = kwargs["mo"]
        self.checkMatch()
        if self.matchobject.getTeamBadges():
            self.homebadge = self.matchobject.HomeBadge
            self.awaybadge = self.matchobject.AwayBadge

    def update(self, mo):
        self.matchobject = mo
        self.checkMatch(None)

    def checkMatch(self, dt=0):
        #self.matchobject.Update()
        self.hometeam = self.matchobject.HomeTeam
        self.awayteam = self.matchobject.AwayTeam
        self.homescore = str(self.matchobject.HomeScore)
        self.awayscore = str(self.matchobject.AwayScore)
        self.status = str(self.matchobject.MatchTime)

class FootballScreen(Screen):
    def __init__(self, **kwargs):
        super(FootballScreen, self).__init__(**kwargs)
        self.params = kwargs["params"]
        self.setup()
        self.flt = self.ids.football_float
        self.flt.remove_widget(self.ids.football_base_box)
        self.fscrmgr = self.ids.football_scrmgr
        self.running = False
        self.scrid = 0

    def setup(self):
        self.myteams = self.params["teams"]
        self.myleagues = self.params["leagues"]
        self.myscreens = self.myteams[:] + self.myleagues[:]
        self.running = False

    def on_enter(self):
        print "MAIN FOOTBALL SCREEN ENTERED "
        if not self.running:
            for team in self.myteams:
                self.fscrmgr.add_widget(FootballBase(team=team, name=team))
            for league in self.myleagues:
                self.fscrmgr.add_widget(LeagueBase(league=league, name=league))
            self.running = True
            self.fscrmgr.current = self.myteams[0]

    def next_screen(self, rev=True):
        a = self.myscreens
        n = -1 if rev else 1
        self.scrid = (self.scrid + n) % len(a)
        self.fscrmgr.transition.direction = "up" if rev else "down"
        self.fscrmgr.current = a[self.scrid]
        print "Clicking {}".format(self.scrid)
