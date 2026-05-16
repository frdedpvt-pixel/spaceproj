import time
import pygame
import sys
import math
class Vector:
    def __init__(self,x,y):
        self.xc = x
        self.yc = y

    def mag(self):
        m = (self.xc)**2 + (self.yc)**2
        return m**0.5

    def component(self):
        m = self.mag()
        if m == 0:
            return Vector(0,0)
        nx = (self.xc)/m

        ny = (self.yc)/m

        return Vector(nx,ny)

    def __mul__(self,scal):
        nx = (self.xc)*scal
        ny = (self.yc)*scal
        return Vector(nx,ny)
    
    def __rmul__(self,scal):
        nx = (self.xc)*scal
        ny = (self.yc)*scal
        return Vector(nx,ny)
    def __add__(self,otheritem):
        return Vector(self.xc+otheritem.xc, self.yc+otheritem.yc)
    
    def __sub__(self,otheritem):
        return Vector(self.xc-otheritem.xc, self.yc-otheritem.yc)

    def __repr__(self):
        return f"[{f'{self.xc:.4f}'}i + {f'{self.yc:.4f}'}j]"

class Body:
    def __init__(self,m,p,v,r,rot=0):
        self.m = m
        self.p = p
        self.v = v
        self.rot = rot
        self.r = r

    def update(self,a,dt):
        self.p,self.v = e_i(self.p,self.v,a,dt)
collision = 0
def step_simulation(bodies, dt, thrust):
    a_l = []
    for bod in bodies:
        a_l1 = []

        for k in bodies:
            if k == bod:
                continue
            ass = getgrav(bod.p,bod.m,k.p,k.m)
            a_l1.append(ass)

        g = Vector(0,0)
        for f in a_l1:
            g += f
        
        a_l.append(g)
    stp = 0
    for bod in bodies:
        if bod == rocket:
            bod.update(a_l[stp] + thrust,dt)
        else:
            bod.update(a_l[stp],dt)
        stp+=1

    for bod in bodies:

        for k in bodies:
            if k == bod:
                continue
            else:
                diff = bod.p - k.p
                if diff.mag() <= (bod.r + k.r):
                    if bod == rocket or k == rocket:
                        global collision
                        collision = 1
                        print("Collision!")

def collision_close(universe,rocket):
        for bod in universe:
            if bod == rocket:
                continue
            diff = bod.p - rocket.p
            if diff.mag() <= (bod.r + rocket.r):
                return bod

def e_i(pos,vel,acc,dt):
    
    vel = vel + acc*dt

    dp = vel*dt
    pos = pos+dp

    return (pos,vel)

def getgrav(p1,m1,p2,m2):
    r = p2-p1
    mag_r = r.mag()
    mag_r = max(mag_r, 0.1)

    r_comp = r.component()

    G = 1
    a = (G*m2)/(mag_r**1.2)
    return a*r_comp



pygame.init()

pygame.font.init()

WIDTH, HEIGHT = 900,900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("rocketry stuff")
clock = pygame.time.Clock()

artxt = pygame.font.SysFont("Arial", 24)

info = "this"

cam_x = 0
cam_y = 0

cam_mode = [0,1]
cam = 0

zoom = 1

sp_bg = pygame.image.load(r'C:\Users\ACER\phyexp\spaceproj\background_space.jpg')

# The Solar System (True Mass Ratios & Stable Satellite Orbit)

# Sun is massive to anchor the system
sun = Body(1000000, Vector(0, 0), Vector(0, 0), 200)

# Inner Rocky Planets
mercury = Body(5, Vector(3900, 0), Vector(0, 16.01), 8)
venus = Body(80, Vector(7200, 0), Vector(0, 11.78), 19)
earth = Body(100, Vector(10000, 0), Vector(0, 10.00), 20)
mars = Body(11, Vector(15200, 0), Vector(0, 8.11), 10)

# Outer Gas Giants 
jupiter = Body(31800, Vector(52000, 0), Vector(0, 4.38), 110)
saturn = Body(9500, Vector(95800, 0), Vector(0, 3.23), 90)
uranus = Body(1450, Vector(192000, 0), Vector(0, 2.28), 40)
neptune = Body(1710, Vector(300000, 0), Vector(0, 1.82), 38)

# ROCKET (Orbiting Earth)
# Earth's V is 10.00. The local orbit V is 1.58. Total V = 11.58.
rocket = Body(0.001, Vector(10040, 0), Vector(0, 11.58), 0.1) 

universe = []
universe.append(sun)
universe.append(rocket)
universe.extend([mercury, venus, earth, mars, jupiter, saturn, uranus, neptune])
dots = []

thrust = Vector(0,0)
thrust_power = 0
flag1 = 1
while True:
    ozoom = zoom
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    d = pygame.key.get_pressed()
    
    if d[pygame.K_x]:
        cam = cam_mode[0]
    elif d[pygame.K_c]:
        cam = cam_mode[1]

    if d[pygame.K_a]:
        rocket.rot -= 1
    elif d[pygame.K_d]:
        rocket.rot += 1

    if d[pygame.K_UP]:
        if zoom <= 1:
            zoom += 0.01  # Slower zoom for precision
    elif d[pygame.K_DOWN]:
        if zoom > 0.001:  # Allow extreme zoom out
            zoom -= 0.01
        else:
            zoom = 0.001


    rocket.rot = rocket.rot % 360

    if ozoom != zoom:
        dots = []

    if cam == 0:
        cam_x = 0
        cam_y = 0
    elif cam == 1:
        cam_x = rocket.p.xc
        cam_y = rocket.p.yc

    if d[pygame.K_w]:
        thrust_power +=1
    if d[pygame.K_s]:
        thrust_power = max(0, thrust_power - 1)

    step_simulation(universe, 0.01, thrust)
    rad_angle = math.radians(rocket.rot)
    if collision == 0:
        thrust = Vector(math.cos(rad_angle) * thrust_power, math.sin(rad_angle) * thrust_power)
    elif collision:
        planet = collision_close(universe, rocket)
        if planet:
            rocket.v = Vector(0, 0) # 1. Hard stop
            diff = rocket.p - planet.p
            rocket.p = planet.p + diff.component() * (rocket.r + planet.r) # 2. Surface snap
            
        # 3. If you throttle up, break the collision lock so you can fly away
        if thrust_power > 0:
            collision = 0

    oa,ob = int(((rocket.p.xc - cam_x) * zoom) + WIDTH/2),int(((rocket.p.yc - cam_y) * zoom) + HEIGHT/2)


    na,nb = int(((rocket.p.xc - cam_x) * zoom) + WIDTH/2),int(((rocket.p.yc - cam_y) * zoom) + HEIGHT/2)
    tempo = (oa,ob)

    dots.append(tempo)

    if len(dots) < 2500:
        for o in tempo:
            flag1 = 0
    else:
        dots.pop(0)
        flag1 = 1
    
    if rocket.rot >= 360:
        rocket.rot = 0
    elif rocket.rot == -360:
        rocket.rot = 0
    
    infot = f'''Thrust: {thrust}'''
    
    infop = f"Position: {rocket.p}"

    infov = f"Velocity: {rocket.v}"

    info_surface1 = artxt.render(infot,True, (255, 215, 0))
    info_surface2 = artxt.render(infop,True, (255, 215, 0))
    info_surface3 = artxt.render(infov,True, (255, 215, 0))
    
    info1_rect = info_surface1.get_rect(topleft = (0,2))
    info2_rect = info_surface2.get_rect(topleft = (0,4))
    info3_rect = info_surface3.get_rect(topleft = (0,6))

    screen.blit(sp_bg,(0,0))
    screen.blit(info_surface1,(0,2))
    screen.blit(info_surface2,(0,30))
    screen.blit(info_surface3,(0,60))

    for bod in universe:

        draw_x = int(((bod.p.xc - cam_x) * zoom) + WIDTH/2)
        draw_y = int(((bod.p.yc - cam_y) * zoom) + HEIGHT/2)


        draw_r = max(1, int(bod.r * zoom))
        pygame.draw.circle(screen, (240, 240, 240), (draw_x, draw_y), draw_r)

        if bod == rocket:
            line_length = 15
            end_x = draw_x + math.cos(math.radians(rocket.rot)) * line_length
            end_y = draw_y + math.sin(math.radians(rocket.rot)) * line_length
            pygame.draw.line(screen, (255, 50, 50), (draw_x, draw_y), (int(end_x), int(end_y)), 2)

        for i in dots:
            pygame.draw.circle(screen,(230,230,0),i,1)

    pygame.display.flip()
    clock.tick(120)
