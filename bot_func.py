"""

bul_rad = 5
player_rad = 5*sqrt(2)

bullet velocity from 5 to almost 14
player velocity is about 5

player'd get shot if the bullet is closer than ~ 2*player_rad
so it takes player a little more than 2 time periods to evade the bullet

the fastest bullet will fly for 14 * 2* sqrt(2) in this time
so the safe distance to spot bullets is sqrt(196 * 8)
"""
dist1 = 196*8

"""
enemy_rad = 10
player_rad = 5*sqrt(2)

enemy velocity is less than 5
player velocity is about 5

player'd get annihilated if the enemy is closer than ~ player_rad*(1+sqrt(2))

that gives safe distance of 5(2+ sqrt(2)) (or 20)
"""
dist2 = 400

def choose_targets(targets, dist, x, y):
    chosen = []
    for i in targets:
        range = ((i[0]-x)**2 + (i[1]-y)**2)
        if range < dist:
            chosen.append([i,range])
    return chosen

"""
now let's decide which of the dangerous bullets to evade. as a test version,
the closest to the player will suffice
"""

def evade_speed(bullets, x, y):
    """
    to evade the destined fella the bot shoult move in perpendicular direction
    this function is to compute it in that case
    """
    k = 196 * 8
    bullet = []
    for i in bullets:
        if k > i[1]:
            k = i[1]
            bullet = i[0]
    if len(bullet) >0:
        return (-bullet[3]/(k**0.5), bullet[2]/(k**0.5))
    return (0, 0)

"""
now let's transform direction into a command
"""
c45 = 2**0.5 / 2

def command(direction, x, y):

    if x < 10:
        return 'RIGHT'
    elif x > 340:
        return'LEFT'
    elif y < 10:
        return 'DOWN'
    elif y > 5900:
        return 'UP'
    if (direction[0] <= c45) and (direction[0] >= -c45) and (direction[1] > 0):
        return 'UP'
    elif (direction[0] <= c45) and (direction[0] >= -c45) and (direction[1] < 0):
        return 'DOWN'
    elif (direction[1] <= c45) and (direction[1] >= -c45) and (direction[0] < 0):
         return'LEFT'
    elif (direction[1] <= c45) and (direction[1] >= -c45) and (direction[0] > 0):
         return 'RIGHT'

##    elif (direction[0] < -0.5) and (direction[1] <= -0.5):
##         return 'UP-LEFT'
##    elif (direction[0] > 0.5) and (direction[1] <= -0.5):
##        return 'UP-RIGHT'
##    elif (direction[0] < -0.5) and (direction[1] > 0.5):
##        return 'DOWN-LEFT'
##    elif (direction[0] > 0.5) and (direction[1] > -0.5):
##        return 'DOWN-RIGHT'
    return ''

"""
now combine all previous functions into 1 final form:
"""

def bot0(player, bullet_tracker):
    ord_move = ''
    x, y = player.x, player.y
    bullets = bullet_tracker.bullets
    enemies = bullet_tracker.enemies
    targets = choose_targets(bullets, dist1, x, y)
    dir = evade_speed(targets, x, y)
    ord_move = command(dir, x, y)
    ord_shoot='SHOOT'
    ord_bomb = ''
    doom =  len(choose_targets(bullets, 200 *c45, x, y)) + len(choose_targets(bullets,400, x, y))
    if doom > 0:
        ord_bomb = 'BOMB'
    ord_focus = ''
    ord_spare_2 = ''
    return ord_move, ord_shoot, ord_bomb, ord_focus, ord_spare_2
