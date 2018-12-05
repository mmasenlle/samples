import sys, pygame, time
import numpy as np
from random import randint
from pygame.locals import *

pygame.init()

size = width, height = 400, 440
black = 10, 10, 100
bsize = 40
vmax = 100 # 500 # px/s
g = 20 # 200.0 # px/s**2

screen = pygame.display.set_mode(size)

gun = pygame.Rect(0,0,15,15)
gun.center = (width/2, height-7)
mov=0
shoot=0

ball = pygame.transform.scale(pygame.image.load("data/ball.bmp"), (bsize, bsize))
ballrect = ball.get_rect()
n=1
balls=[]

bullets=[]

class Score:
    score=0
    noballs=[]
    def ground(self,ball):
        self.score *= .5
        self.noballs.append(ball)
    def drop(self):
        for b in self.noballs:
            if b in balls:
                balls.remove(b)

score=Score()

class Ball:
    def __init__(self):
        self.rect = ballrect.copy()
        self.rect.x = randint(0, width)
        self.rect.y = -30 #randint(0, height)
        self.speed = np.array([float(randint(0, vmax)), float(randint(0, vmax))])
        #self.speed = np.array([float(randint(0, 20)), float(randint(30, 50))])
        self.pos = np.array([self.rect.centerx,self.rect.centery])
        #print "rect:",self.rect," - veloc:",self.speed
    def update_speed_edge_(self):
        if self.rect.left < 0:
            self.speed[0] = abs(self.speed[0])
        if self.rect.right > width:
            self.speed[0] = -abs(self.speed[0])
        if self.rect.bottom > height:
            score.ground(self)
            #self.speed[1] = -abs(self.speed[1])
    def update_speed_collision_(self, other):
        dist = np.linalg.norm(self.pos-other.pos)
        if dist <= bsize: # contacto
            pos2 = self.pos.copy()
            if self.speed[0] > 0: pos2[0] += 1
            if self.speed[0] < 0: pos2[0] -= 1
            if self.speed[1] > 0: pos2[1] += 1
            if self.speed[1] < 0: pos2[1] -= 1
            dist2 = np.linalg.norm(pos2-other.pos)
            if dist > dist2: # acercamiento
                self.speed,other.speed = other.speed,self.speed
    def update_speed_gravity_(self):
        if self.rect.bottom < height:
            self.speed[1] += g*T
    def update(self):
        du=np.rint(self.speed*T)
        self.rect = self.rect.move(du)
        self.pos = np.array([self.rect.centerx,self.rect.centery])
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

class Bullet:
    def __init__(self):
        self.rect = pygame.Rect(0,0,5,5)
        self.rect.center = gun.center
    def update(self):
        if self.rect.y < 0:
            return False
        self.rect = self.rect.move(0,-30)
        pygame.draw.circle(screen, (250,165,0), self.rect.center, 3)
        return True

for i in range(n):
    balls.append(Ball())

clock = pygame.time.Clock()
going = True
fps = 50
T = 1.0/fps
print "T:",T,"s"
old_score=0
pT=100000
p1=pT*.978

myfont = pygame.font.SysFont(None, 30)

while going:
    #if (len(balls) == 0):
    #    print "Congratulations, score: ",score.score
        #going = False
        #break
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            going = False
        elif event.type == MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for b in balls:
                if b.rect.collidepoint(pos):
                    for siz in range(bsize,2,-2):
                        b.deflate(siz)
                        pygame.display.flip()
                        time.sleep(.01)
                    balls.remove(b)
        elif event.type == KEYDOWN:
            if event.key == K_SPACE: shoot = 1
            elif event.key == K_LEFT:  mov = -1
            elif event.key == K_RIGHT: mov =  1
        elif event.type == KEYUP:
            if event.key == K_LEFT and mov < 0: mov = 0
            elif event.key == K_RIGHT and mov > 0: mov = 0
            elif event.key == K_SPACE: shoot = 0

    screen.fill(black)

    # render text
    label = myfont.render("Score: "+str(score.score), 1, (255,255,0))
    screen.blit(label, (100, 100))

    for b in balls:
        b.update()
     
    for i in xrange(len(balls)):
        balls[i].update_speed(i)

    score.drop()

    if shoot == 1 or shoot > 6:
        bullets.append(Bullet())
    if shoot > 0: shoot += 1

    if mov != 0:
        gun = gun.move(mov,0)
        if gun.centerx < 0: gun.centerx = 0
        if gun.centerx > width: gun.centerx = width
        if mov < 0 and mov > -50: mov -= 3
        if mov > 0 and mov <  50: mov += 3

    for b in bullets:
        for ba in balls:
            if ba.rect.colliderect(b):
                for siz in range(bsize,2,-2):
                    ba.deflate(siz)
                    pygame.display.flip()
                    time.sleep(.001)
                balls.remove(ba)
                bullets.remove(b)
                score.score += ba.pos[1] #ba.speed[1]
                break
    for b in bullets:
        if not b.update():
            bullets.remove(b)

    pygame.draw.polygon(screen, (100,105,250), ((gun.left,gun.bottom),(gun.centerx,gun.top),(gun.right,gun.bottom)), 0)
        
    pygame.display.flip()

    #if old_score != score.score:
    #    print "score: ",score.score
    #    old_score = score.score

    if len(balls) < 300 and randint(0, pT) > p1:
        balls.append(Ball())
    if p1 > 1: p1 -= 1

pygame.quit()