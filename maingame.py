import pygame
import sys
import math
import os

pygame.init()

width, height=1366, 768
window=pygame.display.set_mode((width,height))

res= width, height
path = os.path.realpath(os.path.dirname(__file__))
background = pygame.transform.smoothscale(pygame.image.load(path+"/images/background.jpg").convert(), res)

def quit_game():
    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()

class c_player:
    def __init__ (self, x, y):
        self.posx, self.posy=x, y
        self.speed, self.g_speed=0, 0
        self.gravity, self.vjump=0.4, -9
        self.can_climbjump, self.num_dash=False, 0
        self.dash_time, self.dash_max=0, 8
        self.update_hitbox(), self.load_images()
    def load_images(self):
        self.player_right=pygame.image.load(path+"/images/player_right.png")
        self.player_left=pygame.image.load(path+"/images/player_left.png")
    def update_hitbox(self):
        if self.speed>0==0:
            self.xmin, self.xmax=self.posx+10, self.posx+42
            self.ymin, self.ymax=self.posy+5, self.posy+45
        else:
            self.xmin, self.xmax=self.posx+12, self.posx+42
            self.ymin, self.ymax=self.posy+5, self.posy+45
    def fall(self):
        self.posy+=self.g_speed
        self.g_speed+=self.gravity
    def create_dash(self):
        self.dash_time=self.dash_max
        self.mousex, self.mousey=pygame.mouse.get_pos()
        self.vector_x=self.mousex-self.posx+20
        self.vector_y=self.mousey-self.posy+20
        if self.vector_x==0:
            self.vector_x=0.01
        if self.vector_x>=0 and self.vector_y>=0:
            self.dash_angle=math.atan(abs(self.vector_y)/abs(self.vector_x))
        elif self.vector_x<0 and self.vector_y>=0:
            self.dash_angle=math.pi-math.atan(abs(self.vector_y)/abs(self.vector_x))
        elif self.vector_x<0 and self.vector_y<0:
            self.dash_angle=math.pi+math.atan(abs(self.vector_y)/abs(self.vector_x))
        else:
            self.dash_angle=math.pi*2-math.atan(abs(self.vector_y)/abs(self.vector_x))
        self.dash_y=(math.sin(self.dash_angle))*45
        self.dash_x=(math.cos(self.dash_angle))*45
    def update_colissions(self):
        self.c_right=colission_right()
        self.c_left=colission_left()
        self.c_up=colission_up()
        self.c_down=colission_down()
        colission_dash_items()
    def events(self):
        self.update_colissions()
        for event in pygame.event.get():
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    quit_game()
                if event.key==pygame.K_SPACE:
                    if self.c_down:
                        self.g_speed=self.vjump
                    elif (self.c_left or self.c_right) and self.can_climbjump:
                        self.can_climbjump=False
                        self.g_speed=self.vjump
            if event.type==pygame.MOUSEBUTTONDOWN:
                if event.button==1 and self.num_dash>0:
                    self.num_dash-=1
                    self.create_dash()
        key=pygame.key.get_pressed()
        if key[pygame.K_d] and self.c_right==False and self.dash_time==0:
            player.posx+=10
        elif key[pygame.K_a] and self.c_left==False and self.dash_time==0:
            player.posx-=10
#        else:
#            player.speed=0

        if self.c_up or self.c_down or self.c_right or self.c_left:
            if self.dash_time==self.dash_max:
                self.num_dash+=1
            self.dash_time=0
        if self.dash_time>0:
            self.dash_time-=1
            self.posy+=self.dash_y
            self.posx+=self.dash_x
            self.g_speed=0
        for i in list_wind:
            if colission_wind(i)==True:
                if (i.speed<0 and self.c_up==False) or (i.speed>0 and self.c_down==False):
                    player.g_speed+=i.speed
        if self.c_down==False:
            self.fall()
        self.posx+=self.speed
        self.update_hitbox()
    def draw(self):
        if self.speed>=0:
            window.blit(self.player_right,(self.posx,self.posy))
        else:
            window.blit(self.player_left,(self.posx,self.posy))

class c_block:
    def __init__ (self, x, y, sizex, sizey):
        self.color=255,255,255
        self.posx, self.posy=x, y
        self.sizex, self.sizey=sizex, sizey
        self.update()
    def update(self):
        self.rect_block=pygame.Rect(self.posx,self.posy,self.sizex,self.sizey)
    def draw(self):
        pygame.draw.rect(window,self.color,self.rect_block)

class c_static_enemy:
    def __init__(self, x, y, size):
        self.posx, self.posy=x, y
        self.size=size
        self.update_hitbox(), self.load_images()
    def load_images(self):
        if self.size=="small":
            self.enemypng=pygame.image.load(path+"/images/static_enemy_small.png")
        elif self.size=="medium":
            self.enemypng=pygame.image.load(path+"/images/static_enemy_medium.png")
        else:
            self.enemypng=pygame.image.load("/images/static_enemy_big.png")
    def update_hitbox(self):
        if self.size=="small":
            self.xmin, self.xmax=self.posx+15, self.posx+55
            self.ymin, self.ymax=self.posy+15, self.posy+55
        elif self.size=="medium":
            self.xmin, self.xmax=self.posx+20, self.posx+78
            self.ymin, self.ymax=self.posy+20, self.posy+78
        else:
            self.xmin, self.xmax=self.posx+25, self.posx+105
            self.ymin, self.ymax=self.posy+25, self.posy+105
    def draw(self):
        window.blit(self.enemypng,(self.posx,self.posy))

class c_lineal_enemy:
    def __init__(self, x, y, size, angle, times, speed):
        self.posx, self.posy=x, y
        self.size=size
        self.times,self.TIMES=0,times
        self.speed, self.angle=speed, (360-angle)*math.pi/180
        self.update_hitbox(), self.load_images()
    def load_images(self):
        if self.size=="small":
            self.enemypng=pygame.image.load(path+"/images/lineal_enemy_small.png")
        elif self.size=="medium":
            self.enemypng=pygame.image.load(path+"/images/lineal_enemy_medium.png")
        else:
            self.enemypng=pygame.image.load(path+"/images/lineal_enemy_big.png")
    def update_hitbox(self):
        if self.size=="small":
            self.xmin, self.xmax=self.posx+15, self.posx+55
            self.ymin, self.ymax=self.posy+15, self.posy+55
        elif self.size=="medium":
            self.xmin, self.xmax=self.posx+20, self.posx+78
            self.ymin, self.ymax=self.posy+20, self.posy+78
        else:
            self.xmin, self.xmax=self.posx+25, self.posx+105
            self.ymin, self.ymax=self.posy+25, self.posy+105
    def move(self):
        if self.times==self.TIMES:
            self.times=0
            self.speed*=-1
        self.posx+=math.cos(self.angle)*self.speed
        self.posy+=math.sin(self.angle)*self.speed
        self.times+=1
        self.update_hitbox()
    def draw(self):
        window.blit(self.enemypng,(self.posx,self.posy))

class c_rotate_enemy:
    def __init__(self, x, y, size, radius, speed):
        self.size, self.radius=size, radius
        self.centerx, self.centery=x, y
        self.posx, self.posy=self.radius+self.centerx, self.centery
        self.speed, self.angle=speed, 0
        self.update_hitbox(), self.load_images()
    def load_images(self):
        if self.size=="small":
            self.enemypng=pygame.image.load(path+"/images/rotate_enemy_small.png")
        elif self.size=="medium":
            self.enemypng=pygame.image.load(path+"/images/rotate_enemy_medium.png")
        else:
            self.enemypng=pygame.image.load(path+"/images/rotate_enemy_big.png")
    def update_hitbox(self):
        if self.size=="small":
            self.xmin, self.xmax=self.posx+15, self.posx+55
            self.ymin, self.ymax=self.posy+15, self.posy+55
        elif self.size=="medium":
            self.xmin, self.xmax=self.posx+20, self.posx+78
            self.ymin, self.ymax=self.posy+20, self.posy+78
        else:
            self.xmin, self.xmax=self.posx+25, self.posx+105
            self.ymin, self.ymax=self.posy+25, self.posy+105
    def rotate(self):
        self.angle+=self.speed
        self.posx=self.radius*math.cos(self.angle)+self.centerx
        self.posy=self.radius*math.sin(self.angle)+self.centery
        self.update_hitbox()
    def draw(self):
        window.blit(self.enemypng,(self.posx,self.posy))

class c_dynamic_enemy:
    def __init__(self, x, y):
        self.posx, self.posy=x, y
        self.speedmax, self.g=5, 0.1
        self.speed_x=self.speed_y=0
        self.gravity_x=self.gravity_y=self.g
        self.update_hitbox(),self.load_images()
    def load_images(self):
        self.enemypng=pygame.image.load(path+"/images/dynamic_enemy.png")
        self.update_hitbox()
    def update_hitbox(self):
        self.xmin, self.xmax=self.posx+15, self.posx+55
        self.ymin, self.ymax=self.posy+15, self.posy+55
    def set_gravity(self):
        if player.posx>self.posx and self.gravity_x<0:
            self.speed_x*=0.8
            self.gravity_x*=-1
        elif player.posx<=self.posx and self.gravity_x>0:
            self.speed_x*=0.8
            self.gravity_x*=-1
        if player.posy>self.posy and self.gravity_y<0:
            self.speed_y*=0.8
            self.gravity_y*=-1
        elif player.posy<=self.posy and self.gravity_y>0:
            self.speed_y*=0.8
            self.gravity_y*=-1
    def move(self):
        self.set_gravity()
        self.posx+=self.speed_x
        self.speed_x+=self.gravity_x
        self.posy+=self.speed_y
        self.speed_y+=self.gravity_y
        self.speed_x=min(max(-self.speedmax,self.speed_x),self.speedmax)
        self.speed_y=min(max(-self.speedmax,self.speed_y),self.speedmax)
        self.update_hitbox()
    def draw(self):
        window.blit(self.enemypng,(self.posx,self.posy))

class c_dash_item:
    def __init__(self, x, y):
        self.posx, self.posy=x, y
        self.update_hitbox(), self.load_images()
    def update_hitbox(self):
        self.xmin, self.xmax=self.posx, self.posx+20
        self.ymin, self.ymax=self.posy, self.posy+20
    def load_images(self):
        self.itempng=pygame.image.load(path+"/images/dashitem.png")
        self.itempng=pygame.transform.scale(self.itempng,(20,20))
    def draw(self):
        window.blit(self.itempng,(self.posx,self.posy))

class c_wind:
    def __init__(self, x, y, sizex, sizey, speed):
        self.posx, self.posy=x, y
        self.sizex, self.sizey= sizex, sizey
        self.speed=speed
        self.update_hitbox(), self.load_images()
    def update_hitbox(self):
        self.xmin, self.xmax=self.posx, self.posx+self.sizex
        self.ymin, self.ymax=self.posy, self.posy+self.sizey
    def load_images(self):
        self.windpng=pygame.image.load(path+"/images/wind.png")
        self.windpng=pygame.transform.scale(self.windpng,(self.sizex,self.sizey))
    def draw(self):
        window.blit(self.windpng,(self.posx,self.posy))

class c_camera:
    def __init__(self, x, y):
        self.posx, self.posy=x, y
    def set_pos(self, x, y):
        self.scrollx=self.posx-x
        self.scrolly=self.posy-y
        self.move_x(self.scrollx)
        self.move_y(self.scrolly)
    def move_x(self, scroll=0):
        self.posx-=scroll
        player.posx+=scroll
        player.update_hitbox()
        for i in list_blocks:
            i.posx+=scroll
            i.update()
        for i in list_static_enemies:
            i.posx+=scroll
            i.update_hitbox()
        for i in list_lineal_enemies:
            i.posx+=scroll
            i.update_hitbox()
        for i in list_rotate_enemies:
            i.centerx+=scroll
            i.update_hitbox()
        for i in list_dynamic_enemies:
            i.posx+=scroll
            i.update_hitbox()
        for i in list_dash_items:
            i.posx+=scroll
            i.update_hitbox()
        for i in list_wind:
            i.posx+=scroll
            i.update_hitbox()
    def move_y(self, scroll=0):
        self.posy-=scroll
        player.posy+=scroll
        player.update_hitbox()
        for i in list_blocks:
            i.posy+=scroll
            i.update()
        for i in list_static_enemies:
            i.posy+=scroll
            i.update_hitbox()
        for i in list_lineal_enemies:
            i.posy+=scroll
            i.update_hitbox()
        for i in list_rotate_enemies:
            i.centery+=scroll
            i.update_hitbox()
        for i in list_dynamic_enemies:
            i.posy+=scroll
            i.update_hitbox()
        for i in list_dash_items:
            i.posy+=scroll
            i.update_hitbox()
        for i in list_wind:
            i.posy+=scroll
            i.update_hitbox()

def same_axis(i,axis):
    if axis=="x":
        if player.xmax<=i.posx or player.xmin>=i.posx+i.sizex:
            return False
        return True
    if player.ymax<=i.posy or player.ymin>=i.posy+i.sizey:
        return False
    return True
        
def colission_right():
    for i in list_blocks:
        if same_axis(i,"y")==True:
            if player.xmax>=i.posx and player.xmin<i.posx:
                player.posx=i.posx-(player.xmax-player.posx)
                player.update_hitbox()
                return True
    return False

def colission_left():
    for i in list_blocks:
        if same_axis(i,"y")==True:
            if player.xmin<=i.posx+i.sizex and player.xmax>i.posx+i.sizex:
                player.posx=i.posx+i.sizex-(player.xmin-player.posx)
                player.update_hitbox()
                return True
    return False

def colission_up():
    for i in list_blocks:
        if same_axis(i,"x")==True:
            if player.ymin+player.g_speed<=i.posy+i.sizey and player.ymax>i.posy+i.sizey:
                player.posy=i.posy+i.sizey+(player.ymin-player.posy)
                player.g_speed=5
                player.update_hitbox()
                return True
    return False

def colission_down():
    for i in list_blocks:
        if same_axis(i,"x")==True:
            if player.ymax+player.g_speed>=i.posy and player.posy<i.posy:
                player.g_speed=0
                player.posy=i.posy-(player.ymax-player.posy)
                player.can_climbjump=True
                player.update_hitbox()
                return True
    return False

def colission_enemies():
    return False
    for i in list_static_enemies:
        if player.xmax>=i.xmin and player.xmin<=i.xmax:
            if player.ymax>=i.ymin and player.ymin<=i.ymax:
                return True
    for i in list_lineal_enemies:
        if player.xmax>=i.xmin and player.xmin<=i.xmax:
            if player.ymax>=i.ymin and player.ymin<=i.ymax:
                return True
    for i in list_rotate_enemies:
        if player.xmax>=i.xmin and player.xmin<=i.xmax:
            if player.ymax>=i.ymin and player.ymin<=i.ymax:
                return True
    for i in list_dynamic_enemies:
        if player.xmax>=i.xmin and player.xmin<=i.xmax:
            if player.ymax>=i.ymin and player.ymin<=i.ymax:
                return True
    return False

def colission_dash_items():
    for i in list_dash_items:
        if player.xmax>=i.xmin and player.xmin<=i.xmax and player.ymax>=i.ymin and player.ymin<=i.ymax:
            list_dash_items.remove(i)
            player.num_dash+=2
            return True
    return False

def colission_wind(i):
    if player.xmax>=i.xmin and player.xmin<=i.xmax and player.ymax>=i.ymin and player.ymin<=i.ymax:
        return True
    return False

def redraw():
    window.blit(background,(0,0))
    player.draw()
    for i in list_wind:
        i.draw()
    for i in list_blocks:
        i.draw()
    for i in list_static_enemies:
        i.draw()
    for i in list_lineal_enemies:
        i.draw()
    for i in list_rotate_enemies:
        i.draw()
    for i in list_dynamic_enemies:
        i.draw()
    for i in list_dash_items:
        i.draw()
    pygame.display.update()


def load_blocks():
    list_blocks=[]
    list_blocks.append(c_block(60,600,500,80))
    list_blocks.append(c_block(350,430,160,80))
    return list_blocks
def load_static_enemies():
    list_static_enemies=[]
    return list_static_enemies
def load_lineal_enemies():
    list_lineal_enemies=[]
    return list_lineal_enemies
def load_rotate_enemies():
    list_rotate_enemies=[]
    return list_rotate_enemies
def load_dynamic_enemies():
    list_dynamic_enemies=[]
    return list_dynamic_enemies
def load_dash_items():
    list_dash_items=[]
    list_dash_items.append(c_dash_item(250,350))
    return list_dash_items
def load_wind():
    list_wind=[]
    return list_wind

player=c_player(80,550)
list_blocks=load_blocks()
list_static_enemies=load_static_enemies()
list_lineal_enemies=load_lineal_enemies()
list_rotate_enemies=load_rotate_enemies()
list_dynamic_enemies=load_dynamic_enemies()
list_dash_items=load_dash_items()
list_wind=load_wind()
clock=pygame.time.Clock()

while True:
    clock.tick(60)
    player.events()
    for i in list_lineal_enemies:
        i.move()
    for i in list_rotate_enemies:
        i.rotate()
    for i in list_dynamic_enemies:
        i.move()
    if colission_enemies():
        quit_game()
    redraw()