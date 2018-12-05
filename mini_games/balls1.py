import sys, pygame, time
from random import randint
from pygame.locals import *

pygame.init()

size = width, height = 800, 480
black = 10, 10, 100

screen = pygame.display.set_mode(size)

ball = pygame.transform.scale(pygame.image.load("data/ball.bmp"), (50, 50))
ballrect = ball.get_rect()

class Ball:
    rect = None
    speed = None
    def __init__(self):
        self.rect = ballrect.copy()
        self.rect.x = randint(0, width)
        self.rect.y = randint(0, height)
        self.speed = [randint(0, 15), randint(0, 15)]
        print "rect:",self.rect," - veloc:",self.speed
    def update_speed_edge(self):
        if self.rect.left < 0:
            self.speed[0] = abs(self.speed[0])
        if self.rect.right > width:
            self.speed[0] = -abs(self.speed[0])
        if self.rect.bottom > height:
            self.speed[1] = -abs(self.speed[1])
    def update_speed_collision(self, other):
        r_i,r_j = self.rect,other.rect
        if r_i.left < r_j.x and r_i.right > r_j.x and r_i.top < r_j.y and r_i.bottom > r_j.y:
            self.speed,other.speed = other.speed,self.speed

n=7
balls=[]
for i in range(n):
    balls.append(Ball())


while 1:
    if (len(balls) == 0):
        print "Congratulations"
        sys.exit()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            #print "pos: ",pos #,"dir(pos):",dir(pos)
            lst=[]
            for i in range(len(balls)):
                if balls[i].rect.left < pos[0] and balls[i].rect.right > pos[0] and balls[i].rect.top < pos[1] and balls[i].rect.bottom > pos[1]:
                    lst.append(i)
            for i in lst:
                print "delete",i
                for siz in range(50,2,-2):
                    pygame.draw.circle(screen, black, (balls[i].rect.x+25,balls[i].rect.y+25), 25)
                    ballp = pygame.transform.scale(ball, (siz, siz))
                    rp = ballp.get_rect()
                    rp.x+=balls[i].rect.x+(50-siz)/2
                    rp.y+=balls[i].rect.y+(50-siz)/2
                    screen.blit(ballp, rp)
                    pygame.display.flip()
                    time.sleep(.01)
                del balls[i]
            

    screen.fill(black)
    for b in balls:
        b.rect = b.rect.move(b.speed)
        screen.blit(ball, b.rect)
        if b.rect.bottom < height: # and balls[i].rect.top > 0:
            b.speed[1] += 1
     
    for i in range(len(balls)):
        for j in range(i+1, len(balls)):
            balls[i].update_speed_collision(balls[j])
        balls[i].update_speed_edge()
        
    pygame.display.flip()
    time.sleep(.01)