# -*- coding: utf-8 -*- 
import pygame
from time import strftime
import simplejson as json
import os
from displayscreen import PiInfoScreen
from datetime import datetime

class myScreen(PiInfoScreen):
    refreshtime = 60
    displaytime = 10
    supportedsizes = [ (694, 466) ]
    pluginname = "Weather"
    plugininfo = "Displays upcoming weather forecast"
    
    def setPluginVariables(self):
        self.datasource = self.pluginConfig["Weather"]["weathersource"]
        self.weatherrows = [115, 220, 325, 430]
        self.cacherefresh = 3600
        self.cacheFile = os.path.join(self.plugindir, "resources", "cachedWeather.json")
        self.myfont = pygame.font.SysFont("freesans", 20)
        self.mydayfont = pygame.font.SysFont("freesans", 30)
        self.myfontbig = pygame.font.SysFont("freesans", 34)
        self.myrowfont = pygame.font.SysFont("freesans", 18)

    def updateWeather(self):
        weather = json.loads(self.getPage(self.datasource))
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
            if cached['timestamp'] < int(datetime.now().strftime("%s")) + self.cacherefresh:
                print "Loading cache"
                weather = cached['weather']
                try:
                    forecast = weather['forecast']['txt_forecast']['forecastday']
                except:
                    weather = self.updateWeather()
            else:
                print "Updating"
                weather = self.updateWeather()

        else:
            weather = self.updateWeather()
        
        return weather
    
    def showScreen(self):
        
        # Get weather
        weather = self.loadWeather()
        forecast = weather['forecast']['txt_forecast']['forecastday']
        detail = weather['forecast']['simpleforecast']['forecastday']
        
        # Header
        self.surface.fill([200,200,255])
        header = self.myfontbig.render("Weather forecast",1, [0,0,0])
        headerect = header.get_rect()
        headerect.centerx = self.surface.get_rect().centerx
        headerect.centery = 25
        self.surface.blit(header,headerect)
        
        # Draw headers
        pygame.draw.line(self.surface, [0,0,0], [0, 80], [self.surfacesize[0], 80],3)
        weatherday = self.myrowfont.render("Day",1,(0,0,0))
        weatherhigh = self.myrowfont.render("High",1,(0,0,0))
        weatherlow = self.myrowfont.render("Low",1,(0,0,0))
        weatherpop = self.myrowfont.render("Rain",1,(0,0,0))
        self.surface.blit(weatherday, (30,85))
        self.surface.blit(weatherhigh, (310,85))
        self.surface.blit(weatherlow, (450,85))        
        self.surface.blit(weatherpop, (590,85))
        
        # Display weather data
        for wrow in self.weatherrows:
            pygame.draw.line(self.surface, [0,0,0], [0, wrow - 5], [self.surfacesize[0], wrow - 5], 3)

        for i in range(3):
            for day in detail:
                if day['period'] == i + 1:
                    weatherdate = day['date']['weekday']
                    weatherlabel = self.mydayfont.render(weatherdate, 1, [0,0,0])
                    self.surface.blit(weatherlabel, [10, self.weatherrows[i] + 25])
                    iconurl = day['icon_url']
                    iconpath = iconurl.split('/')
                    iconfile = iconpath[len(iconpath) - 1]
                    weatherpath = "http://icons.wxug.com/i/c/i/" + iconfile
                    weatherimage = pygame.transform.scale(self.LoadImageFromUrl(weatherpath),(100,100))
                    self.surface.blit(weatherimage, [150, self.weatherrows[i]])
 
                    weatherhigh = day['high']['celsius'] + u'\xb0' + "C"
                    weatherlow = day['low']['celsius'] + u'\xb0' + "C"
                    weatherpop = str(day['pop']) + "%"
                   
                    weatherhighlabel = self.myfontbig.render(weatherhigh, 1, [0,0,0])
                    weatherlowlabel = self.myfontbig.render(weatherlow, 1, [0,0,0])
                    weatherpoplabel = self.myfontbig.render(weatherpop, 1, [0,0,0])
                    self.surface.blit(weatherhighlabel, [290, self.weatherrows[i]+25])
                    self.surface.blit(weatherlowlabel, [430, self.weatherrows[i]+25])
                    self.surface.blit(weatherpoplabel, [580, self.weatherrows[i]+25])

        # Add details of update time    
        updatetext = "Updated at %s on %s." % (
                    strftime("%H:%M"),
                    strftime("%a %d %b %Y") )
        updatelabel = self.myfont.render(updatetext, 1, [20,20,20])
        updaterect = updatelabel.get_rect()
        updatepos = [self.surfacesize[0] - updaterect[2] - 5, self.surfacesize[1] - updaterect[3] - 2]

        # Scale our surface to the required screensize before sending back
        self.surface.blit(updatelabel, updatepos)
        scaled = pygame.transform.scale(self.surface,self.screensize)
        self.screen.blit(scaled,(0,0))

        return self.screen
