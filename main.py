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
    a = (G*m2)/(mag_r**2)
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

universe = []

sun = Body(100000, Vector(0, 0), Vector(0, 0),50)
rocket = Body(1, Vector(200, 0), Vector(0, 15),5)
collision = 0
# The Solar System (Stable Orbital Data)
mercury = Body(3, Vector(300, 0), Vector(0, 18.25),20)
venus = Body(48, Vector(500, 0), Vector(0, 14.14),20)
earth = Body(59, Vector(750, 0), Vector(0, 11.54),20)
mars = Body(6, Vector(1100, 0), Vector(0, 9.53),20)
jupiter = Body(1500, Vector(2500, 0), Vector(0, 6.32),20)
saturn = Body(1100, Vector(4500, 0), Vector(0, 4.71),20)
uranus = Body(800, Vector(7000, 0), Vector(0, 3.77),20)
neptune = Body(900, Vector(10000, 0), Vector(0, 3.16),20)

universe.append(sun)
universe.append(rocket)
universe.extend([mercury, venus, earth, mars, jupiter, saturn, uranus, neptune])
dots = []
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
            zoom += 0.05
    elif d[pygame.K_DOWN]:
        if zoom > 0.20:
            zoom -=0.05
        else:
            zoom = 0.20


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
        thrust_power = 0
        collision = 1
        rocket.p = collision_close(universe,rocket).p

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


        pygame.draw.circle(screen, (240, 240, 240), (draw_x, draw_y), bod.r)

        if bod == rocket:
            line_length = 15
            end_x = draw_x + math.cos(math.radians(rocket.rot)) * line_length
            end_y = draw_y + math.sin(math.radians(rocket.rot)) * line_length
            pygame.draw.line(screen, (255, 50, 50), (draw_x, draw_y), (int(end_x), int(end_y)), 2)

        for i in dots:
            pygame.draw.circle(screen,(230,230,0),i,1)

    pygame.display.flip()
    clock.tick(120)
