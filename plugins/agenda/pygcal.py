from urllib2 import urlopen
import icalendar
import datetime
from pytz import timezone
import pytz

class PyGCal():
    """Class to parse iCal feed from Google calendar.
    
    Called by passing url of private iCal link.
    """
    
    cal = None
    rawevents = []
    
    def __init__(self, iCalURL):
        
        self.icalurl = iCalURL
        
        self.__loadcalendar()

            
        self.TIMEZONE =  timezone(self.cal.get("x-wr-timezone"))
        
        self.rawevents = self.__parse()
        
    def __loadcalendar(self):
        try:
            self.cal = icalendar.Calendar.from_ical(urlopen(self.icalurl).read())
        except:
            raise Exception("Error loading iCal")

    def __parse(self):
        
        events = []
        for component in self.cal.walk():
            event = {}
            if component.name == "VEVENT":
                if type(component.get("dtstart").dt) == datetime.date:
                    dtstart = datetime.datetime.combine(component.get("dtstart").dt, datetime.time(hour=0,tzinfo=self.TIMEZONE))
                    dtend = datetime.datetime.combine(component.get("dtend").dt, datetime.time(hour=0,tzinfo=self.TIMEZONE))
                    allday = True
                else:
                    dtstart = component.get("dtstart").dt.replace(tzinfo=pytz.utc).astimezone(self.TIMEZONE)
                    dtend = component.get("dtend").dt.replace(tzinfo=pytz.utc).astimezone(self.TIMEZONE)
                    allday = False
                
                event["start"] = dtstart
                event["end"] = dtend
                event["summary"] = str(component.get("summary"))
                event["description"] = str(component.get("description"))
                event["location"] = str(component.get("location"))
                event["allday"] = allday
                event["status"] = str(component.get("status"))
        
                events.append(event)
        
        return events
           
    def Update(self):
        """Reloads the calendar and repopulates the raw data.
        
        """
        self.__loadcalendar()
        self.__parse()

    def getUpcomingEvents(self, limit=0):
        """Returns list of upcoming events.
        
        Can be restricted by passing an integer value.
        
        e.g. getUpcomingEvents(2) returns the next 2 events
        """
        upcomingevents = []
        for event in self.rawevents:
            if event["end"] >= datetime.datetime.now(self.TIMEZONE):
                upcomingevents.append(event)

        sortevents = sorted(upcomingevents, key=lambda k: k['start'])  

        if limit==0:
            return sortevents
        else:
            try:
                return sortevents[:limit]
            except:
                return sortevents
                
    @property
    def Timezone(self):
        return self.TIMEZONE

