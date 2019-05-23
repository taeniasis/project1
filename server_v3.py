import pygame
import time
import sys
import random
import socket as sc

from misc_func import line_move, circle_move

from collections import deque
from codndecode import code1
from pygame.locals import *


###### MAYBE PUT THESE OBJECTS INTO A SEPARATE FILE TOO
###### LIKE A MODULE
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 120

class Game_phase_tracker:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('SERVER')
        self.fpsClock=pygame.time.Clock()


        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface = pygame.Surface(self.screen.get_size())

        self.surface_left = self.surface.subsurface(0,0,SCREEN_WIDTH//2-50, SCREEN_HEIGHT)
        self.surface_middle = self.surface.subsurface(SCREEN_WIDTH//2-50, 0, 100, SCREEN_HEIGHT)
        self.surface_right = self.surface.subsurface(SCREEN_WIDTH//2+50, 0, SCREEN_WIDTH//2-50, SCREEN_HEIGHT)

        pygame.key.set_repeat(1, 10)
        
        self.phase = 'PREP'
    def prep_phase(self):
        title_text = pygame.font.SysFont('Calibri', 40)
        first_text = title_text.render('Awaiting connection...', False, (255,255,255))
    
        self.surface.fill((0,128,128))
        self.surface.blit(first_text, (SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2))
        self.screen.blit(self.surface, (0,0))

        pygame.display.flip()

        self.server_socket_1 = sc.socket()
        self.server_socket_1.bind(('', 9101))
        self.server_socket_1.listen(1)
        self.client_1, self.client_address_1 = self.server_socket_1.accept()

        self.server_socket_2 = sc.socket()
        self.server_socket_2.bind(('', 9102))
        self.server_socket_2.listen(1)
        self.client_2, self.client_address_2 = self.server_socket_2.accept()
        
        
        self.phase='GAME'
        
    def game_phase(self):
        NPC_TRACKER_1, NPC_TRACKER_2 = NPC_tracker_serverside(1), NPC_tracker_serverside(2)

        PLAYER_1 = Player_serverside(NPC_TRACKER_1)
        PLAYER_2 = Player_serverside(NPC_TRACKER_2)
        self.TOP_TRACKER = Top_tracker(NPC_TRACKER_1, NPC_TRACKER_2, PLAYER_1, PLAYER_2, self.surface, self.surface_left, self.surface_right, self.surface_middle, self.client_1, self.client_2)

        while not self.TOP_TRACKER.loss:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    self.server_socket.close()

            if not self.TOP_TRACKER.loss:
                self.TOP_TRACKER.display_all()
                self.TOP_TRACKER.main_loop_progressive()
                self.screen.blit(self.surface, (0,0))
                pygame.display.flip()
                self.fpsClock.tick(FPS)

                

        self.phase='END'
    def end_phase(self):
##        title_text = pygame.font.SysFont('Calibri', 40)
##        if self.TOP_TRACKER.loss==1:
##            last_text = title_text.render('Player 2 won', False, (255,255,255))
##        if self.TOP_TRACKER.loss==2:
##            last_text = title_text.render('Player 1 won', False, (255,255,255))
##        elif self.TOP_TRACKER.loss==3:
##            last_text = title_text.render('DRAW', False, (255,255,255))
##        else:
##            last_text = title_text.render('SOMETHING WENT WRONG', False, (255,255,255))
##
##        for i in range(300):
##            if self.TOP_TRACKER.loss==1:
##                self.surface.fill((0,0,128))
##            elif self.TOP_TRACKER.loss==2:
##                self.surface.fill((128,0,0))
##            elif self.TOP_TRACKER.loss==3:
##                self.surface.fill((200,0,200))
##            else:
##                self.surface.fill((0,0,0))
##                
##            self.surface.blit(last_text, (SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2))
##            self.screen.blit(self.surface, (0,0))
##
##            pygame.display.flip()

        
        self.server_socket_1.close()
        pygame.quit()
        sys.exit()

        
        
        
        
##  THIS BULLSHIT I'LL USE FOR TRACKING WHAT KIND OF DISPLAY TO DRAW
## AS IN: MAIN MENU, CHAR SELECT, GAME, RESULTS AND SO ON

class Top_tracker:
    def __init__(self, NPC_tracker_1, NPC_tracker_2, Player_1, Player_2, surf, left, right, middle, client_1, client_2):
        self.NPC_tracker_1 = NPC_tracker_1
        self.NPC_tracker_2 = NPC_tracker_2
        
        self.player_1 = Player_1
        self.player_2 = Player_2
        
        self.orders_1 = deque([])
        self.orders_2 = deque([])
        
        self.surf = surf
        self.left = left
        self.right = right
        self.middle = middle
        
        self.client_1 = client_1
        self.client_2 = client_2

        self.clock = 0
        self.loss = 0
        pygame.font.init()
        self.text = pygame.font.SysFont('Calibri', 20)

        


    def get_order_to_players(self):
        try:
            self.orders_1.append(self.client_1.recv(64).decode('utf8'))
            self.orders_2.append(self.client_2.recv(64).decode('utf8'))
        except:
            self.orders_1.append('++++')
            self.orders_2.append('++++')
            time.sleep(0.01)
        try:
            order_1 = [self.orders_1.popleft()]
        except:
            order_1 = ['++++']

        try:
            order_2 = [self.orders_2.popleft()]
        except: 
            order_2 = ['++++']
            
        
        self.player_1.recv_orders(order_1)
        self.player_1.execute_order()

        self.player_2.recv_orders(order_2)
        self.player_2.execute_order()
        
    
    #def spawn_enemy_(...)
    #def spawn_bullet_(...)

    def display_all(self):
        self.left.fill((255, 179, 179))
        self.middle.fill((0,0,0))
        self.right.fill((179, 179, 255))

        player_1_status = self.text.render('LIVES:{}   BOMBS:{}   SCORE:{}'.format(self.player_1.lives, self.player_1.bombs, self.NPC_tracker_1.score), False, (255,255,255))
        self.left.blit(player_1_status, (10, 10))
        player_2_status = self.text.render('LIVES:{}   BOMBS:{}   SCORE:{}'.format(self.player_2.lives, self.player_2.bombs, self.NPC_tracker_2.score), False, (255,255,255))
        self.right.blit(player_2_status, (10, 10))
        diff_status = self.text.render('LEVEL:{:.3f}'.format(self.clock/3600), False, (255,255,255))
        self.middle.blit(diff_status, (0,0))
        
        self.NPC_tracker_1.draw(self.left)
        self.NPC_tracker_2.draw(self.right)

        self.player_1.draw(self.left)
        self.player_2.draw(self.right)
    
    def main_loop(self, BULLET_PROB, BULLET_INIT, ENEMY_PROB):
        self.clock+=1
        
        if self.player_1.lives<0 and self.player_2.lives>=0:
            self.loss = 1
        elif self.player_1.lives>=0 and self.player_2.lives<0:
            self.loss = 2
        elif self.player_1.lives<0 and self.player_2.lives<0:
            self.loss = 3 ## a draw - shouldn't be possible
            
        sent_to_2 = self.NPC_tracker_1.update()
        sent_to_1 = self.NPC_tracker_2.update()

        for i in range(sent_to_2):
            self.NPC_tracker_2.spawn_random_bullet_delay((-2,2),(2,4))
        for i in range(sent_to_1):
            self.NPC_tracker_1.spawn_random_bullet_delay((-2,2),(2,4))
            
        self.get_order_to_players()
        
        if self.NPC_tracker_1.hit_player(self.player_1.get_hitbox()) and self.player_1.iframes<=0:
            self.player_1.iframes = 120
            self.player_1.lives-=1
            self.NPC_tracker_1.add_bomb((self.player_1.x, self.player_1.y, 300, 30))
        if self.NPC_tracker_1.score>self.NPC_tracker_1.bomb_score:
            self.player_1.bombs+=1
            self.NPC_tracker_1.bomb_score+=1000
            
        if self.NPC_tracker_2.hit_player(self.player_2.get_hitbox()) and self.player_2.iframes<=0:
            self.player_2.iframes = 120
            self.player_2.lives-=1
            self.NPC_tracker_2.add_bomb((self.player_2.x, self.player_2.y, 300, 30))
        if self.NPC_tracker_2.score>self.NPC_tracker_2.bomb_score:
            self.player_2.bombs+=1
            self.NPC_tracker_2.bomb_score+=1000

        if self.player_1.firing: ## add customizable shots for players
            self.NPC_tracker_1.add_shot((10,10, self.player_1.x, self.player_1.y, 0, -10))
        if self.player_2.firing:
            self.NPC_tracker_2.add_shot((10,10, self.player_2.x, self.player_2.y, 0, -10))
            
        if random.random()<BULLET_PROB:   #### CRAM THIS SHIT INTO A METHOD
            self.NPC_tracker_1.spawn_random_bullet_delay(BULLET_INIT[0],BULLET_INIT[1])
        if random.random()<BULLET_PROB:
            self.NPC_tracker_2.spawn_random_bullet_delay(BULLET_INIT[0],BULLET_INIT[1])
        if random.random()<ENEMY_PROB:  ##### THIS SHIT TOO
            CHOICE = random.random()
            if CHOICE<0.125:
                self.NPC_tracker_1.enemy_pattern_1_left()
            if CHOICE>0.125 and CHOICE<0.25:
                self.NPC_tracker_1.enemy_pattern_2_left()
            if CHOICE>0.25 and CHOICE<0.375:
                self.NPC_tracker_1.enemy_pattern_3_left()
            if CHOICE>0.375 and CHOICE<0.5:
                self.NPC_tracker_1.enemy_pattern_4_left()
            if CHOICE>0.5 and CHOICE<0.625:
                self.NPC_tracker_1.enemy_pattern_1_right()
            if CHOICE>0.625 and CHOICE<0.75:
                self.NPC_tracker_1.enemy_pattern_2_right()
            if CHOICE>0.75 and CHOICE<0.875:
                self.NPC_tracker_1.enemy_pattern_3_right()
            if CHOICE>0.875:
                self.NPC_tracker_1.enemy_pattern_4_right()
        if random.random()<ENEMY_PROB:  ##### THIS SHIT TOO
            CHOICE = random.random()
            if CHOICE<0.125:
                self.NPC_tracker_2.enemy_pattern_1_left()
            if CHOICE>0.125 and CHOICE<0.25:
                self.NPC_tracker_2.enemy_pattern_2_left()
            if CHOICE>0.25 and CHOICE<0.375:
                self.NPC_tracker_2.enemy_pattern_3_left()
            if CHOICE>0.375 and CHOICE<0.5:
                self.NPC_tracker_2.enemy_pattern_4_left()
            if CHOICE>0.5 and CHOICE<0.625:
                self.NPC_tracker_2.enemy_pattern_1_right()
            if CHOICE>0.625 and CHOICE<0.75:
                self.NPC_tracker_2.enemy_pattern_2_right()
            if CHOICE>0.75 and CHOICE<0.875:
                self.NPC_tracker_2.enemy_pattern_3_right()
            if CHOICE>0.875:
                self.NPC_tracker_2.enemy_pattern_4_right()


        try:
            self.client_1.send(self.pack_state().encode())
            self.client_2.send(self.pack_state().encode())
        except:
            print('Ай мля я маслину поймал')

    def main_loop_progressive(self):
        if 4*self.clock/3600<=1:
            self.main_loop(0.1, ((-2,2),(2,4)), 0.01)
        elif 4*self.clock/3600>1 and 4*self.clock/3600<=2:
            self.main_loop(0.2, ((-3,3),(2,4)), 0.01)
        elif 4*self.clock/3600>2 and 4*self.clock/3600<=3:
            self.main_loop(0.4, ((-3,3),(2,5)), 0.01)
        elif 4*self.clock/3600>3 and 4*self.clock/3600<=4:
            self.main_loop(0.6, ((-3,3),(2,5)), 0.01)
        elif 4*self.clock/3600>4 and 4*self.clock/3600<=5:
            self.main_loop(0.7, ((-3,3),(2,5)), 0.01)
        else:
            self.main_loop(0.7, ((-3,3),(3,7)), 0.01)

    def pack_state(self):
        NPC_1_status = self.NPC_tracker_1.pack_status()
        Player_1_status = self.player_1.pack_status()

        Player_2_status = self.player_2.pack_status()
        NPC_2_status = self.NPC_tracker_2.pack_status()
        
        return '$'.join((NPC_1_status, Player_1_status, NPC_2_status, Player_2_status, str(self.clock), str(self.loss)))
        

class NPC_tracker_serverside:
    def __init__(self, PLAYER):
        self.player_shots = [] ## a shot is (size_x, size_y, x, y, vx, vy)

        self.spawning_bullets = deque([]) ### each delay_bullet is (x,y,vx,vy, delay)
        self.bullets = deque([]) ## each bullet is (x,y,vx,vy)
        
        self.bombs=deque([]) ## each bomb is (x,y,R,ticks)
        self.delay_bombs=deque([]) ### each delay bomb is (x,y,R,ticks,delay)
        
        self.enemies = deque([]) ## each enemy is (x,y,x0,y0,w,hp)

        self.score = 0
        self.bomb_score = 1000

        self.enm_side = 8
        self.side = 4

        self.left = 0
        self.right = SCREEN_WIDTH//2-50
##        if PLAYER==1:
##            self.left = 0
##            self.right = SCREEN_WIDTH//2-50
##        elif PLAYER==2:
##            self.left = SCREEN_WIDTH//2+50
##            self.right = SCREEN_WIDTH

##    def spawn_random_bullet(self):
##        x = random.randrange(0, SCREEN_WIDTH)
##        y = random.randrange(0, SCREEN_HEIGHT/5)
##        vx = random.randrange(-3,3)
##        vy = random.randrange(5, 10)
##        self.bullets.append((x,y,vx,vy))

    def spawn_random_bullet_delay(self, vx_r, vy_r):
        x = random.randrange(self.left, self.right)
        y = random.randrange(0, SCREEN_HEIGHT/5)
        vx = random.randrange(vx_r[0],vx_r[1])
        vy = random.randrange(vy_r[0], vy_r[1])
        delay = 6
        self.spawning_bullets.append((x,y,vx,vy, delay))

    def spawn_set_bullet_delay(self,x,y,vx,vy):
        self.spawning_bullets.append((x,y,vx,vy,6))

    def add_bomb(self,bomb):
        self.bombs.append(bomb)

    def add_shot(self,shot):
        self.player_shots.append(shot)

##    def spawn_enemy_circle_set(self,x,y,x0,y0,w):
##        hp = 2
##        self.enemies.append((x,y,x0,y0,w,hp))

    def enemy_pattern_1_left(self): # A LINE OF ENEMIES COMING FROM THE MIDDLE LEFT
        self.enemies.extend([(0,SCREEN_HEIGHT//2, SCREEN_WIDTH//2, -5000, -0.0003, 2),
                             (-30,SCREEN_HEIGHT//2, SCREEN_WIDTH//2, -5000, -0.0003, 2),
                             (-60,SCREEN_HEIGHT//2, SCREEN_WIDTH//2, -5000, -0.0003, 2),
                             (-90,SCREEN_HEIGHT//2, SCREEN_WIDTH//2, -5000, -0.0003, 2),
                             (-120,SCREEN_HEIGHT//2, SCREEN_WIDTH//2, -5000, -0.0003, 2),
                             (-150,SCREEN_HEIGHT//2, SCREEN_WIDTH//2, -5000, -0.0003, 2)])
        
    def enemy_pattern_1_right(self): # A LINE OF ENEMIES COMING FROM THE MIDDLE RIGHT
        L = SCREEN_WIDTH//2-50
        self.enemies.extend([(L,70+SCREEN_HEIGHT//2, SCREEN_WIDTH//2, -5000, 0.0003, 2),
                             (L+30,70+SCREEN_HEIGHT//2, SCREEN_WIDTH//2, -5000, 0.0003, 2),
                             (L+60,70+SCREEN_HEIGHT//2, SCREEN_WIDTH//2, -5000, 0.0003, 2),
                             (L+90,70+SCREEN_HEIGHT//2, SCREEN_WIDTH//2, -5000, 0.0003, 2),
                             (L+120,70+SCREEN_HEIGHT//2, SCREEN_WIDTH//2, -5000, 0.0003, 2),
                             (L+150,70+SCREEN_HEIGHT//2, SCREEN_WIDTH//2, -5000, 0.0003, 2)])
        

    def enemy_pattern_2_left(self): ### AN ARC OF ENEMIES COMING FROM TOP LEFT
        self.enemies.extend([(0, 0, SCREEN_WIDTH//3, 0, -0.005, 2),
                             (2, -30, SCREEN_WIDTH//3, 0, -0.005, 2),
                            (8, -60, SCREEN_WIDTH//3, 0, -0.005, 2),
                            (14, -85, SCREEN_WIDTH//3, 0, -0.005, 2),
                             (25, -110, SCREEN_WIDTH//3, 0, -0.005, 2),
                             (35, -135, SCREEN_WIDTH//3, 0, -0.005, 2)])

    def enemy_pattern_2_right(self): ### AN ARC OF ENEMIES COMING FROM TOP RIGHT
        L = SCREEN_WIDTH//2-50
        self.enemies.extend([(L, 0, L-SCREEN_WIDTH//3, 0, 0.005, 2),
                             (L-2, -30, L-SCREEN_WIDTH//3, 0, 0.005, 2),
                            (L-8, -60, L-SCREEN_WIDTH//3, 0, 0.005, 2),
                            (L-14, -85, L-SCREEN_WIDTH//3, 0, 0.005, 2),
                             (L-25, -110, L-SCREEN_WIDTH//3, 0, 0.005, 2),
                             (L-35, -135, L-SCREEN_WIDTH//3, 0, 0.005, 2)])

        
    def enemy_pattern_3_left(self): ### AN ARC OF ENEMIES COMING FROM TOP LEFT GETTING CLOSER TO PLAYER
        self.enemies.extend([(-30, -28, 0, SCREEN_HEIGHT//3, 0.01, 2),
                             (0, -30, 0, SCREEN_HEIGHT//3, 0.01, 2),
                             (30, -28, 0, SCREEN_HEIGHT//3, 0.01, 2),
                             (60, -22, 0, SCREEN_HEIGHT//3, 0.01, 2),
                             (83, -14, 0, SCREEN_HEIGHT//3, 0.01, 2),
                             (114, 0, 0, SCREEN_HEIGHT//3, 0.01, 2)])

        
    def enemy_pattern_3_right(self): ### AN ARC OF ENEMIES COMING FROM TOP RIGHT GETTING CLOSER TO PLAYER
        L = SCREEN_WIDTH//2-50
        self.enemies.extend([(L+30, -28, L, SCREEN_HEIGHT//3, -0.01, 2),
                             (L, -30, L, SCREEN_HEIGHT//3, -0.01, 2),
                             (L-30, -28, L, SCREEN_HEIGHT//3, -0.01, 2),
                             (L-60, -22, L, SCREEN_HEIGHT//3, -0.01, 2),
                             (L-83, -14, L, SCREEN_HEIGHT//3, -0.01, 2),
                             (L-114, 0, L, SCREEN_HEIGHT//3, -0.01, 2)])

    def enemy_pattern_4_left(self): ### AN ARC OF ENEMIES COMING FROM LOWER LEFT
        H = SCREEN_HEIGHT
        self.enemies.extend([(0, H, SCREEN_WIDTH//3, H, 0.005, 2),
                             (2, H+30, SCREEN_WIDTH//3, H, 0.005, 2),
                            (8, H+60, SCREEN_WIDTH//3, H, 0.005, 2),
                            (14, H+85, SCREEN_WIDTH//3, H, 0.005, 2),
                             (25, H+110, SCREEN_WIDTH//3, H, 0.005, 2),
                             (35, H+135, SCREEN_WIDTH//3, H, 0.005, 2)])

    def enemy_pattern_4_right(self): ### AN ARC OF ENEMIES COMING FROM LOWER RIGHT
        L = SCREEN_WIDTH//2-50
        H = SCREEN_HEIGHT
        self.enemies.extend([(L, H, L-SCREEN_WIDTH//3, H, -0.005, 2),
                             (L-2, H+30, L-SCREEN_WIDTH//3, H, -0.005, 2),
                            (L-8, H+60, L-SCREEN_WIDTH//3, H, -0.005, 2),
                            (L-14, H+85, L-SCREEN_WIDTH//3, H, -0.005, 2),
                             (L-25, H+110, L-SCREEN_WIDTH//3, H, -0.005, 2),
                             (L-35, H+135, L-SCREEN_WIDTH//3, H, -0.005, 2)])
        

            
     
    def update(self):
        ### IM PRETTY SURE THIS PIECE OF CRAP VIOLATES THE GENEVA CONVENTION
        ### THIS SHIT IS A SUPERFUND SITE NOW
        ### EITHER WAY YOU SHOULD PUT IT SOMEWHERE ELSE
        sent_bullets = 0
        
        upd_spawning_bullets=[]
        for x,y,vx,vy,delay in self.spawning_bullets:
            if delay>0:
                upd_spawning_bullets.append((x,y,vx,vy,delay-1))
            else:
                self.bullets.append((x,y,vx,vy))
        self.spawning_bullets = upd_spawning_bullets
            

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
            if bullet[0]<self.left or bullet[0]>self.right or bullet[1]<0 or bullet[1]>SCREEN_HEIGHT:
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
                    sent_bullets+=1
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
            if enemy[0]<self.left-150 or enemy[0]>self.right+150 or enemy[1]<-150 or enemy[1]>SCREEN_HEIGHT+150:
                self.enemies.remove(enemy)
            if enemy[5]<=0:
                try:
                    self.enemies.remove(enemy)
                    self.score+=10
                except:
                    print('FUCK')
                self.delay_bombs.append((enemy[0], enemy[1], 40, 4, 4))
            else:
                i+=1

                
                
        enm_side = self.enm_side
        
        upd_shots = []
        for shot in self.player_shots:
            size_x,size_y, x, y, vx, vy = shot
            x += vx
            y += vy
            upd_shots.append((size_x,size_y,x,y,vx,vy))
        self.player_shots = upd_shots
        
        i=0
        while i<len(self.player_shots):
            shot = self.player_shots[i]
            if shot[2]<self.left or shot[2]>self.right or shot[3]<0 or shot[3]>SCREEN_HEIGHT:
                self.player_shots.remove(shot)
            else:
                i+=1
                
                enemy_hitboxes = [pygame.Rect((enemy[0]-enm_side//2, enemy[1]-enm_side//2), (enm_side,enm_side)) for enemy in self.enemies]
                shot_hitbox = pygame.Rect((shot[2]-shot[0]//2, shot[3]-shot[1]//2),(shot[0], shot[0]))

                a = shot_hitbox.collidelistall(enemy_hitboxes)
                if a:
                    self.player_shots.remove(shot)

                
                upd_enemies = []
                for j in range(len(self.enemies)):
                    x,y,x0,y0,w,hp = self.enemies[j]
                    if j in a:
                        if hp-1<=0:
                            self.delay_bombs.append((x,y,40,4,4))
                            self.score+=10
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

        return sent_bullets


            
    def draw(self, surf):
        for sp_bul in self.spawning_bullets:
            pygame.draw.circle(surf, (128,0,128), (int(sp_bul[0]), int(sp_bul[1])), 10)
        for bullet in self.bullets:
            pygame.draw.circle(surf, (255,0,255), (int(bullet[0]), int(bullet[1])), 5)
        for bomb in self.bombs:
            pygame.draw.circle(surf, (100,100,100), (int(bomb[0]), int(bomb[1])), bomb[2])
        for enemy in self.enemies:
            pygame.draw.circle(surf, (200,200,0), (int(enemy[0]), int(enemy[1])), 10)
        for shot in self.player_shots:
            pygame.draw.rect(surf, (255,255,255), pygame.Rect((shot[2]-6, shot[3]-6),(12,12)))


    def hit_player(self, player_hitbox):  ### player_hitbox is a square with coordinates of player, fixed side
        side = 4
        enm_side = 6
        bullet_hitboxes = [pygame.Rect(( bullet[0]-side//2, bullet[1]-side//2), (side,side)) for bullet in self.bullets]
        enemy_hitboxes = [pygame.Rect((enemy[0]-enm_side//2, enemy[1]-enm_side//2), (enm_side,enm_side)) for enemy in self.enemies]

        return bool((player_hitbox.collidelist(bullet_hitboxes)+1) + (player_hitbox.collidelist(enemy_hitboxes)+1))

    def pack_status(self):
        shot_package = code1(self.player_shots)
        
        bullet_package = code1(self.bullets)

        sp_bullet_package = code1(self.spawning_bullets)

        bomb_package = code1(self.bombs)
        
        enemy_package = code1(self.enemies)

        return 'NPC_STATUS'.join((shot_package, bullet_package, sp_bullet_package, bomb_package, enemy_package, str(self.score)))
        

class Player_serverside:
    def __init__(self, bullet_tracker):
        self.x = SCREEN_WIDTH // 4
        self.y = 7 * SCREEN_HEIGHT // 8
        
        self.L = SCREEN_WIDTH//2-50
        self.H = SCREEN_HEIGHT
        self.order_queue = deque([])
        
        self.firing = False
        self.cooldown = 0
        self.lives = 3
        self.speed = 5
        self.iframes = 0
        self.bomb_timeout = 0
        self.bombs = 5
        
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
            if self.iframes%2==0 and self.iframes>20:
                pygame.draw.rect(surf, (200,200,200), r)
            elif self.iframes%2==1 and self.iframes>20:
                pygame.draw.rect(surf, (20,0,0), r)
            else:
                pygame.draw.rect(surf, (75,75,75), r)
            

    def recv_orders(self, orders):
        '''
            extend my order queue with list - "orders".

            orders is a list of strings with instructions like UP, DOWN, LEFT, RIGHT, LOSE etc etc
        '''
        self.order_queue.extend(orders)

    def execute_order(self):
        H = self.H 
        L = self.L 
        '''
            get an order from queue and execute it

        '''

        self.firing = False
        order = self.order_queue.popleft()
        #print(order)
        ord_move, ord_shoot, ord_bomb, ord_focus, ord_spare_2 = order.split('+')

        if ord_focus=='FOCUS':
            self.speed = 2
        
        if ord_move=='UP' and self.y>5:
            self.y -= self.speed
        elif ord_move=='DOWN' and self.y<H-5:
            self.y += self.speed
        elif ord_move=='LEFT' and self.x>5:
            self.x -= self.speed
        elif ord_move=='RIGHT' and self.x<L-5:
            self.x += self.speed
        elif ord_move=='UP-LEFT' and self.y>5 and self.x>5:
            self.y -= self.speed/1.42
            self.x -= self.speed/1.42
        elif ord_move=='UP-RIGHT' and self.y>5 and self.x<L-5:
            self.y -= self.speed/1.42
            self.x += self.speed/1.42
        elif ord_move=='DOWN-LEFT'and self.y<H-5 and self.x>5:
            self.y += self.speed/1.42
            self.x -= self.speed/1.42
        elif ord_move=='DOWN-RIGHT' and self.y<H-5 and self.x<L-5:
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

        if self.iframes>0:
            self.iframes-=1
            
        self.speed = 5


    def pack_status(self):
        '''
            send your own status through connection
        '''
        
        coord_package = str(self.x) + ',' + str(self.y)

        stat_package = str(self.lives) + ',' + str(self.iframes) + ',' + str(self.bombs)

        return 'PLAYER_STATUS'.join((coord_package, stat_package))
##        connection.send(package.encode())


#### MAYBE SEPARATE THIS SHIT INTO CONFIG AND SETUP COMMANDS
###THEN PUT INTO SEPARATE FILE
##server_socket = sc.socket()
##server_socket.bind(('', 9101))
##server_socket.listen(1)
##client, client_address = server_socket.accept()
##
##
##FPS = 60
##pygame.init()
##pygame.display.set_caption('SERVER')
##fpsClock=pygame.time.Clock()
##
##SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
##screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
##surface = pygame.Surface(screen.get_size())
##
##surface_left = surface.subsurface(0,0,SCREEN_WIDTH//2-50, SCREEN_HEIGHT)
##surface_middle = surface.subsurface(SCREEN_WIDTH//2-50, 0, 100, SCREEN_HEIGHT)
##surface_right = surface.subsurface(SCREEN_WIDTH//2+50, 0, SCREEN_WIDTH//2-50, SCREEN_HEIGHT)
##
##surface_left.fill((128,0,0))
##surface_middle.fill((0,100,100))
##surface_right.fill((0,0,128))
##
##pygame.key.set_repeat(1, 10)
########

##NPC_TRACKER_1, NPC_TRACKER_2 = NPC_tracker_serverside(1), NPC_tracker_serverside(2)
##
##PLAYER_1 = Player_serverside(NPC_TRACKER_1, surface_left, shot_type='trapezoid')
##TOP_TRACKER = Top_tracker(NPC_TRACKER_1, NPC_TRACKER_2, PLAYER_1, surface, surface_left, surface_right, surface_middle, client)
##
##running=True
##while running:
##    for event in pygame.event.get():
##        if event.type == QUIT:
##            pygame.quit()
##            sys.exit()
##            server_socket.close()
##            running = False
##
##    if not TOP_TRACKER.loss:
##        TOP_TRACKER.display_all()
##        TOP_TRACKER.main_loop_progressive()
##        screen.blit(surface, (0,0))
##        pygame.display.flip()
##
##pygame.quit()
##sys.exit()
##server_socket.close()


with fuckit:
    a = Game_phase_tracker()
    a.prep_phase()
    a.game_phase()
    a.end_phase()

















 
