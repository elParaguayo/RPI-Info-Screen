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

        #self.screenratio = self.screensize[0]/self.screensize[1]
    
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
        self.screen.fill((0,0,0))
        rawphoto = pygame.image.load(choice(self.myphotos))
        photosize = rawphoto.get_rect()
        photofit = photosize.fit(self.screen.get_rect())
        photo = pygame.transform.scale(rawphoto,(photofit[2], photofit[3]))
        photofit.centerx = self.screen.get_rect().centerx        
        photofit.centery = self.screen.get_rect().centery
        self.screen.blit(photo,photofit)
        return self.screen
