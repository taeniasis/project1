import pygame
import time
import sys
import random
import socket as sc

from misc_func import line_move, circle_move

from collections import deque
from pygame.locals import *



###### MAYBE PUT THESE OBJECTS INTO A SEPARATE FILE TOO
###### LIKE A MODULE

class Top_tracker:
    def __init__(self, NPC_tracker, Player, surf, left, right, middle, client):
        self.NPC_tracker = NPC_tracker
        self.player = Player
        self.orders = deque([])
        
        self.surf = surf
        self.left = left
        self.right = right
        self.middle = middle
        
        self.client = client


    def get_order_to_player(self):
        self.orders.extend([self.client.recv(512).decode('utf8')])
        try:
            order = [self.orders.popleft()]
        except:
            order = ['0']
        
        self.player.recv_orders(order)
        self.player.execute_order()

    #def spawn_enemy_(...)
    #def spawn_bullet_(...)

    def display_all(self):
        self.left.fill((128,0,0))
        self.middle.fill((0,100,100))
        self.right.fill((0,0,128))

        self.NPC_tracker.draw(self.left)

        self.player.draw(self.left)
    
    def main_loop(self):

        self.NPC_tracker.update()
        self.get_order_to_player()
        
        if self.NPC_tracker.hit_player(self.player.get_hitbox()):
            self.player.iframes = 30

        if self.player.firing:
            self.NPC_tracker.add_shot(((10,10), self.player.x, self.player.y, 0, -10))
        if random.random()<0.4:   #### CRAM THIS SHIT INTO A METHOD
            self.NPC_tracker.spawn_random_bullet()
        if random.random()<0.2:  ##### THIS SHIT TOO
            self.NPC_tracker.spawn_enemy_circle_set(200,100,0,0,0.005)

        self.player.send_status(self.client)

class NPC_tracker_serverside:
    def __init__(self):
        self.player_shots = [] ## a shot is ((size_x, size_y), x, y, vx, vy)
        self.bullets = deque([]) ## each bullet is (x,y,vx,vy)
        self.bombs=[] ## each bomb is (x,y,R,ticks)
        self.delay_bombs=[] ### each delay bomb is (x,y,R,ticks,delay)
        self.enemies = [] ## each enemy is (x,y,x0,y0,w,hp)

        self.enm_side = 8
        self.side = 4
        

    def spawn_random_bullet(self):
        x = random.randrange(0, SCREEN_WIDTH)
        y = random.randrange(0, SCREEN_HEIGHT/5)
        vx = random.randrange(-3,3)
        vy = random.randrange(5, 10)
        self.bullets.append([x,y,vx,vy])


    def spawn_set_bullet(self,x,y,vx,vy):
        self.bullets.append([x,y,vx,vy])

    def add_bomb(self,bomb):
        self.bombs.append(bomb)

    def add_shot(self,shot):
        self.player_shots.append(shot)

    def spawn_enemy_circle_set(self,x,y,x0,y0,w):
        hp = 2
        self.enemies.append((x,y,x0,y0,w,hp))

            
     
    def update(self): #### REPLACE THE BOUNDARY COLLISIONS WITH ADDED CUSTOMIZABLE BOUNDARY COORDINATES FOR 2 LAYERS
        ### IM PRETTY SURE THIS PIECE OF CRAP VIOLATES THE GENEVA CONVENTION
        ### THIS SHIT IS A SUPERFUND SITE NOW
        ### EITHER WAY YOU SHOULD PUT IT SOMEWHERE ELSE
        upd_bullets = []
        for bullet in self.bullets:
            x,y,vx,vy = bullet
            x+=vx
            y+=vy
            upd_bullets.append((x,y,vx,vy))
        self.bullets = upd_bullets
        i=0
        while i<len(self.bullets):
            bullet = self.bullets[i]
            if bullet[0]<0 or bullet[0]>SCREEN_WIDTH or bullet[1]<0 or bullet[1]>SCREEN_HEIGHT:
                self.bullets.remove(bullet)
            else:
                i+=1


        upd_bombs=[]
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
                upd_bombs.append((x,y,R,ticks-1))
        self.bombs=upd_bombs


        upd_enemies = []
        for enemy in self.enemies:
            x,y,x0,y0,w,hp = enemy
            x,y = circle_move(x,y,x0,y0,w)
            upd_enemies.append((x,y,x0,y0,w,hp))
        self.enemies = upd_enemies
        i=0
        while i<len(self.enemies):
            enemy = self.enemies[i]
            if enemy[0]<0 or enemy[0]>SCREEN_WIDTH or enemy[1]<0 or enemy[1]>SCREEN_HEIGHT:
                self.enemies.remove(enemy)
            if enemy[5]<=0:
                try:
                    self.enemies.remove(enemy)
                except:
                    print('FUCK')
                self.delay_bombs.append((enemy[0], enemy[1], 20, 4, 4))
            else:
                i+=1

                
                
        enm_side = self.enm_side
        
        upd_shots = []
        for shot in self.player_shots:
            kind, x, y, vx, vy = shot
            x += vx
            y += vy
            upd_shots.append((kind,x,y,vx,vy))
        self.player_shots = upd_shots
        
        i=0
        while i<len(self.player_shots):
            shot = self.player_shots[i]
            if shot[1]<0 or shot[1]>SCREEN_WIDTH or shot[2]<0 or shot[2]>SCREEN_HEIGHT:
                self.player_shots.remove(shot)
            else:
                i+=1
                
                enemy_hitboxes = [pygame.Rect((enemy[0]-enm_side//2, enemy[1]-enm_side//2), (enm_side,enm_side)) for enemy in self.enemies]
                shot_hitbox = pygame.Rect((shot[1]-shot[0][0]//2, shot[2]-shot[0][1]//2),(shot[0][0], shot[0][1]))

                a = shot_hitbox.collidelistall(enemy_hitboxes)
                if a:
                    self.player_shots.remove(shot)

                upd_enemies = []
                for j in range(len(self.enemies)):
                    x,y,x0,y0,w,hp = self.enemies[j]
                    if j in a:
                        if hp-1<=0:
                            self.delay_bombs.append((x,y,20,4,4))
                        else:
                            upd_enemies.append((x,y,x0,y0,w,hp-1))
                    else:
                        upd_enemies.append((x,y,x0,y0,w,hp))
                self.enemies = upd_enemies

        for bomb in self.bombs:
            X,Y,R,ticks = bomb

            upd_enemies = []
            for x,y,x0,y0,w,hp in self.enemies:
                if (X-x)**2+(Y-y)**2<R**2:
                    upd_enemies.append((x,y,x0,y0,w,hp-2))
                else:
                    upd_enemies.append((x,y,x0,y0,w,hp))
            self.enemies=upd_enemies

        upd_delay_bombs = []
        for x,y,R,ticks,delay in self.delay_bombs:
            if delay>0:
                upd_delay_bombs.append((x,y,R,ticks,delay-1))
            else:
                self.bombs.append((x,y,R,ticks))
        self.delay_bombs = upd_delay_bombs
            
            
            
            
            

            
    def draw(self, surf):
        for bullet in self.bullets:
            pygame.draw.circle(surf, (100,0,100), (int(bullet[0]), int(bullet[1])), 5)
        for bomb in self.bombs:
            pygame.draw.circle(surf, (100,100,100), (int(bomb[0]), int(bomb[1])), bomb[2])
        for enemy in self.enemies:
            pygame.draw.circle(surf, (200,200,0), (int(enemy[0]), int(enemy[1])), 10)
        for shot in self.player_shots:
            pygame.draw.rect(surf, (255,255,255), pygame.Rect((shot[1]-6, shot[2]-6),(12,12)))
            

    #def hit_enemies(self):
        

    def hit_player(self, player_hitbox):  ### player_hitbox is a square with coordinates of player, fixed side
        side = 4
        enm_side = 6
        bullet_hitboxes = [pygame.Rect(( bullet[0]-side//2, bullet[1]-side//2), (side,side)) for bullet in self.bullets]
        enemy_hitboxes = [pygame.Rect((enemy[0]-enm_side//2, enemy[1]-enm_side//2), (enm_side,enm_side)) for enemy in self.enemies]

        return bool((player_hitbox.collidelist(bullet_hitboxes)+1) + (player_hitbox.collidelist(enemy_hitboxes)+1))

    
class Player_serverside:
    def __init__(self, bullet_tracker, surf, shot_type='trapezoid'):
        self.x = SCREEN_WIDTH // 4
        self.y = SCREEN_HEIGHT // 2
        self.order_queue = deque([])
        
        self.firing = False
        self.cooldown = 0
        self.lives = 3
        self.speed = 5
        self.gauge = 0
        self.iframes = 0
        self.bomb_timeout = 0
        self.bombs = 5
        
        
        self.shot_type = shot_type
        self.bullet_tracker = bullet_tracker
##        self.surf = surf


    def fire_trapezoid(self, surf):
        pygame.draw.polygon(surf, (40,40,40), [(self.x-5, self.y-10),(self.x+5, self.y-10),(self.x+30, self.y-100),(self.x-30, self.y-100)])

    def fire_lazer(self, surf):
        pygame.draw.polygon(surf, (40,40,40), [(self.x-2,self.y-10),(self.x+2, self.y-10),(self.x+2,0), (self.x-2,0)])


    def bomb_test(self):
        if self.bombs>0:
            self.bombs-=1
            self.bullet_tracker.add_bomb((int(self.x), int(self.y), 200, 90))

                                
    def get_hitbox(self):
        side = 8
        if self.iframes==0:
            return pygame.Rect((self.x-side//2, self.y-side//2), (side, side))
        else:
            return pygame.Rect((-100,-100), (0,0))

 
    
    def draw(self, surf):
        r = pygame.Rect((self.x-5, self.y-10), (10,20))
        if self.iframes==0:
            pygame.draw.rect(surf, (20,0,0), r)
        else:
            pygame.draw.rect(surf, (100,100,100), r)
            self.iframes-=1
##        if self.firing:
##            self.fire_trapezoid(surf)

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

        self.firing = False
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

        if ord_shoot=='SHOOT' and self.cooldown==0:
            self.firing = True
            self.cooldown = 5

        if ord_bomb=='BOMB' and self.bomb_timeout==0:
            self.bomb_timeout = 60
            self.bomb_test()

        if self.bomb_timeout>0:
            self.bomb_timeout-=1

        if self.cooldown>0:
            self.cooldown-=1
            
        self.speed = 5

        

    def send_status(self, connection):
        '''
            send your own status through connection
        '''
        
        package = str(self.x) + ',' + str(self.y)
        connection.send(package.encode())


#### MAYBE SEPARATE THIS SHIT INTO CONFIG AND SETUP COMMANDS
###THEN PUT INTO SEPARATE FILE
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

surface_left = surface.subsurface(0,0,SCREEN_WIDTH//2-50, SCREEN_HEIGHT)
surface_middle = surface.subsurface(SCREEN_WIDTH//2-50, 0, 100, SCREEN_HEIGHT)
surface_right = surface.subsurface(SCREEN_WIDTH//2+50, 0, SCREEN_WIDTH//2-50, SCREEN_HEIGHT)

surface_left.fill((128,0,0))
surface_middle.fill((0,100,100))
surface_right.fill((0,0,128))

pygame.key.set_repeat(1, 10)
########

NPC_TRACKER = NPC_tracker_serverside()
PLAYER = Player_serverside(NPC_TRACKER, surface_left, shot_type='trapezoid')
TOP_TRACKER = Top_tracker(NPC_TRACKER, PLAYER, surface, surface_left, surface_right, surface_middle, client)

running=True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            server_socket.close()
            running = False
            break
    
    TOP_TRACKER.display_all()
    TOP_TRACKER.main_loop()
    screen.blit(surface, (0,0))
    pygame.display.flip()





















 