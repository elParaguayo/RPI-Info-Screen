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

'''
The Imaginatively Titled
RPi Info Screen
(PiTFT version)
'''

import sys
import pygame
import imp
import os
import getopt 
import traceback
from time import time

from pitftgpio import PiTFT_GPIO

# USER VARIABLES - CAN BE EDITED
debug = True
screensleep = 60000

# DON'T CHANGE ANYTHING BELOW THIS LINE
##############################################################################

# Tell the RPi to use the TFT screen and that it's a touchscreen device
# os.putenv('SDL_VIDEODRIVER', 'fbcon')
# os.putenv('SDL_FBDEV'      , '/dev/fb1')
# os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
# os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')

##############################################################################
# methods to be called be command line flags
def usage():
    '''Background about the script - to be shown when called with help flag'''
    print "RPi Info Screen by elParaguayo"
    print "Displays custom screens on attached display\n"
    print "Usage: " + sys.argv[0] + " [options]"
    print "\t-l\tList available screens"
    print "\t-h\tDisplay this screen"


def listPlugins():
    '''Function for displaying list of plugins that should work'''
    global pluginScreens
    print "RPi Info Screen\n"
    print "Available screens:"
    a=1
    for i in pluginScreens:
        id = str(a)
        print "\t" + id + "\t" + i.showInfo()  
        a = a + 1
##############################################################################

def log(message):
    '''Prints message if user has set debug flag to true.'''
    if debug:
        print message

##############################################################################
# Plugin handling code adapted from: 
# http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/
# THANK YOU!
# ############################################################################
def getPlugins():
    plugins = []
    possibleplugins = os.listdir(PluginFolder)
    a=1
    for i in possibleplugins:
        location = os.path.join(PluginFolder,i)
        if not os.path.isdir(location) or not PluginScript in os.listdir(location):
            continue
        inf = imp.find_module(MainModule, [location])
        plugins.append({"name": i, "info": inf, "id": a})
        a=a+1
    return plugins

def loadPlugin(plugin):
    return imp.load_module(MainModule, *plugin["info"])
##############################################################################


##############################################################################
# Initialise plugin screens
def getScreens():
    '''Gets list of available plugin screen objects.'''
    a = []
    for i in getPlugins():
        plugin = loadPlugin(i)
        try:
            # The plugin should have the myScreen function
            # We send the screen size for future proofing (i.e. plugins should
            # be able to cater for various screen resolutions
            #
            # TO DO: Work out whether plugin can return more than one screen!
            loadedscreen = plugin.myScreen(size, userevents=piscreenevents)
            a.append(loadedscreen)
            showLoadedPlugin(loadedscreen)
        
        except:
            # If it doesn't work, ignore that plugin and move on
            log(traceback.format_exc())
            continue
    return a
##############################################################################


##############################################################################
# Event handling methods
def setUpdateTimer(pluginloadtime):
    ''' Sets an update timer
    Depending on the speed of the processor, the timer
    can flood the event queue with UPDATE events but
    if the plugin takes a while to load there may be no time for
    anything else.
    This function provides some headroom in the timer
    '''
    interval = max(5 * pluginloadtime, pluginScreens[screenindex].refreshtime)

    pygame.time.set_timer(UPDATESCREEN,0)
    pygame.time.set_timer(UPDATESCREEN, interval)

def showWelcomeScreen():
    '''Display a temporary screen to show it's working
    May not display for long because of later code to show plugin loading
    '''
    screen.fill([0,0,0])
    label = myfont.render("Initialising screens...", 1, (255,255,255))
    labelpos = label.get_rect()
    labelpos.centerx = screen.get_rect().centerx
    labelpos.centery = screen.get_rect().centery
    screen.blit(label, labelpos) 
    pygame.display.flip()

def showLoadedPlugin(plugin):
    '''Display a temporary screen to show when a module is successfully
    loaded.
    '''
    screen.fill([0,0,0])
    label = myfont.render("Successfully imported: %s"
                          % (plugin.screenName()), 1, (255,255,255))
    labelpos = label.get_rect()
    labelpos.centerx = screen.get_rect().centerx
    labelpos.centery = screen.get_rect().centery
    screen.blit(label, labelpos) 
    pygame.display.flip()

def setNextScreen(a):
    '''Queues the next screen.'''
    pygame.time.set_timer(NEWSCREEN,0)
    pygame.time.set_timer(UPDATESCREEN,0)
    pygame.event.post(pygame.event.Event(NEXTSCREEN))
    a = (a + 1) % len(pluginScreens)
    displayLoadingScreen(a)
    return a

def displayLoadingScreen(a):
    '''Displays a loading screen.'''
    screen.fill((0,0,0))
    holdtext = myfont.render("Loading screen: %s" 
                            % pluginScreens[a].screenName(),
                            1, 
                            (255,255,255))
    holdrect = holdtext.get_rect()
    holdrect.centerx = screen.get_rect().centerx
    holdrect.centery = screen.get_rect().centery
    screen.blit(holdtext, holdrect)
    pygame.display.flip()
    pygame.time.set_timer(NEWSCREEN, 2000)

def showNewScreen():
    '''Show the next screen.'''
    pygame.time.set_timer(NEWSCREEN,0)
    strttime = time()
    screen = pluginScreens[screenindex].showScreen()
    stptime = time()
    plugdiff = int((stptime - strttime)*1000)
    setUpdateTimer(plugdiff)
    pygame.display.flip()
##############################################################################

##############################################################################
# Call back functions for TFT Buttons
def TFTBtn1Click(channel):
    pygame.event.post(click1event)

def TFTBtn2Click(channel):
    pygame.event.post(click2event)

def TFTBtn3Click(channel):
    pygame.event.post(click3event)

def TFTBtn4Click(channel):
    pygame.event.post(click4event)
##############################################################################



# This is where we start

# Initialise pygame
pygame.init()

# Initialise screen object
tftscreen = PiTFT_GPIO()

# Plugin location and names
PluginFolder = "./plugins"
PluginScript = "screen.py"
MainModule = "screen"
pluginScreens = []

# Screen size (currently fixed)
size = width, height = 320,240

# Set up some custom events
TFTBUTTONCLICK = pygame.USEREVENT + 1
UPDATESCREEN = TFTBUTTONCLICK + 1
NEXTSCREEN = UPDATESCREEN + 1
NEWSCREEN = NEXTSCREEN + 1
SLEEPEVENT = NEWSCREEN + 1

# Set up the four TFT button events
click1event = pygame.event.Event(TFTBUTTONCLICK, button=1)
click2event = pygame.event.Event(TFTBUTTONCLICK, button=2)
click3event = pygame.event.Event(TFTBUTTONCLICK, button=3)
click4event = pygame.event.Event(TFTBUTTONCLICK, button=4)

# Set up the callback functions for the buttons
tftscreen.Button1Interrupt(TFTBtn1Click)
tftscreen.Button2Interrupt(TFTBtn2Click)
tftscreen.Button3Interrupt(TFTBtn3Click)
tftscreen.Button4Interrupt(TFTBtn4Click)

# Dict of events that are accessible to screens
piscreenevents = {
    "button": TFTBUTTONCLICK,
    "update": UPDATESCREEN,
    "nextscreen": NEXTSCREEN,
}

# Set our screen size
# Should this detect attached display automatically?
screen = pygame.display.set_mode(size)

# Set header (useful for testing, not so much for full screen mode!)
pygame.display.set_caption("Info screen")

# Hide mouse
pygame.mouse.set_visible(False)

# Stop keys repeating
pygame.key.set_repeat()

# Base font for messages
myfont = pygame.font.SysFont(None, 20)

# Show welcome screen
showWelcomeScreen()

# Get list of screens that can be provided by plugins
pluginScreens = getScreens()

# Parse some options
try:
    opts, args = getopt.getopt(sys.argv[1:], 'lh', ['help', 'list'])
except getopt.GetoptError as err:
    log(err)
    usage()
    sys.exit()

for o,a in opts:
    # Show installed plugins
    if o in ("-l", "--list"):
        listPlugins()
        sys.exit()
    # Show help
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    # TO DO: add option for automatic screen change (with timeout)
    
# Set some useful variables for controlling the display
quit=False
screenindex=0

# Queue the first screen
displayLoadingScreen(screenindex)

# Run our main loop
while not quit:
    for event in pygame.event.get():
        
        # Handle quit message received
        if event.type == pygame.QUIT:
            quit=True 
        
        # 'Q' to quit    
        if (event.type == pygame.KEYUP): 
            if (event.key == pygame.K_q):
                quit = True
        
        # 'N' to change screen
        if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_n):
                screenindex = setNextScreen(screenindex)


        # 'N' to change screen
        if (event.type == pygame.MOUSEBUTTONUP):
            screenindex = setNextScreen(screenindex)
        
        # 'S' saves screenshot
        if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_s):
                filename = "screen" + str(a) + ".jpeg"                
                pygame.image.save(screen, filename)

        if (event.type == TFTBUTTONCLICK):
            if (event.button == 1):                
                pluginScreens[a].Button1Click()

            if (event.button == 2):                
                pluginScreens[a].Button2Click()

            if (event.button == 3):                
                pluginScreens[a].Button3Click()

            if (event.button == 4):                
                pluginScreens[a].Button4Click()

        if (event.type == UPDATESCREEN):
            screen = pluginScreens[screenindex].showScreen()
            pygame.display.flip()

        if (event.type == NEWSCREEN):
            showNewScreen()


# If we're here we've exited the display loop...
log("Exiting...")
sys.exit(0)
