import pygame
import time
import sys
import socket as sc

from collections import deque
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
surface.fill((64,128,128))

pygame.key.set_repeat(1, 10)

def draw_box(surf, color, pos):
    r = pygame.Rect((pos[0], pos[1]), (10,10))
    pygame.draw.rect(surf, color, r)

#####################

class Player_clientside:
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.order_queue = deque([])
        
        
    def draw(self,surf):
        ### if self.x!=None and self.y!=None:
        draw_box(surf, (20,0,0), (self.x,self.y))

    def recv_status(self, connection):
        package = connection.recv(512).decode('utf8')
        x, y = package.split(',')
        self.x, self.y = float(x), float(y)

    ### as stated below it might be beneficial to cram all the input shit into 
    ### some methods here. It might cause pygame to throw a shitfit though



################
running = True
player = Player_clientside()
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
        ord_shoot='BOMB'

    if keys[K_LSHIFT]:
        ord_focus='FOCUS'

    
    orders.append('{}+{}+{}+{}+{}'.format(ord_move, ord_shoot, ord_bomb, ord_focus, ord_spare_2))

    ####### PUT THIS IN A SEPARATE FUNCTION - THOSE SPAGHETTI ARE PAINFUL TO LOOK AT
    surface.fill((64,128,128))
    player.draw(surface)
    
    try:
        order = orders.popleft()
    except:
        order = '++++'  
    client_socket.send(order.encode())
    ################

    ######### ONCE AGAIN I SHOULD PUT THIS SOMEWHERE. PLAYER CLASS? DISPLAY CLASS?

    player.recv_status(client_socket)

    ##########
    

    ##### THIS CRAP IS JUST WEIRD
    screen.blit(surface, (0,0))
    pygame.display.flip()
    
    fpsClock.tick(FPS)
    
