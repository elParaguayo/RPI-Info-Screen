# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from pylms.server import Server
from pylms.player import Player
from displayscreen import PiInfoScreen

# Class must have this name
class myScreen(PiInfoScreen):
    refreshtime = 2
    displaytime = 5
    supportedsizes = [(320, 240)]
    pluginname = "LMSInfo"
    plugininfo = "Shows status of music playing on Logitech Media Server"
    
    def setPluginVariables(self):
        
        # Log on to LMS server
        self.lmsserverIP = self.pluginConfig["LMSServerInfo"]["serverip"]
        self.lmsserverTelnetPort = int(self.pluginConfig["LMSServerInfo"]["telnetport"])
        self.lmsserverWebPort = int(self.pluginConfig["LMSServerInfo"]["webport"])
        self.lmsServer = self.lmsLogon(self.lmsserverIP, self.lmsserverTelnetPort)
        
        # Get player
        self.squeezePlayers = self.getSqueezePlayers(self.lmsServer)
        self.playerIndex = 0
        self.squeezePlayer = self.getPlayer(self.squeezePlayers)
        
        # Set a few variables for this screen
        self.currenttrack = None
        self.nexttrack = None
        self.playlist = None
        self.currentart = None
        self.currenttrackname = None
        self.currentartist = None
        self.currentalbum = None
        self.nexttracks = None


    
    def lmsLogon(self, host, port):
        try:    
            sc = Server(hostname=host, port=port)
            sc.connect()
        except:
            sc = None
        return sc

    def getSqueezePlayers(self, server):
        try:
            sq= server.get_players()
        except:
            sq = None
        return sq
    
    def getPlayer(self, players):

        if players:
            try:
                player = players[self.playerIndex]
            except:
                self.playerIndex = 0
                player = players[self.playerIndex]

        else:
            player = None

        return player

    def nextPlayer(self):
        self.squeezePlayers = self.getSqueezePlayers(self.lmsServer)
        self.playerIndex = (self.playerIndex + 1) % len(self.squeezePlayers)
        self.squeezePlayer = self.squeezePlayers[self.playerIndex]

    # Only refresh all data if track has changed
    def currentTrackChanged(self, playlist, pos):
        track = pos
        try:
            if playlist[track]['id'] == self.currenttrack:
                return False
            else: 
                return True
        except:
            return True
            
    # Has the next track changed
    def nextTrackChanged(self, playlist, pos):
        try:
            if (playlist[pos + 1]['id'] == self.nexttracks[0]['id']) or (playlist[pos + 2]['id'] == self.nexttracks[1]['id']):
                return False
            else: 
                return True
        except:
            return True
            
    # Get current track information
    def getCurrentTrackInfo(self, playlist, pos):
        self.currenttrack = int(playlist[pos]['id'])
        self.currentart = pygame.transform.scale(self.LoadImageFromUrl("http://%s:%d/music/current/cover.jpg" % (self.lmsserverIP, self.lmsserverWebPort), True),(150,150))
        self.currenttrackname = self.squeezePlayer.get_track_title_unicode()
        self.currentartist = self.squeezePlayer.get_track_artist_unicode()
        self.currentalbum = self.squeezePlayer.get_track_album_unicode()
 
    def getNextTrackInfo(self, playlist, pos):
        ntracks = []
        
        for i in range(2):
            try:
                trackdetail = {}
                trackdetail['id'] = int(playlist[pos+i+1]['id'])
                trackdetail['trackname'] = str(playlist[pos+i+1]['title'])
                trackdetail['artist'] = str(playlist[pos+i+1]['artist'])
                ntracks.append(trackdetail)
            except:
                continue

        return ntracks
                        
    def Button1Click(self):
        # Toggles play/pause on player
        self.squeezePlayer.toggle()

    def Button2Click(self):
        # Previous track
        self.squeezePlayer.prev()

    def Button3Click(self):
        # Next track
        self.squeezePlayer.next()

    def Button4Click(self):
        # Change player
        self.nextPlayer()

    # Main function - returns screen to main script
    def showScreen(self):
        self.surface.fill([0,0,0])
        myfont = pygame.font.SysFont(None, 18)
        mybigfont = pygame.font.SysFont(None, 20)
        mysmallfont = pygame.font.SysFont(None, 12)
        
        if self.lmsServer == None:
            try:
                self.lmsServer = self.lmsLogon(self.lmsserverIP, self.lmsserverTelnetPort)
                self.squeezePlayers = self.getSqueezePlayers(self.lmsServer)
                self.squeezePlayer = self.getPlayer(self.squeezePlayers)
            finally:
                errortext = pygame.font.SysFont("freesans",10).render("Logitech Media Server not found on %s." % (self.lmsserverIP),1,(255,255,255))
                errorrect = errortext.get_rect()
                errorrect.centerx = self.surface.get_rect().centerx
                errorrect.centery = self.surface.get_rect().centery
                self.surface.blit(errortext,errorrect)
            
        elif self.squeezePlayer == None:
            try:
                self.lmsServer = self.lmsLogon(self.lmsserverIP, self.lmsserverTelnetPort)
                self.squeezePlayer = self.getSqueezePlayer(self.lmsServer)
            finally:
                errortext = pygame.font.SysFont("freesans",10).render("No Squeezeplayers connected to server on %s." % (self.lmsserverIP),1,(255,255,255))
                errorrect = errortext.get_rect()
                errorrect.centerx = self.surface.get_rect().centerx
                errorrect.centery = self.surface.get_rect().centery
                self.surface.blit(errortext,errorrect)
        
        else:
            if len(self.lmsServer.get_players()) == 0:
                self.squeezePlayer = None
            else:    
                try:
                    self.playlist = self.squeezePlayer.playlist_get_info()
                    self.playlistposition = int(self.squeezePlayer.playlist_get_position())
                except:
                    self.squeezePlayer = None
                else:
                   
                    if self.currentTrackChanged(self.playlist, self.playlistposition):
                        self.getCurrentTrackInfo(self.playlist,self.playlistposition)
                        
                    if self.nextTrackChanged(self.playlist, self.playlistposition):

                        updatenext = True
                        self.nexttracks=self.getNextTrackInfo(self.playlist, self.playlistposition)
                    else:
                        updatenext = False
                    # Player name
                    playername = myfont.render(self.squeezePlayer.get_name(), 1, (255,255,255))
                    self.surface.blit(playername, (310 - playername.get_rect()[2], 10))
                    # Now playing...
                    nowtext = myfont.render("Now playing...", 1, (255,255,255))
                    self.surface.blit(nowtext, (170, 60))
                    
                    # get artwork
                    self.surface.blit(self.currentart, (10,40))
                    
                    # get artist name
                    artisttext = mybigfont.render(self.currentartist, 1, [255,255,255])
                    self.surface.blit(artisttext, (170,85))
                    
                    # get track name
                    tracktext = myfont.render(self.currenttrackname, 1, [255,255,255])
                    self.surface.blit(tracktext, (170,110))        

                    # get track album
                    albumtext = myfont.render(self.currentalbum, 1, [255,255,255])
                    self.surface.blit(albumtext, (170,135))   
                    
                    # Show progress bar
                    elapse = self.squeezePlayer.get_time_elapsed()
                    duration = self.squeezePlayer.get_track_duration()
                    try:
                        trackposition = elapse / duration
                    except:
                        trackposition = 0
                    self.surface.blit(self.showProgress(trackposition,(130,10),(255,255,255),(0,0,144),(0,0,0)),(170,180))
                    
                    elapsem, elapses = divmod(int(elapse),60)
                    elapseh, elapsem = divmod(elapsem, 60)
                    elapsestring = "%02d:%02d" % (elapsem, elapses)
                    if elapseh > 0 : elapsestring = elapsestring + "%d:" % (elapseh)
                    
                    durationm, durations = divmod(int(duration),60)
                    durationh, durationm = divmod(durationm, 60)             
                    durationstring = "%02d:%02d" % (durationm, durations)
                    if durationh > 0 : durationstring = durationstring + "%d:" % (durationh)    
                    
                    progressstring = "%s / %s" % (elapsestring, durationstring)
                    
                    progresstext = myfont.render(progressstring, 1, (255,255,255))
                    self.surface.blit(progresstext, (170, 160))
                    
             
                    # Next track info
                        
                    # if len(self.nexttracks) > 0:
                    #     if updatenext:
                    #         self.nexttrackart = pygame.transform.scale(self.LoadImageFromUrl("http://%s:%d/music/%d/cover.jpg" % (self.lmsserverIP, self.lmsserverWebPort, self.nexttracks[0]['id'])),(75,75))

                    #     nexttracklabel = mysmallfont.render("Next track: %s - %s" % (self.nexttracks[0]['artist'], self.nexttracks[0]['trackname']), 1, (255,255,255))
                    #     self.surface.blit(self.nexttrackart, (20, 300))
                    #     self.surface.blit(nexttracklabel, (105, 300))

                    # if len(self.nexttracks) > 1:
                    #     if updatenext:
                    #         self.xnexttrackart = pygame.transform.scale(self.LoadImageFromUrl("http://%s:%d/music/%d/cover.jpg" % (self.lmsserverIP, self.lmsserverWebPort, self.nexttracks[1]['id'])),(75,75))

                    #     xnexttracklabel = mysmallfont.render("Next track: %s - %s" % (self.nexttracks[1]['artist'], self.nexttracks[1]['trackname']), 1, (255,255,255))
                    #     self.surface.blit(self.xnexttrackart, (20, 385))
                    #     self.surface.blit(xnexttracklabel, (105, 385))
        
        # Scale our surface to the required screensize before sending back
        scaled = pygame.transform.scale(self.surface,self.screensize)
        self.screen.blit(scaled,(0,0))
            
        return self.screen
