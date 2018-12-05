import sys, pygame, time
from random import randint
from pygame.locals import *

pygame.init()

size = width, height = 400, 240
black = 10, 10, 100
bsize = 50
vmax = 50

screen = pygame.display.set_mode(size)

ball = pygame.transform.scale(pygame.image.load("data/ball.bmp"), (bsize, bsize))
ballrect = ball.get_rect()
n=15
balls=[]

class Ball:
    def __init__(self):
        self.rect = ballrect.copy()
        self.rect.x = randint(0, width)
        self.rect.y = randint(0, height)
        self.speed = [randint(0, vmax), randint(0, vmax)]
        print "rect:",self.rect," - veloc:",self.speed
    def update_speed_edge_(self):
        if self.rect.left < 0:
            self.speed[0] = abs(self.speed[0])
        if self.rect.right > width:
            self.speed[0] = -abs(self.speed[0])
        if self.rect.bottom > height:
            self.speed[1] = -abs(self.speed[1])
    def update_speed_collision_(self, other):
        if self.rect.colliderect(other):
            self.speed,other.speed = other.speed,self.speed
    def update_speed_gravity_(self):
        if self.rect.bottom < height:
            self.speed[1] += 1
    def update(self):
        self.rect = self.rect.move(self.speed)
        screen.blit(ball, self.rect)
        self.update_speed_gravity_()
    def deflate(self,siz):
        pygame.draw.circle(screen, black, self.rect.center, bsize/2)
        ballp = pygame.transform.scale(ball, (siz, siz))
        rp = ballp.get_rect()
        rp.center = self.rect.center
        screen.blit(ballp, rp)
    def update_speed(self,my_id):
        for j in xrange(my_id+1, len(balls)):
            self.update_speed_collision_(balls[j])
        self.update_speed_edge_()

for i in range(n):
    balls.append(Ball())

clock = pygame.time.Clock()
going = True

while going:
    if (len(balls) == 0):
        print "Congratulations"
        going = False
        break
    clock.tick(20)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for b in balls:
                if b.rect.collidepoint(pos):
                    for siz in range(bsize,2,-2):
                        b.deflate(siz)
                        pygame.display.flip()
                        time.sleep(.01)
                    balls.remove(b)
            

    screen.fill(black)
    for b in balls:
        b.update()
     
    for i in xrange(len(balls)):
        balls[i].update_speed(i)
        
    pygame.display.flip()

pygame.quit()