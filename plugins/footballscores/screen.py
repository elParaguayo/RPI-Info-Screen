from displayscreen import PiInfoScreen
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from footballscores import FootballMatch

            
class myScreen(PiInfoScreen):
    
    refreshtime = 60
    displaytime = 5
    pluginname = "FootballScores"
    plugininfo = "Displays live football scores for a chosen team"
    supportedsizes = [ (320, 240) ]
    
    def setPluginVariables(self):
        self.myTeam = self.pluginConfig["Config"]["myteam"]
        self.myMatch = FootballMatch("Liverpool",detailed=True)
        self.myMatch.getTeamBadges()

    def showScreen(self):
        self.surface.fill([0,0,0])
        scorefont = pygame.font.SysFont("freesans", 40)
        teamfont = pygame.font.SysFont("freesans", 25)
        self.myMatch.Update()
        
        # if self.myMatch.JSONError:
        #     # Error parsing data
        #     errortext = pygame.font.SysFont("freesans",30).render("Error loading data.",1,(255,255,255))
        #     errorrect = errortext.get_rect()
        #     errorrect.centerx = self.surface.get_rect().centerx
        #     errorrect.centery = self.surface.get_rect().centery
        #     self.surface.blit(errortext,errorrect)
   
        if self.myMatch:
            
            # Draw competition name
            comptext = pygame.font.SysFont("freesans",15).render(self.myMatch.Competition,1,(255,255,255))
            comprect = comptext.get_rect()
            comprect.centerx = self.surface.get_rect().centerx
            self.surface.blit(comptext,(comprect[0],5))
            
            # Add today's date
            datetext = pygame.font.SysFont("freesans",10).render(self.myMatch.MatchDate,1,(255,255,255))
            daterect = datetext.get_rect()
            daterect.centerx = comprect.centerx
            self.surface.blit(datetext, (daterect[0],20))
            
            # Draw team names
            teamrect = pygame.Rect(0,0,90,40)
            hometeam = self.render_textrect(self.myMatch.HomeTeam, teamfont, teamrect, 
                                            (255,255,255), (0,0,0), 2, shrink=True, 
                                            SysFont="freesans", MaxFont=25, MinFont=5, vjustification=1)
            awayteam = self.render_textrect(self.myMatch.AwayTeam, teamfont, teamrect, 
                                            (255,255,255), (0,0,0), 0, shrink=True, 
                                            SysFont="freesans", MaxFont=25, MinFont=5, vjustification=1)
            self.surface.blit(hometeam, (10, 80))
            self.surface.blit(awayteam, (220, 80))
            
            # Draw scores
            score = scorefont.render("%s-%s" % (self.myMatch.HomeScore, self.myMatch.AwayScore),1,(255,255,255))
            scorerect = score.get_rect()
            scorerect.centerx = self.surface.get_rect().centerx
            scorerect.y = 80
            self.surface.blit(score,scorerect)
            
            # Draw match status
            status = pygame.font.SysFont("freesans",10).render("(%s)" % (self.myMatch.MatchTime), 1, (255,255,255))
            statusrect = status.get_rect()
            statusrect.centerx=scorerect.centerx
            self.surface.blit(status,(statusrect[0],130))
                
            # Display team badges
            # Home...
            if self.myMatch.HomeBadge:
                homebadge = pygame.transform.scale(self.LoadImageFromUrl(self.myMatch.HomeBadge),(30,30))
                self.surface.blit(homebadge, (35, 45))
            
            # ...and Away
            if self.myMatch.AwayBadge:
                awaybadge = pygame.transform.scale(self.LoadImageFromUrl(self.myMatch.AwayBadge),(30,30))
                self.surface.blit(awaybadge, (255, 45))            
            
            
            # Display scorers
            scorerrect = pygame.Rect(0,0,90,120)
            scorerfont = teamfont = pygame.font.SysFont("freesans", 12)
            
            # Home...
            if self.myMatch.HomeScorers:
                hscorers = self.myMatch.formatIncidents(self.myMatch.HomeScorers)
                hscorerstext = self.render_textrect(hscorers, scorerfont, scorerrect, (255,255,255), (0,0,0), 1)
                self.surface.blit(hscorerstext, (10,110))
            
            # ...and Away
            if self.myMatch.AwayScorers:
                ascorers = self.myMatch.formatIncidents(self.myMatch.AwayScorers)
                ascorerstext = self.render_textrect(ascorers, scorerfont, scorerrect, (255,255,255), (0,0,0), 1)
                self.surface.blit(ascorerstext, (220,110))        
        else:
            # Match not found so team aren't playing today
            errortext = pygame.font.SysFont("freesans",15).render("%s are not playing today." % (self.myTeam),1,(255,255,255))
            errorrect = errortext.get_rect()
            errorrect.centerx = self.surface.get_rect().centerx
            errorrect.centery = self.surface.get_rect().centery
            self.surface.blit(errortext,errorrect)
            
        # Scale our surface to the required screensize before sending back
        scaled = pygame.transform.scale(self.surface,self.screensize)
        self.screen.blit(scaled,(0,0))
        
        return self.screen
