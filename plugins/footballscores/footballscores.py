'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import urllib2
import string
from BeautifulSoup import BeautifulSoup
import re
from datetime import datetime, time


class matchcommon(object):
    '''class for common functions for match classes.'''

    livescoreslink = ("http://www.bbc.co.uk/sport/shared/football/"
                      "live-scores/matches/{comp}/today")

    def getPage(self, url, sendresponse = False):
        page = None
        try:
            user_agent = ('Mozilla/5.0 (Windows; U; Windows NT 6.1; '
                          'en-US; rv:1.9.1.5) Gecko/20091102 Firefox')
            headers = { 'User-Agent' : user_agent }
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            page = response.read()
        except:
            pass
        
        if sendresponse:
            return response    
        else:
            return page

class FootballMatch(matchcommon):
    '''Class for getting details of individual football matches.
    Data is pulled from BBC live scores page.
    '''
    # self.accordionlink = "http://polling.bbc.co.uk/sport/shared/football/accordion/partial/collated"

    detailprefix =   ("http://www.bbc.co.uk/sport/football/live/"
                      "partial/{id}")

    def __init__(self, team, detailed = False, data = None):
        '''Creates an instance of the Match object.
        Must be created by passing the name of one team.
        
        data - User can also send data to the class e.g. if multiple instances
        of class are being run thereby saving http requests. Otherwise class 
        can handle request on its own.
        
        detailed - Do we want additional data (e.g. goal scorers, bookings)?
        '''
        self.detailed = detailed
        
        # Set the relevant urls
        self.detailedmatchpage = None
        self.scorelink = None
        
        # Boolean to notify user if there is a valid match
        self.matchfound = False
        
        # Which team am I following?
        self.myteam = team

        self.__resetMatch()
        
        # Let's try and load some data
        data = self.__loadData(data)
        
        # If our team is found or we have data
        if data:

            # Update the class properties
            self.__update(data)
            # No notifications for now
            self.goal = False
            self.statuschange = False
            self.newmatch = False

    def __getServerTime(self):

        headers = self.getPage("http://www.bbc.co.uk",True)
        datematch = re.compile(r'Date: (.*)')
        rawtime = datematch.search(str(headers.headers))
        if rawtime:
            servertime = datetime.strptime(rawtime.groups()[0].strip()[:-4],
                                           "%a, %d %b %Y %H:%M:%S")
            return servertime

        else:

            return None

    def __resetMatch(self):
        '''Clear all variables'''
        self.hometeam = None
        self.awayteam = None
        self.homescore = None
        self.awayscore = None  
        self.scorelink = None
        self.homescorers = None
        self.awayscorers = None
        self.homeyellowcards = None
        self.awayyellowcards = None
        self.homeredcards = None
        self.awayredcards = None
        self.competition = None
        self.matchtime = None
        self.status = None
        self.goal = False
        self.statuschange = False
        self.newmatch = False
        self.homebadge = None
        self.awaybadge = None


    def __findMatch(self):
        # Start with the default page so we can get list of active leagues
        raw =  BeautifulSoup(self.getPage(self.livescoreslink.format(comp="")))
        
        # Find the list of active leagues
        selection = raw.find("div", {"class": 
                                     "drop-down-filter live-scores-fixtures"})
        
        teamfound = False
        data = None
      
        # Loop throught the active leagues
        for option in selection.findAll("option"):
            
            # Build the link for that competition
            league = option.get("value")[12:]
            
            if league:
                scorelink = self.livescoreslink.format(comp=league)
            
                # Prepare to process page
                optionhtml = BeautifulSoup(self.getPage(scorelink))
                
                # We just want the live games...
                live = optionhtml.find("div", {"id": "matches-wrapper"})
                
                # Let's look for our team
                if live.find(text=self.myteam):
                    teamfound = True
                    self.scorelink = scorelink
                    self.competition = option.text.split("(")[0].strip()
                    data = live
                    break
        
        self.matchfound = teamfound
                    
        return data

    def __getScores(self, data, update = False):

        for match in data.findAll("tr", {"id": re.compile(r'^match-row')}):
            if match.find(text=self.myteam):

                self.hometeam = match.find("span", 
                                          {"class": "team-home"}).text
                
                self.awayteam = match.find("span", 
                                          {"class": "team-away"}).text

                linkrow = match.find("td", {"class": "match-link"})
                link = linkrow.find("a").get("href")
                self.matchlink = "http://www.bbc.co.uk%s" % (link)
        
                if match.get("class") == "fixture":
                    status = "Fixture"
                    matchtime = match.find("span", 
                                     {"class": 
                                     "elapsed-time"}).text.strip()[:5]

                elif match.get("class") == "report":
                    status = "FT"
                    matchtime = None

                elif ("%s" % 
                     (match.find("span", 
                     {"class": "elapsed-time"}).text.strip()) == "Half Time"):
                    status = "HT"
                    matchtime = None

                else:
                    status = "L"
                    matchtime = match.find("span", 
                                     {"class": "elapsed-time"}).text.strip()
        
                matchid = match.get("id")[10:]
        
                score = match.find("span", 
                                 {"class": "score"}).text.strip().split(" - ")
                
                try:
                    homescore = int(score[0].strip())
                    awayscore = int(score[1].strip())
                
                except:
                    homescore = 0
                    awayscore = 0

                self.statuschange = False
                self.newmatch = False
                self.goal=False

                if update:

                    if not status == self.status:
                        self.statuschange = True
                    
                    if not matchid == self.matchid:
                        self.newmatch = True

                    if not (homescore == self.homescore and
                            awayscore == self.awayscore):
                        self.goal = True

                self.status = status
                self.matchtime = matchtime
                self.matchid = matchid
                self.homescore = homescore
                self.awayscore = awayscore

        
    def __update(self, data = None):
 
        self.__getScores(data)
        
        if self.detailed:
            self.__getDetails()

    def __loadData(self, data = None):

        self.matchfound = False

        if data:
            if data.find(text=self.myteam):
                self.matchfound = True
            else:
                data = None

        if not data and self.scorelink:
            scorehtml = BeautifulSoup(self.getPage(self.scorelink))
            data = scorehtml.find("div", {"id": "matches-wrapper"})
            if data.find(text=self.myteam):
                self.matchfound = True
            else:
                data = None

        if not data:
            data = self.__findMatch()

        if not data:
            self.__resetMatch()
       
        return data
    
    def Update(self, data = None):

        data = self.__loadData(data)

        if data:
            self.__getScores(data, update = True)

        if self.detailed:
            self.__getDetails()
    
        
    # def __checkMatch(self):
            
    #     # Status change (half-time etc.)
    #     if not match.find("span", 
    #                      {"class": 
    #                      re.compile(r"\bstatus\b")}).find(
    #                                               "abbr").text == self.status:
    #         self.statuschange = True
    #     else:
    #         self.statuschange = False
        
    #     # New match (i.e. different opponent)    
    #     if not (
    #                 match.find("span", 
    #                           {"class": "home-team"}).text == self.hometeam or
    #                 match.find("span", 
    #                           {"class": "away-team"}).text == self.awayteam):
    #         self.newmatch = True
    #     else:
    #         self.newmatch = False
        
    #     # Goooooooooooaaaaaaaaalllllllllllll!  
        
    #     score = match.find("span", {"class": "result"}).text.split(" ")
    #     try:
    #         homescore = int(score[0].strip())
    #         awayscore = int(score[2].strip())
    #     except:
    #         homescore = 0
    #         awayscore = 0
          
    #     if not (
    #                 homescore == self.homescore or
    #                 awayscore == self.awayscore
    #             ):
    #         self.goal = True
    #     else:
    #         self.goal = False
        
    #     self.__update()

    def __getDetails(self):
        
        if self.matchid:
            # Prepare bautiful soup to scrape match page
            bs =  BeautifulSoup(self.getPage(self.detailprefix.format(
                                             id=self.matchid)))

                # Let's get the home and away team detail sections
            try:
                incidents = bs.find("table", 
                                   {"class": "incidents-table"}).findAll("tr")
            except:
                incidents = None

            # Get incidents
            # This populates variables with details of scorers and bookings
            # Incidents are stored in a list of tuples: format is:
            # [(Player Name, [times of incidents])]
            hsc = []
            asc = []
            hyc = []
            ayc = []
            hrc = []
            arc = []
            
            if incidents:

                self.__goalscorers = []
                self.__yellowcards = []
                self.__redcards = []

                for incident in incidents:
                    i = incident.find("td", 
                                     {"class": 
                                     re.compile(r"\bincident-type \b")})
                    if i:
                        h = incident.find("td", 
                                         {"class": 
                                         "incident-player-home"}).text.strip()
                        
                        a = incident.find("td", 
                                         {"class": 
                                         "incident-player-away"}).text.strip()
                        
                        t = incident.find("td", 
                                         {"class": 
                                         "incident-time"}).text.strip()

                        if "goal" in i.get("class"):     
                            if h:
                                hsc = self.__addIncident(hsc, h, t)
                                self.__goalscorers.append((self.hometeam,
                                                           h, t)) 
                            else:
                                asc = self.__addIncident(asc, a, t)
                                self.__goalscorers.append((self.awayteam,
                                                           a, t))
                        
                        elif "yellow-card" in i.get("class"):
                            if h:
                                hyc = self.__addIncident(hyc, h, t)
                                self.__yellowcards.append((self.hometeam,
                                                           h, t)) 
                            else:
                                ayc = self.__addIncident(ayc, a, t)
                                self.__yellowcards.append((self.awayteam,
                                                           a, t))

                        elif "red-card" in i.get("class"):
                            if h:
                                hrc = self.__addIncident(hrc, h, t)
                                self.__redcards.append((self.hometeam,
                                                           h, t)) 
                            else:
                                arc = self.__addIncident(arc, a, t)
                                self.__redcards.append((self.awayteam,
                                                           a, t))
                                    
            self.homescorers = hsc
            self.awayscorers = asc
            self.homeyellowcards = hyc
            self.awayyellowcards = ayc
            self.homeredcards = hrc
            self.awayredcards = arc

    def __addIncident(self, incidentlist, player, incidenttime):
        '''method to add incident to list variable'''
        found = False
        for incident in incidentlist:
            if incident[0] == player:
                incident[1].append(incidenttime)
                found = True
                break

        if not found:
            incidentlist.append((player, [incidenttime]))

        return incidentlist

    def formatIncidents(self, incidentlist):
        '''Incidents are in the following format:
        List:
          [Tuple:
            (Player name, [list of times of incidents])]

        This function converts the list into a string.
        '''
        temp = []
        for incident in incidentlist:
            temp.append("%s (%s)" % (incident[0],
                                     ", ".join(incident[1])))

        return ", ".join(temp)

    def getTeamBadges(self):
        found = False
        
        if self.matchlink:
            linkpage = BeautifulSoup(self.getPage(self.matchlink))
            badges = linkpage.findAll("div", {"class": "team-badge"})
            if badges:
                self.homebadge = badges[0].find("img").get("src")
                self.awaybadge = badges[1].find("img").get("src")
                found = True

        return found

    
    def __nonzero__(self):

        return self.matchfound

    def __repr__(self):

        return "FootballMatch(\'%s\', detailed=%s)" % (self.myteam,
                                                          self.detailed)

    
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
        return self.competition
    
    @property        
    def Status(self):
        """Returns the status of the match
        
        e.g. "L", "HT", "FT"
        
        """
        if self.status == "Fixture":
            return self.matchtime
        else:
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
    def HomeYellowCards(self):
        """Returns list of players receiving yellow cards for home team
        
        """
        return self.homeyellowcards
    
    @property    
    def AwayYellowCards(self):
        """Returns list of players receiving yellow cards for away team
        
        """
        return self.awayyellowcards      
    
    @property    
    def HomeRedCards(self):
        """Returns list of players sent off for home team
        
        """
        return self.homeredcards

    @property    
    def AwayRedCards(self):
        """Returns list of players sent off for away team
        
        """
        return self.awayredcards

    @property
    def LastGoalScorer(self):
        if self.detailed:
            if self.__goalscorers:
                return self.__goalscorers[-1]
            else:
                return None
        else:
            return None

    @property
    def LastYellowCard(self):
        if self.detailed:
            if self.__yellowcards:
                return self.__yellowcards[-1]
            else:
                return None
        else:
            return None

    @property
    def LastRedCard(self):
        if self.detailed:
            if self.__redcards:
                return self.__redcards[-1]
            else:
                return None
        else:
            return None

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
        if self.status=="L" and self.matchtime is not None:
            return self.matchtime
        else:
            return self.Status
        
    def __str__(self):
        """Returns short formatted summary of match.
        
        e.g. "Arsenal 1-1 Chelsea (L)"
        
        """
        if self.matchfound:
        
            return "%s %s-%s %s (%s)" % (
                                          self.hometeam,
                                          self.homescore,
                                          self.awayscore,
                                          self.awayteam,
                                          self.Status
                                          )
        else:

            return "%s are not playing today." % (self.myteam)
    @property
    def PrintDetail(self):
        """Returns detailed summary of match (if available).
        
        e.g. "(L) Arsenal 1-1 Chelsea (Arsenal: Wilshere 10', 
              Chelsea: Lampard 48')"
        """
        if self.detailed:
            hscore = False
            scorerstring = ""
            
            if self.homescorers or self.awayscorers:
                scorerstring = " ("
                if self.homescorers:
                    hscore = True
                    scorerstring += "%s: %s" % (self.hometeam,
                                                self.formatIncidents(self.homescorers))

                            
                if self.awayscorers:
                    if hscore:
                        scorerstring += " - "
                    scorerstring += "%s: %s" % (self.awayteam,
                                                self.formatIncidents(self.awayscorers))

                scorerstring += ")"
                
            return "(%s) %s %s-%s %s%s" % (
                                            self.MatchTime,
                                            self.hometeam,
                                            self.homescore,
                                            self.awayscore,
                                            self.awayteam,
                                            scorerstring
                                            )
        else:
            return self.__str__()

    @property
    def TimeToKickOff(self):
        '''Returns a timedelta object for the time until the match kicks off.

        Returns None if unable to parse match time or if match in progress.

        Should be unaffected by timezones as it gets current time from bbc
        server which *should* be the same timezone as matches shown.
        '''
        if self.status == "Fixture":
            try:
                koh = int(self.matchtime[:2])
                kom = int(self.matchtime[3:5])
                kickoff = datetime.combine(
                            datetime.now().date(),
                            time(koh, kom, 0))
                timetokickoff = kickoff - self.__getServerTime()
            except Exception, e:
                timetokickoff = None
            finally:
                pass
        else:
            timetokickoff = None

        return timetokickoff

class League(matchcommon):
    '''Get summary of matches for a given league.

    NOTE: this may need to be updated as currently uses the accordion
    source data whereas main Match module uses more complete source.
    '''
    
    accordionlink = ("http://polling.bbc.co.uk/sport/shared/football/"
                     "accordion/partial/collated")

    def __init__(self, league, detailed=False):

        self.__leaguematches = self.__getMatches(league,detailed=detailed)
        self.__leagueid = league
        self.__leaguename = self.__getLeagueName(league)
        self.__detailed = detailed

    def __getData(self, league):

        scorelink = self.livescoreslink.format(comp=league)
    
        # Prepare to process page
        optionhtml = BeautifulSoup(self.getPage(scorelink))
        
        # We just want the live games...
        data = optionhtml.find("div", {"id": "matches-wrapper"})

        return data

    def __getLeagueName(self, league):

        raw =  BeautifulSoup(self.getPage(self.livescoreslink.format(comp=league)))
        
        # Find the list of active leagues
        selection = raw.find("div", {"class": 
                                     "drop-down-filter live-scores-fixtures"})
      
        selectedleague = selection.find("option", {"selected": "selected"})
        leaguename = selectedleague.text.split("(")[0].strip()
        
        return leaguename


    @staticmethod
    def getLeagues():
        leagues = []
        # raw =  BeautifulSoup(self.getPage(self.accordionlink))
        # # Loop through all the competitions being played today
        # for option in raw.findAll("option"):
        #     league = {}
        #     league["name"] = option.text
        #     league["id"] = option.get("value")
        #     leagues.append(league)
            
        # return leagues
        livescoreslink = matchcommon().livescoreslink

        # Start with the default page so we can get list of active leagues
        raw =  BeautifulSoup(matchcommon().getPage(livescoreslink.format(comp="")))
        
        # Find the list of active leagues
        selection = raw.find("div", {"class": 
                                     "drop-down-filter live-scores-fixtures"})
      
        # Loop throught the active leagues
        for option in selection.findAll("option"):
            
            # Build the link for that competition
            # league = option.get("value")[12:]
            league = {}
            league["name"] = option.text.split("(")[0].strip()
            league["id"] = option.get("value")[12:]
            if league["id"]:
                leagues.append(league)

        return leagues
        
    def __getMatches(self, league, detailed=False):

        data = self.__getData(league)

        matches = []

        rawmatches = data.findAll("tr", {"id": re.compile(r'^match-row')})

        if rawmatches:

            for match in rawmatches:
                team = match.find("span", {"class": "team-home"}).text
                m = FootballMatch(team, detailed=detailed, data=data)
                matches.append(m)

        return matches

    def __repr__(self):
        return "League(\'%s\', detailed=%s)" % (self.__leagueid,
                                                self.__detailed)

    def __str__(self):
        if self.__leaguematches:
            if len(self.__leaguematches) == 1:
                matches = "(1 match)"
            else:
                matches = "(%d matches)" % (len(self.__leaguematches))
            return "%s %s" % (self.__leaguename, matches)
        else:
            return None

    def __nonzero__(self):
        return bool(self.__leaguematches)

    def Update(self):

        if self.__leaguematches:
            data = self.__getData(self.__leagueid)
            for match in self.__leaguematches:
                match.Update(data=data)

    @property 
    def LeagueMatches(self):
        return self.__leaguematches

    @property
    def LeagueName(self):
        return self.__leaguename

    @property 
    def LeagueID(self):
        return self.__leagueid

class LeagueTable(matchcommon):
    '''class to convert BBC league table format into python list/dict.'''

    leaguebase = "http://www.bbc.co.uk/sport/football/tables"
    leaguemethod = "filter"
    
    def __init__(self):
        #self.availableLeague = self.getLeagues()
        pass
    
    def getLeagues(self):
        '''method for getting list of available leagues'''

        leaguelist = []
        raw = BeautifulSoup(self.getPage(self.leaguebase))
        form = raw.find("div", {"class": "drop-down-filter",
                                "id": "filter-fixtures-no-js"})
        self.leaguemethod = form.find("select").get("name")
        leagues = form.findAll("option")
        for league in leagues:
            l = {}
            if league.get("value") <> "":
                l["name"] = league.text
                l["id"] = league.get("value")
                leaguelist.append(l)
        return leaguelist
        
    def getLeagueTable(self, leagueid):
        '''method for creating league table of selected league.'''

        class LeagueTableTeam(object):

            def __init__(self, team):

                f = team.find
                self.name = f("td", {"class": "team-name"}).text
                self.position = int(f("span", 
                                     {"class": "position-number"}).text)
                self.played = int(f("td", {"class": "played"}).text)
                self.won = int(f("td", {"class": "won"}).text)
                self.drawn = int(f("td", {"class": "drawn"}).text)
                self.lost = int(f("td", {"class": "lost"}).text)            
                self.goalsfor = int(f("td", {"class": "for"}).text)
                self.goalsagainst = int(f("td", {"class": "against"}).text) 
                self.goaldifference = int(f("td", 
                                           {"class": "goal-difference"}).text)
                self.points = int(f("td", {"class": "points"}).text)  
                
                try:
                    lastgames = f("td", {"class": "last-10-games"})
                    lg = []
                    for game in lastgames.findAll("li"):
                        g = {}
                        g["result"] = game.get("class")
                        g["score"] = game.get("data-result")
                        g["opponent"] = game.get("data-against")
                        g["date"] = game.get("data-date")
                        g["summary"] = game.get("title")
                        lg.append(g)
                    self.lasttengames = lg
                
                except:
                    self.lasttengames = []

                def __repr__(self):
                    return "<LeagueTableTeam object - %s>" % self.name

            def __str__(self):
                return "%d %s %d" % (self.position,
                                     self.name,
                                     self.points)


        leaguetable = []
        
        leaguepage = "%s?%s=%s" % (self.leaguebase,
                                   self.leaguemethod,
                                   leagueid)
                                   
        raw = BeautifulSoup(self.getPage(leaguepage))
        
        table = raw.find("div", {"class": "league-table full-table-wide"})
        
        for team in table.findAll("tr", {"id": re.compile(r'team')}):
            t = LeagueTableTeam(team)
            leaguetable.append(t)
            
        return leaguetable

class Teams(matchcommon):

    def getTeams(self):
        # Start with the default page so we can get list of active leagues
        raw =  BeautifulSoup(self.getPage(self.livescoreslink.format(comp="")))
        
        # Find the list of active leagues
        selection = raw.find("div", {"class": 
                                     "drop-down-filter live-scores-fixtures"})
        
        teamlist = []
      
        # Loop throught the active leagues
        for option in selection.findAll("option"):
            
            # Build the link for that competition
            league = option.get("value")[12:]
            
            if league:
                scorelink = self.livescoreslink.format(comp=league)
            
                # Prepare to process page
                optionhtml = BeautifulSoup(self.getPage(scorelink))
                
                # We just want the live games...
                live = optionhtml.find("div", {"id": "matches-wrapper"})

                for match in live.findAll("tr", {"id": re.compile(r'^match-row')}):

                    teamlist.append(match.find("span", 
                                              {"class": "team-home"}).text)
                    
                    teamlist.append(match.find("span", 
                                              {"class": "team-away"}).text)
                

        teamlist = sorted(teamlist)
                    
        return teamlist