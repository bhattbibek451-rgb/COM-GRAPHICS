
# Bresenham's line algorithm implementation in Python using Pygame

def bla(x1,y1,x2,y2):
    dx=abs(x2-x1)
    dy=abs(y2-y1)

    if(x2>x1):
        lx=1
    else:
        lx=-1
    if(y2>y1):
        ly=1
    else:
        ly=-1
    
    x=x1
    y=y1
    

    if(dx>dy):
        pk=2*dy-dx
        for i in range(dx):
            if(pk<0):
                x=x+lx
                pk=pk+2*dy
            else:
                x=x+lx
                y=y+ly
                pk=pk+2*dy-2*dx
            screen.set_at((x,y),white)
    else:
        pk=2*dx-dy
        for i in range(dy):
            print(x,y)
            if(pk<0):
                y=y+ly
                pk=pk+2*dx
            else:
                y=y+ly
                x=x+lx
                pk=pk+2*dx-2*dy
            screen.set_at((x,y),white)

import pygame
import sys
pygame.init()
w,h=800,600
screen=pygame.display.set_mode((w,h))
white=(255,255,255)
black=(0,0,0)

while True:
    for event in pygame.event.get():
        if(event.type==pygame.QUIT):
            pygame.quit()
            sys.exit()
    screen.fill(black)
    bla(0,0,80,30)
    
    pygame.display.flip()




    