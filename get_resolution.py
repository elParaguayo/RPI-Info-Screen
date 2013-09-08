import pygame
from time import sleep

pygame.init()
screen = pygame.display.set_mode((0,0))

screen.fill((0,0,180))
rfont = pygame.font.SysFont(None,30)
size = screen.get_rect()
resolutiontext = rfont.render("Screen resolution: %d x %d" % (size[2],size[3]), 1, (255,255,255))
resrect = resolutiontext.get_rect()
resrect.centerx = size.centerx
resrect.centery = size.centery
screen.blit(resolutiontext, resrect)
pygame.display.flip()
sleep(5)
pygame.quit()


