import pygame
import sys
pygame.init() 
w,h=800,600 
screen = pygame.display.set_mode((w, h))
white = (255, 255, 255)
black = (0, 0, 0)

def draw(x1, y1, x2, y2):
    
    dx=x2 - x1
    dy=y2 - y1
    if abs(dx) > abs(dy):
        step=abs(dx)
    else:
        step=abs(dy)    
    xinc=dx/step
    yinc=dy/step
    x,y=x1,y1
    for i in range(step+1):
        screen.set_at((round(x), round(y)), white)
        x+=xinc
        y+=yinc   
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill(black)
    draw(40,40,120,120)
    pygame.display.flip()        