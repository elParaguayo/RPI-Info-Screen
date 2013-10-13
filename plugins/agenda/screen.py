# -*- coding: utf-8 -*- 
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime

from pygcal import PyGCal
from displayscreen import PiInfoScreen

class myScreen(PiInfoScreen):
    refreshtime = 1
    displaytime = 10
    pluginname = "Agenda"
    plugininfo = "Displays upcoming events"
    lastrefresh = None
    upcomingevents = []
    
    def setPluginVariables(self):
        self.clockfont = os.path.join(self.plugindir, "resources", "SFDigitalReadout-Medium.ttf")         
        self.myfont = pygame.font.SysFont(None, 20)
        self.icalurl = self.pluginConfig["Calendar"]["icalurl"]
        self.datarefresh = int(self.pluginConfig["Calendar"]["datarefresh"])
        self.ical = PyGCal(self.icalurl)
        self.lastrefresh = datetime.now()
        self.weathersource = self.pluginConfig["Weather"]["weatherurl"]
        self.weatherrefresh = int(self.pluginConfig["Weather"]["weatherrefresh"]) * 60
        self.cacheFile = os.path.join(self.plugindir, "resources", "cachedWeather.json")

    def updateWeather(self):
        weather = json.loads(self.getPage(self.weathersource))
        self.cacheWeather(weather)
        return weather

    def cacheWeather(self, weather):
        cache = {}
        cache['timestamp'] = int(datetime.now().strftime("%s"))
        cache['weather'] = weather
        with open(self.cacheFile, 'w') as outfile:
            json.dump(cache, outfile)   
    
    def loadWeather(self):
        try:
            raw = open(self.cacheFile, 'r')
            cached = json.load(raw)
        except:
            cached = False
            
        if cached:
            if int(datetime.now().strftime("%s")) < int(cached['timestamp']) + self.weatherrefresh:
                weather = cached['weather']
                try:
                    forecast = weather['hourly_forecast']
                except:
                    weather = self.updateWeather()
            else:
                weather = self.updateWeather()

        else:
            weather = self.updateWeather()
        
        return weather
        
    def refreshData(self):
        # Refreshes the iCal data only if the time since the last refresh is greater
        # than the time set in our config file
        if (datetime.now() - self.lastrefresh).total_seconds() > (self.datarefresh * 60):
            self.ical.Update()
            self.lastrefresh = datetime.now()

    def renderWeather(self, hourly):
        hourrect = pygame.Surface((200,90))
        weathertime = datetime.fromtimestamp(float(hourly["FCTTIME"]["epoch"]))
        weatherdate = weathertime.strftime("%a %H:%M")
        weathertext = hourly["condition"]
        weathericon = hourly["icon_url"]
        iconpath = weathericon.split('/')
        iconfile = iconpath[len(iconpath) - 1]
        weathericon = "http://icons.wxug.com/i/c/h/" + iconfile
        weathertemp = "Temp: " + hourly["temp"]["metric"] + u'\xb0' + "C"
        weatherpop = "Rain: " + hourly["pop"] + "%"
        weatherimage = pygame.transform.scale(self.LoadImageFromUrl(weathericon),(80, 80))
        datelabel = self.myfont.render(weatherdate, 1, (255, 255, 255))
        weatherlabel = self.myfont.render(weathertext, 1, (255, 255, 255))
        templabel = self.myfont.render(weathertemp, 1, (255, 255, 255))
        poplabel = self.myfont.render(weatherpop, 1, (255, 255, 255))
        
        hourrect.blit(datelabel, (10, 10))
        hourrect.blit(weatherlabel, (10, 30))
        hourrect.blit(templabel, (10, 50))
        hourrect.blit(poplabel, (10, 70))
        hourrect.blit(weatherimage, (110, 5))
        pygame.draw.rect(hourrect, (100, 100, 100), (5, 5, 190, 85), 1)
        
        return hourrect
        
    
    def formatDate(self, date):
        eventtime = date.strftime("%H:%M")
        
        if date.date() == datetime.now().date():
            eventdate = "Today"
        else:
            eventdate = date.strftime("%a %d/%m/%y")
            
        return eventdate, eventtime

    def isActive(self, event):
        isactive = False
        
        if event["allday"]:
            if (event["start"].date() == datetime.now().date() or
                event["end"].date() == datetime.now().date() or
                (event["start"].date() < datetime.now().date() and event["end"].date() > datetime.now().date())):
                    isactive = True
        else:
            if (event["start"] <= datetime.now(self.ical.TIMEZONE) and event["end"] >= datetime.now(self.ical.TIMEZONE)):
                isactive = True
                
        return isactive
            
    def renderEvent(self, event):
        eventsurface = pygame.Surface((490,87))
        eventcolour = (0,0,0)
        
        startdate, starttime = self.formatDate(event["start"])
        enddate, endtime = self.formatDate(event["end"])
        
        if self.isActive(event):
            rectColour = (150, 0, 0)
        else:
            rectColour = (0, 0, 100)
        
        if event["allday"]:
            start = startdate
            end = enddate
        else:
            start = "%s %s" % (startdate, starttime)
            end = "%s %s" % (enddate, endtime)

        timelabel = "Start:\n%s\nEnd:\n%s" % (start, end)
        timerect = pygame.Rect((0,0,150,87))
                
        timelabel = self.render_textrect(timelabel, None, timerect, 
                                     (255,255,255), eventcolour, 0, shrink=True, 
                                     SysFont=None, MaxFont=50, MinFont=10, vjustification=0, margin=2)
        eventsurface.blit(timelabel, (0,0))
        
        eventrect = pygame.Rect((0,0,340,87))
        eventlabel = event["summary"]
        if event["location"]:
            eventlabel += "\n(%s)" % event["location"]
        eventlabel = self.render_textrect(eventlabel, None, eventrect, 
                                        (255,255,255), eventcolour, 1, shrink=True, 
                                        SysFont=None, MaxFont=30, MinFont=10, vjustification=1, margin=2)
        eventsurface.blit(eventlabel, (150,0))

        pygame.draw.rect(eventsurface, rectColour, (0,0,490,87), 1)
        
        return eventsurface

    def drawClock(self):
        clockSurface = pygame.Surface((200,120))
        mytime = strftime("%H:%M")
        mydate = strftime("%a %e %b %Y")
        clockrect = pygame.Rect((0,0,200,100))
        daterect = pygame.Rect((0,0,200,30))
        clocklabel = self.render_textrect(mytime, None, clockrect, 
                                         (255,255,255), (0,0,0), 1, shrink=True, 
                                         FontPath=self.clockfont, MaxFont=200, MinFont=10, vjustification=1,margin=10)        
        datelabel = self.render_textrect(mydate, None, daterect, 
                                         (255,255,255), (0,0,0), 1, shrink=True, 
                                         FontPath=self.clockfont, MaxFont=50, MinFont=1, vjustification=1,margin=1)        
        
        
        clockSurface.blit(clocklabel,(0,0))
        clockSurface.blit(datelabel,(0,90))
        
        return clockSurface
        
    def showScreen(self):
        self.surface.fill([0,0,0])
        
        # Draw the clock
        self.surface.blit(self.drawClock(), (0,-15))
        
        # Draw the weather 
        weather = self.loadWeather()
        for i in range(4):
            forecast = weather['hourly_forecast'][i]
            self.surface.blit(self.renderWeather(forecast), (0, (90 * i) + 100))

        # Draw the events
        self.refreshData()
        self.upcomingevents = self.ical.getUpcomingEvents(5)
        for i, event in enumerate(self.upcomingevents):
            self.surface.blit(self.renderEvent(event), (200, (92 * i) + 5))

        # Scale our surface to the required screensize before sending back
        scaled = pygame.transform.scale(self.surface,self.screensize)
        self.screen.blit(scaled,(0,0))

        return self.screen
