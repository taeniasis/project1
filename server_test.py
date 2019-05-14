import pygame
import time
import sys
import random
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

##def draw_rec(surf, color, pos):
##    r = pygame.Rect((pos[0]-20, pos[1]-20), (40,40))
##    pygame.draw.rect(surf, color, r)

##def draw_circle(surf, color, pos):
##    pygame.draw.circle(surf, color, pos, 5)
##########################

class Projectile_tracker_serverside:
    def __init__(self):
        self.bullets = deque([]) ## each bullet is (x,y,vx,vy)
        self.bombs=[] ## each bomb is x,y,R,ticks
        self.sprites = []
        self.side = 4
        

    def spawn_random(self):
        x = random.randrange(0, SCREEN_WIDTH)
        y = random.randrange(0, SCREEN_HEIGHT/5)
        vx = random.randrange(-3,3)
        vy = random.randrange(5, 10)
        self.bullets.append([x,y,vx,vy])

    def spawn_set(self,x,y,vx,vy):
        self.bullets.append([x,y,vx,vy])

    def add_bomb(self,bomb):
        self.bombs.append(bomb)            
    
    def update(self):
        i = 0
        while i<len(self.bullets):
            bullet = self.bullets[i]
            bullet[0]+=bullet[2]
            bullet[1]+=bullet[3]
            if bullet[0]<0 or bullet[0]>SCREEN_WIDTH or bullet[1]<0 or bullet[1]>SCREEN_HEIGHT:
                self.bullets.remove(bullet)
            else:
               i+=1

        new_bombs=[]
        for bomb in self.bombs:
            x, y, R, ticks = bomb
            i = 0
            while i<len(self.bullets):
                bullet = self.bullets[i]
                if (bullet[0]-x)**2+(bullet[1]-y)**2<R**2:
                    self.bullets.remove(bullet)
                else:
                    i+=1
            if ticks>1:
                new_bombs.append((x,y,R,ticks-1))
        self.bombs=new_bombs

            
    def draw(self,surf):
        for bullet in self.bullets:
            pygame.draw.circle(surf, (100,0,100), (bullet[0], bullet[1]), 5)
        for bomb in self.bombs:
            pygame.draw.circle(surf, (100,100,100), (bomb[0], bomb[1]), bomb[2])
            

    def hit_player(self, player_hitbox):  ### player_hitbox is a square with coordinates of player, fixed side
        bullet_hitboxes = [pygame.Rect(( bullet[0]-self.side//2, bullet[1]-self.side//2), (self.side,self.side)) for bullet in self.bullets]
        return bool(player_hitbox.collidelist(bullet_hitboxes)+1)

    



#### A TRYOUT FOR PLAYER OBJECT ON SERVER
### I LIKE THE IDEA OF ONLY USING THE PLAYER OBJECT FOR TAKING AND EXECUTING ORDERS
#### I SHOULD KEEP IT THAT WAY
class Player_serverside:
    def __init__(self, surf):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.order_queue = deque([])
        self.lives = 3
        self.speed = 5
        self.gauge = 0
        self.invincible = False
        self.iframes = 0
        self.bombs = 5

        self.surf = surf


    def fire_trapezoid(self):
        pygame.draw.polygon(self.surf, (40,40,40), [(self.x-5, self.y-10),(self.x+5, self.y-10),(self.x+30, self.y-50),(self.x-30, self.y-50)])

    def bomb_test(self, bullet_tracker):
        if self.bombs>0:
            self.bombs-=1
            bullet_tracker.add_bomb((int(self.x), int(self.y), 200, 90))
                                
    def get_hitbox(self):
        side = 8
        if self.iframes==0:
            return pygame.Rect((self.x-side//2, self.y-side//2), (side, side))
        else:
            return pygame.Rect((-100,-100), (0,0))
    
    def draw(self):
        r = pygame.Rect((self.x-5, self.y-10), (10,20))
        if self.iframes==0:
            pygame.draw.rect(self.surf, (20,0,0), r)
        else:
            pygame.draw.rect(self.surf, (100,100,100), r)
            self.iframes-=1

    def recv_orders(self, orders):
        '''
            extend my order queue with list - "orders".

            orders is a list of strings with instructions like UP, DOWN, LEFT, RIGHT, LOSE etc etc
        '''
        self.order_queue.extend(orders)

    def execute_order(self, bullet_tracker):
        '''
            get an order from queue and execute it
        '''
        order = self.order_queue.popleft()

        ord_move, ord_shoot, ord_bomb, ord_focus, ord_spare_2 = order.split('+')

        if ord_focus=='FOCUS':
            self.speed = 2
        
        if ord_move=='UP':
            self.y -= self.speed
        elif ord_move=='DOWN':
            self.y += self.speed
        elif ord_move=='LEFT':
            self.x -= self.speed
        elif ord_move=='RIGHT':
            self.x += self.speed
        elif ord_move=='UP-LEFT':
            self.y -= self.speed/1.42
            self.x -= self.speed/1.42
        elif ord_move=='UP-RIGHT':
            self.y -= self.speed/1.42
            self.x += self.speed/1.42
        elif ord_move=='DOWN-LEFT':
            self.y += self.speed/1.42
            self.x -= self.speed/1.42
        elif ord_move=='DOWN-RIGHT':
            self.y += self.speed/1.42
            self.x += self.speed/1.42

        self.speed = 5

        if ord_shoot=='SHOOT':
            self.fire_trapezoid()

        if ord_bomb=='BOMB':
            self.bomb_test(bullet_tracker)


                
        

    def send_status(self, connection):
        '''
            send your own status through connection
        '''
        
        package = str(self.x) + ',' + str(self.y)
        connection.send(package.encode())
 
####################
running = True
player = Player_serverside(surface)
bullet_tracker = Projectile_tracker_serverside()

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
    
    player.draw()
    bullet_tracker.draw(surface)
    
    orders.extend([client.recv(512).decode('utf8')])
    try:
        order = [orders.popleft()]
    except:
        order = ['0']
    player.recv_orders(order)
    player.execute_order(bullet_tracker)
    
    if bullet_tracker.hit_player(player.get_hitbox()):
        player.iframes = 30
##        pygame.quit()
##        sys.exit()
##        server_socket.close()

    ####### MORE SHIT TO ORGANIZE
    if random.random()<0.4:
        bullet_tracker.spawn_random()
        #bullet_tracker.spawn_set(100,100,0,0)
    bullet_tracker.update()

    player.send_status(client)

    player.draw()
    ###############



    #######
    

    ##### THIS CRAP IS JUST WEIRD
    screen.blit(surface, (0,0))
    pygame.display.flip()
    
    fpsClock.tick(FPS)
