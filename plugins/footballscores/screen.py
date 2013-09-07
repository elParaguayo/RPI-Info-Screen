from displayscreen import PiInfoScreen
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from match import Match

            
class myScreen(PiInfoScreen):
    
    refreshtime = 60
    displaytime = 5
    pluginname = "FootballScores"
    plugininfo = "Displays live football scores for a chosen team"
    
    def setPluginVariables(self):
        print self.pluginConfig
        self.myTeam = self.pluginConfig["Config"]["myteam"]
        self.myMatch = None

    def showScreen(self):
        self.screen.fill([0,0,0])
        matchfound = False
        scorefont = pygame.font.SysFont("freesans", 80)
        teamfont = pygame.font.SysFont("freesans", 50)
        self.myMatch=Match(self.myTeam,detailed=True)
        
        if self.myMatch.JSONError:
            # Error parsing data
            errortext = pygame.font.SysFont("freesans",30).render("Error loading data.",1,(255,255,255))
            errorrect = errortext.get_rect()
            errorrect.centerx = self.screen.get_rect().centerx
            errorrect.centery = self.screen.get_rect().centery
            self.screen.blit(errortext,errorrect)
   
        elif self.myMatch.MatchFound:
            
            # Draw competition name
            comptext = pygame.font.SysFont("freesans",30).render(self.myMatch.Competition,1,(255,255,255))
            comprect = comptext.get_rect()
            comprect.centerx = self.screen.get_rect().centerx
            self.screen.blit(comptext,(comprect[0],20))
            
            # Add today's date
            datetext = pygame.font.SysFont("freesans",20).render(self.myMatch.MatchDate,1,(255,255,255))
            daterect = datetext.get_rect()
            daterect.centerx = comprect.centerx
            self.screen.blit(datetext, (daterect[0],60))
            
            # Draw team names
            teamrect = pygame.Rect(0,0,200,80)
            hometeam = self.render_textrect(self.myMatch.HomeTeam, teamfont, teamrect, (255,255,255), (0,0,0), 2)
            awayteam = self.render_textrect(self.myMatch.AwayTeam, teamfont, teamrect, (255,255,255), (0,0,0), 0)
            self.screen.blit(hometeam, (45, 200))
            self.screen.blit(awayteam, (445, 200))
            
            # Draw scores
            score = scorefont.render("%s-%s" % (self.myMatch.HomeScore, self.myMatch.AwayScore),1,(255,255,255))
            scorerect = score.get_rect()
            scorerect.centerx = self.screen.get_rect().centerx
            scorerect.centery = self.screen.get_rect().centery
            self.screen.blit(score,scorerect)
            
            # Draw match status
            status = pygame.font.SysFont("freesans",20).render("(%s)" % (self.myMatch.MatchTime), 1, (255,255,255))
            statusrect = status.get_rect()
            statusrect.centerx=scorerect.centerx
            self.screen.blit(status,(statusrect[0],275))
                
            # Display team badges
            # Home...
            if self.myMatch.HomeBadge:
                homebadge = pygame.transform.scale(self.LoadImageFromUrl(self.myMatch.HomeBadge),(66,66))
                self.screen.blit(homebadge, (112, 120))
            
            # ...and Away
            if self.myMatch.AwayBadge:
                awaybadge = pygame.transform.scale(self.LoadImageFromUrl(self.myMatch.AwayBadge),(66,66))
                self.screen.blit(awaybadge, (512, 120))            
            
            
            # Display scorers
            scorerrect = pygame.Rect(0,0,200,150)
            scorerfont = teamfont = pygame.font.SysFont("freesans", 25)
            
            # Home...
            if self.myMatch.HomeScorers:
                hscorers = "\n".join(self.myMatch.HomeScorers)
                hscorerstext = self.render_textrect(hscorers, scorerfont, scorerrect, (255,255,255), (0,0,0), 1)
                self.screen.blit(hscorerstext, (45,275))
            
            # ...and Away
            if self.myMatch.AwayScorers:
                ascorers = "\n".join(self.myMatch.AwayScorers)
                ascorerstext = self.render_textrect(ascorers, scorerfont, scorerrect, (255,255,255), (0,0,0), 1)
                self.screen.blit(ascorerstext, (445,275))        
        else:
            # Match not found so team aren't playing today
            errortext = pygame.font.SysFont("freesans",30).render("%s are not playing today." % (self.myTeam),1,(255,255,255))
            errorrect = errortext.get_rect()
            errorrect.centerx = self.screen.get_rect().centerx
            errorrect.centery = self.screen.get_rect().centery
            self.screen.blit(errortext,errorrect)
            
                
        return self.screen
