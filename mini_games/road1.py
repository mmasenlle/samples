import sys, pygame, time
import numpy as np
from random import randint
from pygame.locals import *

pygame.init()

size = width, height = 600, 600
black = 101, 110, 100

screen = pygame.display.set_mode(size)

car = pygame.transform.rotate(pygame.image.load("data/top.png"), -90)
carrect = car.get_rect()
carrect.center = (width/2, height*2/3)

clock = pygame.time.Clock()
going = True

road_y=range(0,height,1) + [height,]
road_x=[width/2 for _ in xrange(len(road_y))]

vr=width/2
n=0
vel=100
mov=0

while going:
    clock.tick(vel)
    #print "clock.get_time():",clock.get_time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            going = False
        elif event.type == KEYDOWN:
            if event.key == K_DOWN:
                if vel >= 10: vel -= 10
            elif event.key == K_UP:
                if vel < 200: vel += 10
            elif event.key == K_LEFT:
                if mov > -20: mov -= 1
            elif event.key == K_RIGHT:
                if mov < 20: mov += 1
        elif event.type == KEYUP and (event.key == K_LEFT or event.key == K_RIGHT):
            mov=0

    screen.fill(black)
    #for i in xrange(1,len(road_y)):
    #    #print "start_point:",(road_x[i-1],road_y[i-1])
    #    pygame.draw.line(screen, (255,255,0), (road_x[i-1]-25,road_y[i-1]), (road_x[i]-25,road_y[i]), 1)
    #    pygame.draw.line(screen, (255,255,0), (road_x[i-1]+25,road_y[i-1]), (road_x[i]+25,road_y[i]), 1)

    for i in xrange(len(road_y)):
        pygame.draw.line(screen, (255,255,200), (road_x[i]-65,road_y[i]), (road_x[i]+65,road_y[i]), 1)

    if mov != 0:
        print "mov:",mov
        carrect = carrect.move(mov,0)
    screen.blit(car, carrect)

    road_x.pop()
    n-=1
    if n <= 0:
        if mov > 0 and mov < 4: mov += 1
        if mov < 0 and mov > -4: mov -= 1
        n=20
        vr=np.random.normal(vr,50,1)
        vr=max(10,min(width-10,vr)) # saturation
    val=((road_x[0]*97) + (vr*3))/100.0 # low pass filter
    road_x = [int(round(val)),] + road_x

    pygame.display.flip()

pygame.quit()