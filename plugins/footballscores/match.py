import urllib2
import string
from BeautifulSoup import BeautifulSoup
import re
import simplejson as json
from datetime import datetime

class Match():
    # Class for getting details of football match from BBC data
    # Data is pulled from JSON feed
    # Additional data is scraped from game page on BBC sports page

    def __init__(self, team, json = None, detailed = False):
        # user can send json data to the class e.g. if multiple instances of class are being run
        # thereby saving requests. Otherwise class can handle request on its own.
        
        # Do we want additional data (e.g. urls for club badges, goal scorers)?
        self.detailed = detailed
        
        # Set the relevant urls
        self.footballjsonlink = "http://news.bbc.co.uk//sport/hi/english/static/football/statistics/collated/live_scores_summary_all.json"
        self.matchprefix = "http://www.bbc.co.uk/sport/0/football/"
        self.detailedmatchpage = None
        
        # Boolean to notify user if there is a valid match
        self.matchfound = False
        
        # Which team am I following?
        self.myteam = team
        
        # Get the data
        self.loadData(json)
        
        # If our team is found...
        if self.matchfound:
            # Update the class properties
            self.__update__(self.match, self.competition)
            # No notifications for now
            self.goal = False
            self.statuschange = False
            self.newmatch = False
        
        
    def __update__(self, match, competition):
        self.competition = competition
        self.competitionname = competition['name']
        self.hometeam = match['homeTeam']['name']
        self.awayteam =  match['awayTeam']['name']
        self.homescore =  match['homeTeam']['score']
        self.awayscore =  match['awayTeam']['score']
        self.status = match['statusCode']
        
        if self.awayteam == self.myteam:
            try:
                self.teamurl = match['awayTeam']['url']
            except:
                self.teamurl = None
        else:
            try:
                self.teamurl = match['homeTeam']['url']
            except:
                self.teamurl = None
        
        if self.detailed:
            self.getDetails(match['url'])

    def loadData(self, json):

        if json:
            mymatches = json
        else:
            mymatches = self.getJSONFixtures()
        
        if not self.jsonerror:
        
            self.matchfound = False
            
            for competition in mymatches['competition']:
                compname = competition['name']
                for match in competition['match']:
                    if (
                          match['homeTeam']['name'] == self.myteam or 
                          match['awayTeam']['name'] == self.myteam
                        ):
                        self.matchfound = True
                        self.match = match
                        self.competition = competition
                        break
    
    def Update(self, json = None):
        self.loadData(json)
        self.__checkMatch__(self.match, self.competition)
    
        
    def __checkMatch__(self, match, competition):
        if not self.jsonerror:
            # Set some notification properties...
            
            # Status change (half-time etc.)
            if not match['statusCode'] == self.status:
                self.statuschange = True
            else:
                self.statuschange = False
            
            # New match (i.e. different opponent)    
            if not (
                        match['homeTeam']['name'] == self.hometeam or
                        match['awayTeam']['name'] == self.awayteam or
                        competion == self.competition
                    ):
                self.newmatch = True
            else:
                self.newmatch = False
            
            # Goooooooooooaaaaaaaaalllllllllllll!    
            if not (
                        match['homeTeam']['score'] == self.homescore or
                        match['awayTeam']['score'] == self.awayscore
                    ):
                self.goal = True
            else:
                self.goal = False
            
            self.__update__(match, competition)

    def getPage(self, url):
        page = None
        try:
            user_agent = 'Mozilla/5 (Solaris 10) Gecko'
            headers = { 'User-Agent' : user_agent }
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            page = response.read()
        except:
            pass
            
        return page

    def getDetails(self, matchurl):
        
        if not self.detailedmatchpage:
            
            # Try to find detailed web page for additional info
            
            # PAGE 1: Sometimes the json feed contains hints...
            # For some reason the url in the json feed gives a 404
            # BUT the number before the .stm extension is relevant...
            self.matchurl = self.matchprefix + re.search('[^/]*(?=\.[^.]+($|\?))', matchurl).group(0)
            page = self.getPage(self.matchurl)
            if page:
                self.detailedmatchpage = self.matchurl
            
            
            # If that didn't work, let's use the team link in the json feed and
            # scrape that for a live match link
            if not page:
                if not self.teamurl is None:
                    teampage = BeautifulSoup(self.getPage(self.teamurl))
                    if teampage:
                        try:
                            liveteam = teampage.find("div", {"class": "accordion-container live-today"})
                            link = liveteam.find("a")
                            gamepage = "http://www.bbc.co.uk%s" % (link.get("href"))
                        except:
                            gamepage = None
                    if gamepage:
                        page = self.getPage(gamepage)
                        if page:
                            self.detailedmatchpage = gamepage
            
            # If we've still not found a page, then let's clear out the variables
            if not page:
                self.homescorers = []
                self.awayscorers = []
                self.homebadge = None
                self.awaybadge = None
                self.matchtime = None
                self.detailedmatchpage = None               
        
        
        else:
            # Prepare bautiful soup to scrape match page
            bs =  BeautifulSoup(self.getPage(self.detailedmatchpage))
            
            # Let's get the home and away team detail sections
            match = bs.find("div", {"id": "match-overview"})
            homedetail = match.find("div", {"id": "home-team"})
            awaydetail = match.find("div", {"id": "away-team"})
            matchdetail = match.find("div", {"id": "match-details"})
            match = None
            
            # Get urls of team badges
            try:
                self.homebadge = homedetail.find("img")['src']
                self.awaybadge = awaydetail.find("img")['src']
            except:
                self.homebadge = None
                self.awaybadge = None
            
            # Get scorers
            # Class "scorer-list" only exists when there are goalscorers.
            # If the class doesn't exist the "findAll" function will fail
            hscorers = []
            try:
                scorers = homedetail.find("p", {"class": re.compile(r"\bscorer-list\b")}).findAll("span")
                for scorer in scorers:
                    # tidy up the goalscorer string and add to our list
                    hscorers.append(scorer.string.replace("&prime;","'").lstrip().rstrip())
            except:
                pass
                
            ascorers = []
            try:
                scorers = awaydetail.find("p", {"class": re.compile(r"\bscorer-list\b")}).findAll("span")
                for scorer in scorers:
                    # tidy up the goalscorer string and add to our list
                    ascorers.append(scorer.string.replace("&prime;","'").lstrip().rstrip())
            except:
                pass
                
            self.homescorers = hscorers
            self.awayscorers = ascorers
        
            # Get match time
            self.matchtime = None
            try:
                self.matchtime = matchdetail.find("span", {"class": "match-time"}).string
            except:
                pass
        

    def getJSONFixtures(self):
        jsonresult = self.getPage(self.footballjsonlink)
        fixtures = ""
      
        if jsonresult:
      
            try:
                fixtures = json.loads(jsonresult)
                self.jsonerror = False
                
            except:  
          
                try:
                    # BBC json feed needs a bit of tidying up to work here    
                    if jsonresult[0:4] == "<!--":
                        a = string.find(jsonresult, "-->")
                        stra = jsonresult[a+3:]
                        if "<!--" in stra:
                            a = string.find(stra, "<!--")
                            strb = stra[0:a] + "}"
                            fixtures = json.loads(strb)
                            self.jsonerror = False
                 
                except:
                    self.jsonerror = True   
          
        return fixtures        
    
    # Neater functions to return data:
    
    @property        
    def HomeTeam(self):
        """Returns string of the home team's name
        
        """
        return self.hometeam
            
    @property
    def AwayTeam(self):
        """Returns string of the away team's name
        
        """
        return self.awayteam
    
    @property        
    def HomeScore(self):
        """Returns the number of goals scored by the home team
        
        """
        return self.homescore
    
    @property        
    def AwayScore(self):
        """Returns the number of goals scored by the away team
        
        """
        return self.awayscore
    
    @property        
    def Competition(self):
        """Returns the name of the competition to which the match belongs
        
        e.g. "Premier League", "FA Cup" etc
        
        """
        return self.competitionname
    
    @property        
    def Status(self):
        """Returns the status of the match
        
        e.g. "L", "HT", "FT"
        
        """
        return self.status
    
    @property        
    def Goal(self):
        """Boolean. Returns True if score has changed since last update
        
        """
        return self.goal
    
    @property        
    def StatusChanged(self):
        """Boolean. Returns True if status has changed since last update
        
        e.g. Match started, half-time started etc
        
        """
        return self.statuschange

    @property
    def NewMatch(self):
        """Boolean. Returns True if the match found since last update
        
        """
        return self.newmatch

    @property
    def MatchFound(self):
        """Boolean. Returns True if a match is found in JSON feed
        
        """
        return self.matchfound
        
    @property
    def JSONError(self):
        """Boolean. Returns True if class unable to parse data from BBC
        
        """
        return self.jsonerror
        
    @property
    def HomeBadge(self):
        """Returns link to image for home team's badge
        
        """
        return self.homebadge
    
    @property    
    def AwayBadge(self):
        """Returns link to image for away team's badge
        
        """
        return self.awaybadge
    
    @property    
    def HomeScorers(self):
        """Returns list of goalscorers for home team
        
        """
        return self.homescorers
    
    @property    
    def AwayScorers(self):
        """Returns list of goalscorers for away team
        
        """
        return self.awayscorers
        
    @property
    def MatchDate(self):
        """Returns date of match i.e. today's date
        
        """
        d = datetime.now()
        datestring = "%s %d %s" % (
                                        d.strftime("%A"),
                                        d.day,
                                        d.strftime("%B %Y")
                                      )
        return datestring
        
    @property
    def MatchTime(self):
        """If detailed info available, returns match time in minutes.
        
        If not, returns Status.
        
        """
        if self.status=="L" and not self.matchtime == None:
            return "%s mins" % (self.matchtime)
        else:
            return self.status
        
    def __str__(self):
        """Returns short formatted summary of match.
        
        e.g. "Arsenal 1-1 Chelsea (L)"
        
        """
        return "%s %s-%s %s (%s)" % (
                                      self.hometeam,
                                      self.homescore,
                                      self.awayscore,
                                      self.awayteam,
                                      self.status
                                      )
    @property
    def PrintDetail(self):
        """Returns detailed summary of match (if available).
        
        e.g. "(L) Arsenal 1-1 Chelsea (Arsenal: Wilshere 10', Chelsea: Lampard 48')"
        
        """
        if self.detailed:
            hscore = False
            scorerstring = ""
            
            if len(self.homescorers) > 0 or len(self.awayscorers) > 0:
                scorerstring = " ("
                if len(self.homescorers) > 0:
                    hscore = True
                    scorerstring += "%s:" % self.hometeam
                    for i, scorer in enumerate(self.homescorers):
                        scorerstring += " %s" % scorer
                        if i < (len(self.homescorers) - 1):
                            scorerstring += ","
                            
                if len(self.awayscorers) > 0:
                    if hscore:
                        scorerstring += " - "
                    scorerstring += "%s:" % self.awayteam
                    for i, scorer in enumerate(self.awayscorers):
                        scorerstring += " %s" % scorer
                        if i < (len(self.awayscorers) - 1):
                            scorerstring += ","
                scorerstring += ")"
                
            return "(%s) %s %s-%s %s%s" % (
                                            self.status,
                                            self.hometeam,
                                            self.homescore,
                                            self.awayscore,
                                            self.awayteam,
                                            scorerstring
                                            )
        else:
            return self.__str__()
