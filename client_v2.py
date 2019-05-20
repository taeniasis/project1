import pygame
import time
import sys
import socket as sc

from collections import deque
from codndecode import decode1
from pygame.locals import *


########## PUT THIS BULLSHIT IN A SEPARATE FILE AND IMPORT AND EXECUTE IT
client_socket = sc.socket()
client_socket.connect(('127.0.0.1', 9101))

FPS = 60
pygame.init()
pygame.display.set_caption('CLIENT')

fpsClock=pygame.time.Clock()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
surface = pygame.Surface(screen.get_size())
surface_left = surface.subsurface(0,0,SCREEN_WIDTH//2-50, SCREEN_HEIGHT)
surface_middle = surface.subsurface(SCREEN_WIDTH//2-50, 0, 100, SCREEN_HEIGHT)
surface_right = surface.subsurface(SCREEN_WIDTH//2+50, 0, SCREEN_WIDTH//2-50, SCREEN_HEIGHT)
text = pygame.font.SysFont('Calibri', 20)


pygame.key.set_repeat(1, 10)

def draw_box(surf, color, pos):
    r = pygame.Rect((pos[0], pos[1]), (10,10))
    pygame.draw.rect(surf, color, r)

#####################


class NPC_tracker_clientside:
    def __init__(self):
        self.player_shots = deque([])
        
        self.bullets = deque([])
        self.spawning_bullets=deque([])

        self.bombs = deque([])

        self.enemies = deque([])

        self.score = 0
        
        self.enm_side = 8
        self.side = 4

        self.left = 0
        self.right = SCREEN_WIDTH//2-50


    def draw(self, surf):
        for sp_bul in self.spawning_bullets:
            pygame.draw.circle(surf, (128,0,128), (int(sp_bul[0]), int(sp_bul[1])), 10)
        for bullet in self.bullets:
            pygame.draw.circle(surf, (255,0,255), (int(bullet[0]), int(bullet[1])), 5)
        for bomb in self.bombs:
            pygame.draw.circle(surf, (100,100,100), (int(bomb[0]), int(bomb[1])), int(bomb[2]))
        for enemy in self.enemies:
            pygame.draw.circle(surf, (200,200,0), (int(enemy[0]), int(enemy[1])), 10)
        for shot in self.player_shots:
            pygame.draw.rect(surf, (255,255,255), pygame.Rect((shot[2]-6, shot[3]-6),(12,12)))

    def recv_status(self, shots, bullets, sp_bullets, bombs, enemies):
        self.player_shots = deque(decode1(shots))
        
        self.bullets = deque(decode1(bullets))
        self.spawning_bullets = deque(decode1(sp_bullets))

        self.bombs = deque(decode1(bombs))

        self.enemies = deque(decode1(enemies))



class Player_clientside:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.lives = 0
        self.iframes=0
        self.bombs=0
        self.order_queue = deque([])
        
        
    def draw(self, surf):
        r = pygame.Rect((self.x-5, self.y-10), (10,20))
        if self.iframes==0:
            pygame.draw.rect(surf, (20,0,0), r)
        else:
            if self.iframes%2==0 and self.iframes>20:
                pygame.draw.rect(surf, (200,200,200), r)
            elif self.iframes%2==1 and self.iframes>20:
                pygame.draw.rect(surf, (20,0,0), r)
            else:
                pygame.draw.rect(surf, (75,75,75), r)

    def recv_status(self, coord, stats):
        x, y = coord.split(',')
        self.x, self.y = float(x), float(y)
        
        l,i,b = stats.split(',')
        self.lives, self.iframes,self.bombs=float(l),float(i),float(b)

##        package = connection.recv(512).decode('utf8')
##        l,i,b = package.split(',')
##        self.lives, self.iframes, self.bombs=float(l),float(i),float(b)

    ### as stated below it might be beneficial to cram all the input shit into 
    ### some methods here. It might cause pygame to throw a shitfit though



################
running = True
player_1 = Player_clientside()
NPC_tracker_1 = NPC_tracker_clientside()
orders = deque([])


##### MAYBE MAKE THE DISPLAY A SEPARATE OBJECT..?
##### MAKE A FANCY-ASS IF NAME==__MAIN__ CRAP OF THIS
while running:
    
#### THIS BABY MAY NEED A SEPARATE FUNCTION
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            client_socket.close()
            running = False
            break


    
    #### NOW THIS IS GOING IN MY CRINGE COMPILATION
    ##### SWEEP THIS BULLSHIT UNDER THE RUG WITH A FUNCTION OR A CLASS
    ##### ALSO THE INPUT/ORDERS MAY BE BETTER INSIDE A PLAYER_CLIENTSIDE METHOD
    keys = pygame.key.get_pressed()

    ord_move = ''
    ord_shoot = ''
    ord_bomb = ''
    ord_focus = ''
    ord_spare_2 = ''

    
    if keys[K_UP] and not (keys[K_LEFT] or keys[K_RIGHT] or keys[K_DOWN]):
        ord_move='UP'
    elif keys[K_DOWN] and not (keys[K_LEFT] or keys[K_RIGHT] or keys[K_UP]):
        ord_move='DOWN'
    elif keys[K_LEFT] and not (keys[K_UP] or keys[K_DOWN] or keys[K_RIGHT]):
        ord_move='LEFT'
    elif keys[K_RIGHT] and not (keys[K_UP] or keys[K_DOWN] or keys[K_LEFT]):
        ord_move='RIGHT'
    elif keys[K_UP] and keys[K_LEFT]:
        ord_move='UP-LEFT'
    elif keys[K_UP] and keys[K_RIGHT]:
        ord_move='UP-RIGHT'
    elif keys[K_DOWN] and keys[K_LEFT]:
        ord_move='DOWN-LEFT'
    elif keys[K_DOWN] and keys[K_RIGHT]:
        ord_move='DOWN-RIGHT'

    if keys[K_z]:
        ord_shoot='SHOOT'

    if keys[K_x]:
        ord_bomb='BOMB'

    if keys[K_LSHIFT]:
        ord_focus='FOCUS'

    
    orders.append('{}+{}+{}+{}+{}'.format(ord_move, ord_shoot, ord_bomb, ord_focus, ord_spare_2))

    ####### PUT THIS IN A SEPARATE FUNCTION - THOSE SPAGHETTI ARE PAINFUL TO LOOK AT

    surface_left.fill((128,0,0))
    surface_middle.fill((0,0,0))
    surface_right.fill((0,0,128))

    player_1_status = text.render('LIVES:{}   BOMBS:{}   SCORE:n/a'.format(player_1.lives, player_1.bombs), False, (255,255,255))
    surface_left.blit(player_1_status, (10, 10))

    player_1.draw(surface_left)
    NPC_tracker_1.draw(surface_left)
    
    try:
        order = orders.popleft()
    except:
        order = '++++'  
    client_socket.send(order.encode())
    ################

    ######### ONCE AGAIN I SHOULD PUT THIS SOMEWHERE. PLAYER CLASS? DISPLAY CLASS?

    package = client_socket.recv(4096).decode('utf8')
    npc,playa = package.split('$')
    
    coord, stat = playa.split('PLAYER_STATUS')
    player_1.recv_status(coord, stat)

    shots,bullet,sp_bullet,bomb,enemy = npc.split('NPC_STATUS')
    print(shots,bullet,sp_bullet,bomb,enemy, sep='\n', end='\n\n')
    NPC_tracker_1.recv_status(shots,bullet,sp_bullet,bomb,enemy)
    

    ##########
    

    ##### THIS CRAP IS JUST WEIRD
    screen.blit(surface, (0,0))
    pygame.display.flip()
    
    fpsClock.tick(FPS)
    
client_socket.close()
