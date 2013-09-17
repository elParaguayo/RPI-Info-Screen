import os
from time import strftime
from MythTV import MythBE
import simplejson as json
from displayscreen import PiInfoScreen

class myScreen(PiInfoScreen):
    refreshtime = 60
    displaytime = 10
    pluginname = "MythTV"
    plugininfo = "Displays details of upcoming recordings"
    supportedsizes = [ (694, 466) ]
    
    def setPluginVariables(self):
        self.be = None
        self.backendfail = False
        self.cachedmode = False
        self.isrecording = False
        self.regularfont = os.path.join(self.plugindir, "resources", "ArchivoNarrow-Regular.otf") 
        self.italicfont = os.path.join(self.plugindir, "resources", "ArchivoNarrow-Italic.otf") 
        self.boldfont = os.path.join(self.plugindir, "resources", "ArchivoNarrow-Bold.otf") 
        self.cacheFile = os.path.join(self.plugindir, "resources", "cachedRecordings.json")
        self.mytitlefont = pygame.font.Font(self.boldfont, 24)
        self.myboldfont = pygame.font.Font(self.boldfont, 20)
        self.myregularfont = pygame.font.Font(self.regularfont, 16)
        self.myitalicfont = pygame.font.Font(self.italicfont, 16)
        self.rectwidth = 132
        self.rectgap = 5
        self.rectadjust = 2
    
    def cacheRecs(self, recs):
        with open(self.cacheFile, 'w') as outfile:
            json.dump(recs, outfile)   
    
    def loadCache(self):
        try:
            raw = open(self.cacheFile, 'r')
            recs = json.load(raw)
        except:
            recs = []
        
        return recs

    def showScreen(self):
        self.surface.fill([0,0,0])

        if self.be == None:
            try:
                recs = []
                self.be = MythBE()
                self.upcomingrecs = self.be.getUpcomingRecordings()
                for r in self.upcomingrecs:
                    rec = {}
                    rec["title"] = r.title
                    rec["subtitle"] = r.subtitle
                    rec["time"] = r.starttime.strftime("%a %d %b %H:%M")
                    rec["desc"] = r.description
                    recs.append(rec)
                recorders = MythBE().getRecorderList()
                for recorder in recorders:
                    if MythBE().isRecording(recorder):
                        self.isrecording = True
                        break
                self.backendfail = False
                self.cachedmode = False
            except:
                self.backendfail = True
        
        if self.backendfail:
            recs = self.loadCache()
            if recs: 
                self.backendfail = False
                self.cachedmode = True
        
        if not self.backendfail:
            
            self.cacheRecs(recs)
            
            screentitle = self.mytitlefont.render("MythTV upcoming recordings",1,(255,255,255))
            screenrect = screentitle.get_rect()
            screenrect.centerx = self.surface.get_rect().centerx
            screenrect.centery = 20
            self.surface.blit(screentitle, screenrect)
            
            n = min(len(recs),5)
            if n > 0:
                for i in range(n):
                    mytitlerect = pygame.Rect((0,0,self.rectwidth,60))
                    mytimerect = pygame.Rect((0,0,self.rectwidth,30))
                    mydescrect = pygame.Rect((0,0,self.rectwidth,330))
                    fontcolour = (255,255,255)
                    rectcolour = (0,50,75)
                    titletext = self.render_textrect(recs[i]["title"], self.myboldfont, mytitlerect, fontcolour, rectcolour,1)
                    timetext = self.render_textrect(recs[i]["time"], self.myitalicfont, mytimerect, fontcolour, rectcolour,1)
                    desctext = self.render_textrect(recs[i]["desc"], self.myregularfont, mydescrect, fontcolour, rectcolour,0,margin=5)
                    self.surface.blit(titletext,((self.rectwidth*i)+(self.rectgap*(i+1)+self.rectadjust), 40))
                    self.surface.blit(timetext,((self.rectwidth*i)+(self.rectgap*(i+1)+self.rectadjust), 80))
                    self.surface.blit(desctext,((self.rectwidth*i)+(self.rectgap*(i+1)+self.rectadjust), 105))
                    
                if self.cachedmode:
                    mystatus = self.myitalicfont.render("Backend is offline. Displaying cached recording list",1,(255,255,255))
                else:
                    if self.isrecording:
                        recording = "currently"
                    else:
                        recording = "not"
                    mystatus = self.myitalicfont.render("Backend is online and is " + recording + " recording.",1,(255,255,255))
                    
                self.surface.blit(mystatus,(5,445))
            else:
                failtext = self.myboldfont.render("No upcoming recordings found.",1, (255,255,255))
                failrect = failtext.get_rect()
                failrect.centerx = self.surface.get_rect().centerx
                failrect.centery = self.surface.get_rect().centery
                self.surface.blit(failtext, failrect)                
            
        else:
            failtext = self.myboldfont.render("MythTV backend unavailable.",1, (255,255,255))
            failrect = failtext.get_rect()
            failrect.centerx = self.surface.get_rect().centerx
            failrect.centery = self.surface.get_rect().centery
            self.surface.blit(failtext, failrect)
        
        self.be = None

        # Scale our surface to the required screensize before sending back
        scaled = pygame.transform.scale(self.surface,self.screensize)
        self.screen.blit(scaled,(0,0))

        return self.screen
