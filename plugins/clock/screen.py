import os
from time import strftime
from displayscreen import PiInfoScreen

class myScreen(PiInfoScreen):
    refreshtime = 1
    displaytime = 10
    pluginname = "Clock"
    plugininfo = "Basic digital clock"
    
    def setPluginVariables(self):
        self.clockfont = os.path.join(self.plugindir, "resources", "SFDigitalReadout-Medium.ttf")         
        self.myfont = pygame.font.Font(self.clockfont, 240)
        self.myfontsmall = pygame.font.Font(self.clockfont, 120)
        
    def showScreen(self):
        self.screen.fill([0,0,0])
        mytime = strftime("%H:%M")
        mysecs = strftime("%S")
        clocklabel = self.myfont.render(mytime, 1, [255,255,255])
        secondlabel = self.myfontsmall.render(mysecs, 1, [255,255,255])
        textpos = clocklabel.get_rect()
        textpos.centerx = self.screen.get_rect().centerx
        textpos.centery = self.screen.get_rect().centery
        secpos = [ textpos[0] + textpos[2] + 10, textpos[1] + 70 ]
        self.screen.blit(secondlabel, secpos)
        self.screen.blit(clocklabel, textpos) 

        return self.screen
