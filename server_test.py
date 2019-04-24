import pygame
import time
import sys
import socket as sc

from collections import deque
from pygame.locals import *


########## PUT THIS BULLSHIT IN A SEPARATE FILE AND IMPORT AND EXECUTE IT
server_socket = sc.socket()
server_socket.bind(('', 9101))
server_socket.listen(1)
client, client_address = server_socket.accept()


FPS = 60
pygame.init()
pygame.display.set_caption('SERVER')
fpsClock=pygame.time.Clock()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
surface = pygame.Surface(screen.get_size())
surface.fill((64,128,128))


pygame.key.set_repeat(1, 10)

def draw_box(surf, color, pos):
    r = pygame.Rect((pos[0], pos[1]), (10,10))
    pygame.draw.rect(surf, color, r)
##########################
    


#### A TRYOUT FOR PLAYER OBJECT ON SERVER
class Player_serverside:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.order_queue = deque([])
        
    def draw(self,surf):
        draw_box(surf, (20,0,0), (self.x,self.y))

    def recv_orders(self, orders):
        '''
            extend my order queue with list - "orders".

            orders is a list of strings with instructions like UP, DOWN, LEFT, RIGHT, LOSE etc etc
        '''
        self.order_queue.extend(orders)

    def execute_order(self):
        '''
            get an order from queue and execute it
        '''
        order = self.order_queue.popleft()

        if order=='UP':
            self.y -= 5
        elif order=='DOWN':
            self.y += 5
        elif order=='LEFT':
            self.x -= 5
        elif order=='RIGHT':
            self.x += 5
        elif order=='UP-LEFT':
            self.y -= 5/1.42
            self.x -= 5/1.42
        elif order=='UP-RIGHT':
            self.y -= 5/1.42
            self.x += 5/1.42
        elif order=='DOWN-LEFT':
            self.y += 5/1.42
            self.x -= 5/1.42
        elif order=='DOWN-RIGHT':
            self.y += 5/1.42
            self.x += 5/1.42

    def send_status(self, connection):
        '''
            send your own status through connection
        '''
        
        package = str(self.x) + ',' + str(self.y)
        connection.send(package.encode())
 
####################
running = True
player = Player_serverside()
orders = deque([])

##### MAYBE MAKE THE DISPLAY A SEPARATE OBJECT..?
##### MAKE A FANCY-ASS IF NAME==__MAIN__ CRAP OF THIS
while running:

    ####### THIS BABY MAY NEED A SEPARATE FUNCTION
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            server_socket.close()
            running = False
            break


    ######### PUT THIS IN A SEPARATE FUNCTION - THOSE SPAGHETTI ARE PAINFUL TO LOOK AT
    ##### ALSO THE INPUT/ORDERS MAY BE BETTER INSIDE A PLAYER_SERVERSIDE METHOD
    surface.fill((64,128,128))
    player.draw(surface)
    
    orders.extend([client.recv(512).decode('utf8')])
    try:
        order = [orders.popleft()]
    except:
        order = ['0']
    player.recv_orders(order)
    player.execute_order()

    player.send_status(client)
    ###############



    #######
    

    ##### THIS CRAP IS JUST WEIRD
    screen.blit(surface, (0,0))
    pygame.display.flip()
    
    fpsClock.tick(FPS)
