import pygame
from time import strftime
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import urllib2
import simplejson as json
import os
import struct
from displayscreen import PiInfoScreen


class myScreen(PiInfoScreen):
    supportedsizes = [ (694,466) ]
    refreshtime = 60
    displaytime = 5
    pluginname = "TubeStatus"
    plugininfo = "Shows current status of London Underground"
    
    
    def setPluginVariables(self):
        self.datasource = "http://cloud.tfl.gov.uk/TrackerNet/LineStatus"
        self.tubelayout = [
            (10,100), (10,150), (10,200), (10,250), (10,300), (10,350), (10,400),
            (347,100), (347,150), (347,200), (347,250), (347,300), (347,350), (347,400)
            ]
        self.statuscolour = [(0,0,0), (17,56,146)]
        configfile = os.path.join(self.plugindir, "resources", "resources.json")
        jconfig = open(configfile, 'r')
        self.config = json.load(jconfig)
    
    def showScreen(self):
        self.surface.fill([255,255,255])
        myfont = pygame.font.SysFont("freesans", 32)
        header = myfont.render("Live Tube Status",1, [0,0,0])
        width=header.get_rect()[2]
        headerx= int((self.surfacesize[0]/2) - (width/2))
        self.surface.blit(header,[headerx,20])
        myfont = pygame.font.SysFont(None, 22)
        response = urllib2.urlopen(self.datasource)
        html = response.read()
        xmldoc = ET.fromstring(html)
        for (i, child) in enumerate(xmldoc.findall('{http://webservices.lul.co.uk/}LineStatus')):
            line = child.find('{http://webservices.lul.co.uk/}Line').attrib['Name']
            status = child.find('{http://webservices.lul.co.uk/}Status').attrib['Description']
            bgrgb = self.config['tube']['colours'][line]['background'][-6:]
            textrgb = self.config['tube']['colours'][line]['text'][-6:]
            linebg = struct.unpack('BBB',bgrgb.decode('hex'))
            linetext = struct.unpack('BBB',textrgb.decode('hex'))
            linelabel = myfont.render(line, 1, linetext)
            if status == "Good Service":
                statuscolour = self.statuscolour[0]
            else:
                statuscolour = self.statuscolour[1]
            statuslabel = myfont.render(status, 1, statuscolour)    
            myheight = int(linelabel.get_rect()[3]/2)
            self.surface.fill(linebg,[self.tubelayout[i][0], self.tubelayout[i][1]-myheight,190, 50])
            
            self.surface.blit(linelabel, [self.tubelayout[i][0] + 5, self.tubelayout[i][1] + 5]) 
            self.surface.blit(statuslabel, [self.tubelayout[i][0] + 200, self.tubelayout[i][1] + 5])

        updatetext = "Updated at %s on %s." % (
                    strftime("%H:%M"),
                    strftime("%a %d %b %Y") )
        updatelabel = myfont.render(updatetext, 1, [0,0,0])
        updaterect = updatelabel.get_rect()
        updatepos = [self.surfacesize[0] - updaterect[2] - 5, self.surfacesize[1] - updaterect[3] - 5]
        self.surface.blit(updatelabel, updatepos)

        # Scale our surface to the required screensize before sending back
        scaled = pygame.transform.scale(self.surface,self.screensize)
        self.screen.blit(scaled,(0,0))

        return self.screen
