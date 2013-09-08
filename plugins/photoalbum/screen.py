import os
from random import choice
from displayscreen import PiInfoScreen

# Class must have this name
class myScreen(PiInfoScreen):
    refreshtime = 5
    displaytime = 60
    supportedsizes = [ (480,234) ]
    pluginname = "PhotoAlbum"
    plugininfo = "Displays slideshow of images"
    
    def setPluginVariables(self):

        #self.surfaceratio = self.surfacesize[0]/self.surfacesize[1]
    
        # Set folders for photos
        self.searchfolders = []
        for folder in self.pluginConfig["Albums"]["folders"].split(","):
            self.searchfolders.append(folder.strip())
        self.myphotos = self.getPhotos(self.searchfolders)
        
       
    def getPhotos(self, folders):
        photos = []
        for folder in folders:
            for filename in os.listdir(folder):
                if filename.lower().endswith('.jpg'):
                    photos.append(os.path.join(folder,filename))
        return photos
        

    # Main function - returns screen to main script
    def showScreen(self):
        self.surface.fill((0,0,0))
        rawphoto = pygame.image.load(choice(self.myphotos))
        photosize = rawphoto.get_rect()
        photofit = photosize.fit(self.surface.get_rect())
        photo = pygame.transform.scale(rawphoto,(photofit[2], photofit[3]))
        photofit.centerx = self.surface.get_rect().centerx        
        photofit.centery = self.surface.get_rect().centery
        self.surface.blit(photo,photofit)
        
        # Scale our surface to the required screensize before sending back
        scaled = pygame.transform.scale(self.surface,self.screensize)
        self.screen.blit(scaled,(0,0))
        return self.screen
