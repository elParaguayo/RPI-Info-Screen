import pygame
import os
import struct
from time import strftime

class myScreen():
    
    def __init__(self, screensize):
        self.supportedsizes = [ (964, 466) ]
        self.screensize = screensize
        self.refreshtime = 1
        self.displaytime = 10
        if screensize not in self.supportedsizes:
            print "Unsupported screen size"
            self.supported = False
        else:
            self.supported = True
            
        pygame.init()
        self.screen = pygame.display.set_mode(self.screensize)
        self.mydir=os.path.dirname(os.path.abspath(__file__))
        """configfile = os.path.join(self.mydir, "resources", "resources.json")
        jconfig = open(configfile, 'r')
        self.config = json.load(jconfig)"""
        self.clockfont = os.path.join(self.mydir, "resources", "SFDigitalReadout-Medium.ttf") 
    
    def supported(self):
        return self.supported
        
    def refreshtime(self):
        return self.refreshtime
        
    def displaytime(self):
        return self.displaytime
    
    def showInfo(self):
        return "Clock: provides time"
        
    def screenName(self):
        return "Clock"

    def showScreen(self):
        return True

    def showScreen(self):
        self.screen.fill([0,0,0])
        myfont = pygame.font.Font(self.clockfont, 240)
        myfontsmall = pygame.font.Font(self.clockfont, 120)
        mytime = strftime("%H:%M")
        mysecs = strftime("%S")
        clocklabel = myfont.render(mytime, 1, [255,255,255])
        secondlabel = myfontsmall.render(mysecs, 1, [255,255,255])
        textpos = clocklabel.get_rect()
        textpos.centerx = self.screen.get_rect().centerx
        textpos.centery = self.screen.get_rect().centery
        secpos = [ textpos[0] + textpos[2] + 10, textpos[1] + 70 ]
        self.screen.blit(secondlabel, secpos)

        self.screen.blit(clocklabel, textpos) 


        



        return self.screen
