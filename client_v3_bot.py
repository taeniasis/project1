import pygame
import time
import sys
import socket as sc

from collections import deque
from codndecode import decode1
import bot_func as bot
from pygame.locals import *


########## PUT THIS BULLSHIT IN A SEPARATE FILE AND IMPORT AND EXECUTE IT

FPS = 60

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600


def draw_box(surf, color, pos):
    r = pygame.Rect((pos[0], pos[1]), (10,10))
    pygame.draw.rect(surf, color, r)


    

####################

class Game_phase_tracker_clientside:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('CLIENT')
        self.fpsClock=pygame.time.Clock()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surface = pygame.Surface(self.screen.get_size())
    
        self.surface_left = self.surface.subsurface(0,0,SCREEN_WIDTH//2-50, SCREEN_HEIGHT)
        self.surface_middle = self.surface.subsurface(SCREEN_WIDTH//2-50, 0, 100, SCREEN_HEIGHT)
        self.surface_right = self.surface.subsurface(SCREEN_WIDTH//2+50, 0, SCREEN_WIDTH//2-50, SCREEN_HEIGHT)
    
        self.text = pygame.font.SysFont('Calibri', 20)
        self.title_text = pygame.font.SysFont('Calibri', 40)
        pygame.key.set_repeat(1, 10)

        self.loss = 0
        self.phase = 'PREP'
        

    def prep_phase(self):
##        title_text = pygame.font.SysFont('Calibri', 40)
        first_text = self.title_text.render('Connecting to server. Please follow console instructions', False, (255,255,255))
        
        self.surface.fill((0,128,128))
        self.surface.blit(first_text, (0, SCREEN_HEIGHT//2))
        self.screen.blit(self.surface, (0,0))
        pygame.display.flip()
        
        self.server_address = input('Enter server address: ')
        self.player_id = input('Which player are you? [1/2]: ')
        
        self.client_socket = sc.socket()
        if self.player_id=='1':
            try:
                self.client_socket.connect((self.server_address, 9101))
            except:
                print('Connection busy, pal. Try a different id')
                
        elif self.player_id=='2':
            try:
                self.client_socket.connect((self.server_address, 9102))
            except:
                print('Connection busy, pal. Try a different id')
        else:
            print('A comedian, huh? Fuck off, I have no time for your inane faggotry')


        self.phase = 'GAME'
    def game_phase(self):
        clock=0
        player_1 = Player_clientside()
        player_2 = Player_clientside()
        NPC_tracker_1 = NPC_tracker_clientside()
        NPC_tracker_2 = NPC_tracker_clientside()
        orders = deque([])

        while not self.loss:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    client_socket.close()
                    

            ord_move = ''
            ord_shoot = ''
            ord_bomb = ''
            ord_focus = ''
            ord_spare_2 = ''

            if self.player_id=='1':
                ord_move, ord_shoot, ord_bomb, ord_focus, ord_spare_2 = bot.bot0(player_1, NPC_tracker_1)
            elif self.player_id=='2':
                ord_move, ord_shoot, ord_bomb, ord_focus, ord_spare_2 = bot.bot0(player_2, NPC_tracker_2)
            ord_shoot='SHOOT'
            orders.append('{}+{}+{}+{}+{}'.format(ord_move, ord_shoot, ord_bomb, ord_focus, ord_spare_2))
            

            try:
                order = orders.popleft()
            except:
                order = '++++'  
            self.client_socket.send(order.encode())



            self.surface_left.fill((255, 179, 179))
            self.surface_middle.fill((0,0,0))
            self.surface_right.fill((179, 179, 255))

            player_1_status = self.text.render('LIVES:{}   BOMBS:{}   SCORE:{}'.format(int(player_1.lives), int(player_1.bombs), int(NPC_tracker_1.score)), False, (255,255,255))
            player_2_status = self.text.render('LIVES:{}   BOMBS:{}   SCORE:{}'.format(int(player_2.lives), int(player_2.bombs), int(NPC_tracker_2.score)), False, (255,255,255))
            game_status = self.text.render('LEVEL:{:.3f}'.format(float(clock)/3600), False, (255,255,255))
            if self.player_id=='1':
                player_id = self.text.render('<<<<<YOU', False, (255,255,255))
            else:
                player_id = self.text.render('YOU>>>>>', False, (255,255,255))
            
            self.surface_left.blit(player_1_status, (10, 10))
            self.surface_right.blit(player_2_status, (10, 10))
            self.surface_middle.blit(game_status, (0,0))
            self.surface_middle.blit(player_id, (0, SCREEN_HEIGHT-20))

            NPC_tracker_1.draw(self.surface_left)
            NPC_tracker_2.draw(self.surface_right)
            player_1.draw(self.surface_left)
            player_2.draw(self.surface_right)
            
            self.screen.blit(self.surface, (0,0))
            pygame.display.flip()
            self.fpsClock.tick(FPS)


            package = self.client_socket.recv(8192).decode('utf8')
            npc_1,playa_1,npc_2,playa_2,clock, loss = package.split('$')
            self.loss = int(loss)
            
            coord, stat = playa_1.split('PLAYER_STATUS')
            player_1.recv_status(coord, stat)

            coord, stat = playa_2.split('PLAYER_STATUS')
            player_2.recv_status(coord, stat)

            shots,bullet,sp_bullet,bomb,enemy,score = npc_1.split('NPC_STATUS')
            NPC_tracker_1.recv_status(shots,bullet,sp_bullet,bomb,enemy,score)
            
            shots,bullet,sp_bullet,bomb,enemy,score = npc_2.split('NPC_STATUS')
            NPC_tracker_2.recv_status(shots,bullet,sp_bullet,bomb,enemy,score)



    def end_phase(self):
        title_text = pygame.font.SysFont('Calibri', 40)        

##        print('\n', self.loss)
        if self.loss==1:
            last_text = title_text.render('Player 2 won', False, (255,255,255))
        elif self.loss==2:
            last_text = title_text.render('Player 1 won', False, (255,255,255))
        elif self.loss==3:
            last_text = title_text.render('DRAW', False, (255,255,255))
        else:
            last_text = title_text.render('SOMETHING WENT WRONG', False, (255,255,255))

        for i in range(300):
            if self.loss==1:
                self.surface.fill((179, 179, 255))
            elif self.loss==2:
                self.surface.fill((255, 179, 179))
            elif self.loss==3:
                self.surface.fill((200,0,200))
            else:
                self.surface.fill((0,0,0))
                
            self.surface.blit(last_text, (SCREEN_WIDTH//2-100, SCREEN_HEIGHT//2))
            self.screen.blit(self.surface, (0,0))

            pygame.display.flip()

        
        self.client_socket.close()
        pygame.quit()
        sys.exit()

            
            

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

    def recv_status(self, shots, bullets, sp_bullets, bombs, enemies, score):
        self.player_shots = deque(decode1(shots))
        
        self.bullets = deque(decode1(bullets))
        self.spawning_bullets = deque(decode1(sp_bullets))

        self.bombs = deque(decode1(bombs))

        self.enemies = deque(decode1(enemies))

        self.score = float(score)



class Player_clientside:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.lives = 10
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



a = Game_phase_tracker_clientside()
a.prep_phase()
a.game_phase()
a.end_phase()


##
