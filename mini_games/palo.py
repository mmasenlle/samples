import sys, pygame, time
from random import randint
from pygame.locals import *

pygame.init()

size = width, height = 600, 440
black = 10, 10, 100
bsize = 50
vmax = 5

screen = pygame.display.set_mode(size)

ball = pygame.transform.scale(pygame.image.load("data/ball.bmp"), (bsize, bsize))
ballrect = ball.get_rect()
n=5
balls=[]

class Palo:
    def __init__(self):
        self.h = 10
        self.rect = pygame.Rect(0,height-self.h,width,self.h)
        self.sube_baja = 0
        self.golpeando = 10
    def sube(self):
        self.sube_baja = -1
    def baja(self):
        self.sube_baja = 1
    def para(self):
        self.sube_baja = 0
    def golpe(self):
        self.golpeando = -3
    def update(self):
        if self.golpeando < 4:
            self.rect = self.rect.move([0,(self.golpeando)*3])
            self.golpeando += 1
        if self.sube_baja > 0 and self.rect.bottom < height:
            self.rect = self.rect.move([0,self.sube_baja])
            if self.sube_baja < 5:
                self.sube_baja += 1
        if self.sube_baja < 0 and self.rect.top > 0:
            self.rect = self.rect.move([0,self.sube_baja])
            if self.sube_baja > -5:
                self.sube_baja -= 1
        screen.fill((200,20,20), self.rect)

palo=Palo()

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
        if self.rect.bottom > height or self.rect.bottom > palo.rect.top:
            if self.speed[1] > 0:
                self.speed[1] = -abs(self.speed[1]) + 1 # gravity correction ?
            if self.rect.bottom > palo.rect.top and palo.golpeando < 4:
                self.speed[1] += (palo.golpeando)*3
    def update_speed_collision_(self, other):
        if self.rect.colliderect(other):
            self.speed,other.speed = other.speed,self.speed
    def update_speed_gravity_(self):
        if self.rect.bottom < height:
            self.speed[1] += 1
    def update(self):
        #print "speed:",self.speed
        self.rect = self.rect.move(self.speed)
        if self.rect.bottom > palo.rect.top:
            self.rect.bottom = min(palo.rect.top + 10, self.rect.bottom)
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
    #print "clock.get_time():",clock.get_time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            going = False
        elif event.type == KEYDOWN:
            if event.key == K_DOWN:
                palo.baja()
            elif event.key == K_UP:
                palo.sube()
            elif event.key == K_LEFT:
                palo.golpe()
        elif event.type == KEYUP and (event.key == K_UP or event.key == K_DOWN):
            palo.para()
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

    palo.update()
     
    for i in xrange(len(balls)):
        balls[i].update_speed(i)
        
    pygame.display.flip()

pygame.quit()