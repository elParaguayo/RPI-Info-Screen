from displayscreen import PiInfoScreen
import simplejson as json
import urllib2
from datetime import datetime
import os

# Class must have this name
class myScreen(PiInfoScreen):
    pluginname = "Buses"
    plugininfo = "Displays upcoming bus departure times"
    supportedsizes = [ (694,466) ]
    refreshtime = 30
    displaytime = 5
    
    def setPluginVariables(self):
        # Get our journey data
        print "Setting variables..."
        configfile = os.path.join(self.plugindir, "journeys", "journeys.json")
        raw = open(configfile, 'r')
        self.journeys = json.load(raw)

        # Nothing to display if there are no journeys
        if len(self.journeys) == 0:
            self.enabled = False
        else:
            self.enabled = True

    def getBusTimes(self):
        bustimes = []
        for journey in self.journeys:
            url = "http://countdown.api.tfl.gov.uk/interfaces/ura/instant_V1?StopCode1=" + journey['id']
            result = self.getPage(url)
            route = {}
            route['name'] = journey['name']
            route['direction'] = journey['direction']
            bus = []
            for line in result.split("\n"):
                a = json.loads(line)
                if not a[0] == 4:
                    busdetail = {}
                    if len(journey['buses']) >0 and a[2] in journey['buses']: 
                        busdetail["route"] = a[2]
                        busdetail["time"] = int(a[3])
                        bus.append(busdetail)
                    elif len(journey['buses']) == 0:
                        busdetail["route"] = a[2]
                        busdetail["time"] = int(a[3])
                        bus.append(busdetail)
            sortedbus = sorted(bus, key=lambda k: k['time'])                 
            route['buses'] = sortedbus
            bustimes.append(route)
        return bustimes

    def getBusTime(self, epoch):
        epoch = epoch / 1000
        bustime = datetime.fromtimestamp(epoch)
        diff = bustime - datetime.utcnow()
        minutes = (diff.seconds % 3600) // 60
        if minutes == 0:
            arrival = "Due"
        elif minutes == 1:
            arrival = "1 minute"
        else:
            arrival = "%d minutes" % minutes
        return arrival

    # Main function - returns screen to main script
    def showScreen(self):
        self.bustimes = self.getBusTimes()
        mytitlefont = pygame.font.SysFont(None, 30)
        mybusfont = pygame.font.SysFont(None, 25)
        self.screen.fill([0,0,0])
        header = mytitlefont.render("Live bus departures",1,(255,255,255))
        headerrect = header.get_rect()
        headerrect.centerx = self.screen.get_rect().centerx
        self.screen.blit(header, (headerrect[0],10))
        for i, route in enumerate(self.bustimes):
            stop = mybusfont.render("Stop:", 1, (255,255,255))
            stoptext = mybusfont.render(route['name'], 1, (255,255,255))
            dest = mybusfont.render("Destination:", 1, (255,255,255))
            desttext = mybusfont.render(route['direction'],1,(255,255,255))
            pygame.draw.rect(self.screen,(5,5,60),(5 + (i*230), 45, 220, 400)) 
            self.screen.blit(stop, (5 + (i*230) + 5, 50))            
            self.screen.blit(stoptext, (5 + (i*230) + 5, 70))
            self.screen.blit(dest, (5 + (i*230) + 5, 95))
            self.screen.blit(desttext, (5 + (i*230) + 5, 115))
            
            for j, bus in enumerate(route['buses']):
                bustime = self.getBusTime(bus['time'])
                bustext = mybusfont.render("%s: %s" % (bus['route'], bustime), 1, (255,255,255))
                self.screen.blit(bustext, (5 + (i*230) + 5, (30 * j) + 150))
                
        updatetext = "Updated at %s on %s. Live bus data provided by TfL." % (
                    strftime("%H:%M"),
                    strftime("%a %d %b %Y") )
        updatelabel = pygame.font.SysFont(None,20).render(updatetext, 1, (255,255,255))
        self.screen.blit(updatelabel,(5,447))
        
        return self.screen
