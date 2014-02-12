import sys
import pygame
import imp
import os
import getopt 
import traceback

# Set some variables

# Plugin location and names
PluginFolder = "./plugins"
PluginScript = "screen.py"
MainModule = "screen"
pluginScreens = []

# Screen size (currently fixed)
size = width, height = 694, 466

# Automatically cycle screens
automode = False

# Background about the script
def usage():
    print "RPi Info Screen by elParaguayo"
    print "Displays custom screens on attached display\n"
    print "Usage: " + sys.argv[0] + " [options]"
    print "\t-l\tList available screens"
    print "\t-h\tDisplay this screen"
    print "\t-s\tSet size of display e.g. '-s 600,400'"


# Plugin handling code adapted from: http://lkubuntu.wordpress.com/2012/10/02/writing-a-python-plugin-api/
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

# Collect a list of plugins found
def getScreens():
    a = []
    for i in getPlugins():
        plugin = loadPlugin(i)
        try:
            # The plugin should have the myScreen function
            # We send the screen size for future proofing (i.e. plugins should be able to cater
            # for various screen resolutions
            #
            # TO DO: Work out whether plugin can return more than one screen!
            a.append(plugin.myScreen(size))
        
        except Exception, err:
            # If it doesn't work, ignore that plugin and move on
            # print traceback.format_exc()
            continue
    return a

def screenSize(arg):
    try:
        newsize = tuple([int(x) for x in a.split(",")])
        if len(newsize) == 2:
            global size
            global pluginScreens
            size = width, height = newsize
            pluginScreens = getScreens()
    except:
        pass

# Function for displaying list of plugins that should work
def listPlugins():
    global pluginScreens
    print "RPi Info Screen\n"
    print "Available screens:"
    a=1
    for i in pluginScreens:
        id = str(a)
        print "\t" + id + "\t" + i.showInfo()  
        a = a + 1

# This is where we start

# Initialise pygame
pygame.init()

# Get list of screens that can be provided by plugins
pluginScreens = getScreens()

# Parse some options
try:
    opts, args = getopt.getopt(sys.argv[1:], 'alhs:', ['auto', 'help', 'list', 'size'])
except getopt.GetoptError as err:
    print(err)
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
    # Screen size
    if o in ("-s", "--size"):
        print "size", a
        screenSize(a)
    # Automatically change screens
    if o in ("-a", "--auto"):
        automode = True
    # TO DO: add option for automatic screen change (with timeout)
    
# Set our screen size
# Should this detect attached display automatically?
screen = pygame.display.set_mode(size)

# Set header (useful for testing, not so much for full screen mode!)
pygame.display.set_caption("Info screen")

# Hide mouse
pygame.mouse.set_visible(False)

# Stop keys repeating
pygame.key.set_repeat()

# Display a temporary screen to show it's working
# May not display for long because of later code to show plugin loading
screen.fill([0,0,0])
myfont = pygame.font.SysFont(None, 20)
label = myfont.render("Initialising screens...", 1, (255,255,255))
labelpos = label.get_rect()
labelpos.centerx = screen.get_rect().centerx
labelpos.centery = screen.get_rect().centery
screen.blit(label, labelpos) 
pygame.display.flip()

# Set some useful variables for controlling the display
quit=False
a=1
b=pygame.time.get_ticks()
c=-1
d=0
newscreen=False
newwait=0
refresh = 60000

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
                a = a + 1
                if a > len(pluginScreens) - 1: a = 0
        
        # 'S' saves screenshot
        if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_s):
                filename = "screen" + str(a) + ".jpeg"                
                pygame.image.save(screen, filename)

        if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_f):                
                pygame.display.toggle_fullscreen()

# only update the screen if it has changed
#
# TO DO: automatic screen change
    if a <> c:
        
        # Tell the user we're loading next screen
        screen.fill((0,0,0))
        holdtext = myfont.render("Loading screen: " + pluginScreens[a].screenName(),1, (255,255,255))
        holdrect = holdtext.get_rect()
        holdrect.centerx = screen.get_rect().centerx
        holdrect.centery = screen.get_rect().centery
        screen.blit(holdtext, holdrect)
        pygame.display.flip()
        newscreen=True
        newwait=pygame.time.get_ticks()+2000
        c=a
                
    if newscreen and (pygame.time.get_ticks()>newwait or automode):
        # Get the next screen
        newscreen = False
        screen = pluginScreens[a].showScreen()
        pygame.display.flip()
        

        # time how long do we display screen
        nextscreen = pluginScreens[a].displaytime * 1000
        refresh = pluginScreens[a].refreshtime * 1000
        

    # refresh current screen
    if pygame.time.get_ticks() >= (b + refresh):
        screen = pluginScreens[a].showScreen()
        pygame.display.flip()
        b = pygame.time.get_ticks()
        
    if automode and (pygame.time.get_ticks() >= (d + nextscreen)):
        a = a + 1
        if a > len(pluginScreens) - 1: a = 0
        d = pygame.time.get_ticks()
        
        

    

# If we're here we've exited the display loop...
print "Exiting..."
sys.exit()


