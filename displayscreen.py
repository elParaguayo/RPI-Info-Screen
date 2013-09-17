import pygame
import ConfigParser
import sys
import os
import urllib2
import urllib
import StringIO
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class PiInfoScreen():
    
    # Set default names
    pluginname = "UNDEFINED"
    plugininfo = "You should set pluginname and plugininfo in your plugin subclass"
    
    # List of screen sizes supported by the script
    supportedsizes = [ (694,466) ]
    
    # Refresh time = how often the data on the screen should be updated (seconds)
    refreshtime = 30
    
    # How long screen should be displayed before moving on to next screen (seconds)
    # only relevant when screen is autmatically changing screens
    # rather than waiting for key press
    displaytime = 5
    
    # Read the plugin's config file and dump contents to a dictionary
    def readConfig(self):
        class AutoVivification(dict):
            """Implementation of perl's autovivification feature."""
            def __getitem__(self, item):
                try:
                    return dict.__getitem__(self, item)
                except KeyError:
                    value = self[item] = type(self)()
                    return value
        
        self.pluginConfig = AutoVivification()
        
        try:
            config = ConfigParser.ConfigParser()
            config.read(self.configfile)
            for section in config.sections():
                for option in config.options(section):
                    self.pluginConfig[section][option] = config.get(section,option)
        except:
            pass
            
        self.setPluginVariables()
    
    # Can be overriden to allow plugin to change option type
    # Default method is to treat all options as strings
    # If option needs different type (bool, int, float) then this should be done here
    # Alternatively, plugin can just read variables from the pluginConfig dictionary that's created
    # Any other variables (colours, fonts etc.) should be defined here
    def setPluginVariables(self):
        pass
    
    # Tells the main script that the plugin is compatible with the requested screen size
    def supported(self):
        return self.supported
    
    # Returns the refresh time    
    def refreshtime(self):
        return self.refreshtime
    
    # Returns the display time
    def displaytime(self):
        return self.displaytime
    
    # Returns a short description of the script
    # displayed when user requests list of installed plugins
    def showInfo(self):
        return self.plugininfo

    # Returns name of the plugin
    def screenName(self):
        return self.pluginname
    
    # Get web page
    def getPage(self, url):
        user_agent = 'Mozilla/5 (Solaris 10) Gecko'
        headers = { 'User-Agent' : user_agent }
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        the_page = response.read()
        return the_page
    
    # Function to get image and return in format pygame can use    
    def LoadImageFromUrl(self, url, solid = False):
        f = urllib.urlopen(url)
        buf = StringIO.StringIO(f.read())
        image = self.LoadImage(buf, solid)
        return image
        
    def LoadImage(self, fileName, solid = False):
        image = pygame.image.load(fileName)
        image = image.convert()
        if not solid:
            colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    
    
    # Draws a progress bar    
    def showProgress(self, position, barsize, bordercolour, fillcolour, bgcolour):
        try:
            if position < 0 : position = 0
            if position > 1 : position = 1
        except:
            position = 0
        progress = pygame.Surface(barsize)
        pygame.draw.rect(progress,bgcolour,(0,0,barsize[0],barsize[1]))
        progresswidth = int(barsize[0] * position)
        pygame.draw.rect(progress,fillcolour,(0,0,progresswidth,barsize[1]))
        pygame.draw.rect(progress,bordercolour,(0,0,barsize[0],barsize[1]),1)
        return progress

    def render_textrect(self, string, font, rect, text_color, background_color, 
                        justification=0, vjustification=0, margin=0, shrink = False, 
                        SysFont=None, FontPath=None, MaxFont=0, MinFont=0):
        """Returns a surface containing the passed text string, reformatted
        to fit within the given rect, word-wrapping as necessary. The text
        will be anti-aliased.

        Takes the following arguments:

        string - the text you wish to render. \n begins a new line.
        font - a Font object
        rect - a rectstyle giving the size of the surface requested.
        text_color - a three-byte tuple of the rgb value of the
                     text color. ex (0, 0, 0) = BLACK
        background_color - a three-byte tuple of the rgb value of the surface.
        justification - 0 (default) left-justified
                        1 horizontally centered
                        2 right-justified

        Returns the following values:

        Success - a surface object with the text rendered onto it.
        Failure - raises a TextRectException if the text won't fit onto the surface.
        """
        
        """ Amended by el_Paraguayo:
         - cutoff=True - cuts off text instead of raising error
         - margin=(left,right,top,bottom) or 
         - margin=2 is equal to margin = (2,2,2,2) 
         - shrink=True adds variable font size to fit text
            - Has additional args:
                - SysFont=None - set SysFont to use when shrinking
                - FontPath=none - set custom font path to use when shrinking
                MaxFont=0 (max font size)
                MinFont=0 (min font size)
         - vjustification=0 adds vertical justification
            0 = Top
            1 = Middle
            2 = Bottom
        """
        
        class TextRectException(Exception):
            def __init__(self, message = None):
                self.message = message
            def __str__(self):
                return self.message

        def draw_text_rect(string, font, rect, text_color, background_color, 
                           justification=0, vjustification=0, margin=0, cutoff=True):
                               
            final_lines = []

            requested_lines = string.splitlines()

            # Create a series of lines that will fit on the provided
            # rectangle.

            for requested_line in requested_lines:
                if font.size(requested_line)[0] > (rect.width - (margin[0] + margin[1])):
                    words = requested_line.split(' ')
                    # if any of our words are too long to fit, return.
                   # for word in words:
                   #     if font.size(word)[0] >= (rect.width - (margin * 2)):
                   #         raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
                            
                    # Start a new line
                    accumulated_line = ""
                    for word in words:
                        test_line = accumulated_line + word + " "
                        # Build the line while the words fit.    
                        if font.size(test_line.strip())[0] < (rect.width - (margin[0] + margin[1])) :
                            accumulated_line = test_line 
                        else: 
                            final_lines.append(accumulated_line) 
                            accumulated_line = word + " " 
                    final_lines.append(accumulated_line)
                else: 
                    final_lines.append(requested_line) 

            # Let's try to write the text out on the surface.

            surface = pygame.Surface(rect.size) 
            surface.fill(background_color) 

            accumulated_height = 0 
            for line in final_lines: 
                if accumulated_height + font.size(line)[1] >= (rect.height - margin[2] - margin[3]):
                    if not cutoff:
                        raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
                    else:
                        break
                if line != "":
                    tempsurface = font.render(line.strip(), 1, text_color)
                    if justification == 0:
                        surface.blit(tempsurface, (0 + margin[0], accumulated_height + margin[2]))
                    elif justification == 1: 
                        surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height + margin[2]))
                    elif justification == 2:
                        surface.blit(tempsurface, (rect.width - tempsurface.get_width() - margin[1], accumulated_height + margin[2]))
                    else:
                        raise TextRectException, "Invalid justification argument: " + str(justification)
                accumulated_height += font.size(line)[1]

            if vjustification == 0:
                # Top aligned, we're ok
                pass
            elif vjustification == 1:
                # Middle aligned
                tempsurface = pygame.Surface(rect.size)
                tempsurface.fill(background_color)
                vpos = (0, (rect.size[1] - accumulated_height)/2)
                tempsurface.blit(surface, vpos, (0,0,rect.size[0],accumulated_height))
                surface = tempsurface
            elif vjustification == 2:
                # Bottom aligned
                tempsurface = pygame.Surface(rect.size)
                tempsurface.fill(background_color)
                vpos = (0, (rect.size[1] - accumulated_height - margin[3]))
                tempsurface.blit(surface, vpos, (0,0,rect.size[0],accumulated_height))
                surface = tempsurface
            else:
                raise TextRectException, "Invalid vjustification argument: " + str(justification)
            return surface
            
        surface = None
        
        if type(margin) is tuple:
            if not len(margin) == 4:
                try:
                    margin = (int(margin),  int(margin), int(margin), int(margin))
                except:
                    margin = (0,0,0,0)
        elif type(margin) is int:
            margin = (margin, margin, margin, margin)
        else:
            margin = (0,0,0,0)
        
        if not shrink:
            surface = draw_text_rect(string, font, rect, text_color, background_color, 
                                     justification=justification, vjustification=vjustification, 
                                     margin=margin, cutoff=False)
        
        else:
            fontsize = MaxFont
            fit = False
            while fontsize >= MinFont:
                if FontPath is None:
                    myfont = pygame.font.SysFont(SysFont,fontsize)
                else:
                    myfont = pygame.font.Font(FontPath,fontsize)
                try:
                    surface = draw_text_rect(string, myfont, rect,text_color, background_color, 
                                             justification=justification, vjustification=vjustification, 
                                             margin=margin, cutoff=False)
                    fit = True
                    break
                except:
                    fontsize -= 1
            if not fit:
                surface = draw_text_rect(string, myfont, rect, text_color, background_color, 
                                         justification=justification, vjustification=vjustification, 
                                         margin=margin)

        return surface
    
    # Main function - returns screen to main script
    # Will be overriden by plugins
    # Defaults to showing name and description of plugin
    def showScreen(self):
        self.screen.fill([0,0,0])
   
        screentext = pygame.font.SysFont("freesans",20).render("%s: %s." % (self.pluginname, self.plugininfo),1,(255,255,255))
        screenrect = screentext.get_rect()
        screenrect.centerx = self.screen.get_rect().centerx
        screenrect.centery = self.screen.get_rect().centery
        self.screen.blit(screentext,screenrect)
            
        return self.screen
        
        
    # This function should not be overriden
    def __init__(self, screensize, scale=True):
        
        # Set config filepath...
        self.plugindir=os.path.dirname(sys.modules[self.__class__.__module__].__file__)
        self.configfile = os.path.join(self.plugindir, "config", "screen.ini")
        
        # ...and read the config file
        self.readConfig()
        
        # Save the requested screen size
        self.screensize = screensize
        
        # Check requested screen size is compatible and set supported property
        if screensize not in self.supportedsizes:
            self.supported = False
        else:
            self.supported = True
         
        # Initialise pygame for the class
        if self.supported or scale:    
            pygame.init()
            self.screen = pygame.display.set_mode(self.screensize)
            self.surfacesize = self.supportedsizes[0]
            self.surface = pygame.Surface(self.surfacesize)
