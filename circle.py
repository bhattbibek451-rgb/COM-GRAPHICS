# import pygame
# import sys

# pygame.init()
# w,h=1000,1000
# screen=pygame.display.set_mode((w,h))
# white=(255,255,255)
# black=(0,0,0)

# def trans(x1,y1,x2,y2):
#     tx=400
#     ty=600
#     x3=x1+tx
#     y3=y1+ty
#     x4=x2+tx
#     y4=y2+ty 
#     pygame.draw.line(screen,black,(x3,y3),(x4,y4),2)

# while True:
#     for event in pygame.event.get():
#         if(event.type==pygame.QUIT):
#             pygame.quit()
#             sys.exit()
#     screen.fill(white)
#     pygame.draw.line(screen,black,(100,100),(600,600),2)
#     trans(100,100,600,600)
#     pygame.display.flip()        



# import pygame
# import sys
# import math

# pygame.init()
# w,h=1000,1000
# screen=pygame.display.set_mode((w,h))
# white=(255,255,255)
# black=(0,0,0)
# red=(255,0,0)

# def rotation(x1,y1,x2,y2):
#     x3=x1*math.cos(math.radians(22)-y1*math.sin(math.radians(22)))
#     y3=y1*math.cos(math.radians(22)+y1*math.sin(math.radians(22)))
#     x4=x2*math.cos(math.radians(22)-y2*math.sin(math.radians(22)))
#     y4=y2*math.cos(math.radians(22)+y2*math.sin(math.radians(22)))
#     pygame.draw.line(screen,red,(x3,y3),(x4,y4),2)

# while True:
#     for event in pygame.event.get():
#         if(event.type==pygame.QUIT):
#             pygame.quit()
#             sys.exit()
#     screen.fill(white)
#     pygame.draw.line(screen,black,(50,50),(200,200),2)
#     rotation(50,50,200,200)
#     pygame.display.flip()        




import pygame
import sys

pygame.init()
w,h=1300,675
screen=pygame.display.set_mode((w,h))
white=(255,255,255)
black=(0,0,0)

def trans(x1,y1,x2,y2):
    tx=0
    while(tx<500):

        x3=x1+tx
        y3=y1
        x4=x2+tx
        y4=y2 
        tx+=10
        clock.tick(10)
        pygame.display.flip() 
        pygame.draw.line(screen,black,(x3,y3),(x4,y4),2)

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if(event.type==pygame.QUIT):
            pygame.quit()
            sys.exit()
    screen.fill(white)
    pygame.draw.line(screen,black,(100,100),(600,600),2)
    trans(100,100,600,600)
    pygame.display.flip()   






