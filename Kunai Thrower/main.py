import pygame, os, sys, random
from pygame.constants import KEYDOWN, K_ESCAPE, K_SPACE, K_r 

pygame.init()

# icon 
icon = pygame.image.load(os.path.join('assets/sprites/icons/','Kunai.png'))

GRAVITY = .5
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Kunai Throwing Simulator')
pygame.display.set_icon(icon)

pygame.time.set_timer(pygame.USEREVENT+1, 2000)
clock = pygame.time.Clock()

# background images
sky_image = pygame.image.load(os.path.join('assets/sprites/background/','sky_cloud.png'))
mountain_image = pygame.image.load(os.path.join('assets/sprites/background/','mountain.png'))
pine_one_image = pygame.image.load(os.path.join('assets/sprites/background/','pine1.png'))
pine_two_image = pygame.image.load(os.path.join('assets/sprites/background/','pine2.png'))



level_map = [
'                            ',
'                            ',
'                            ',
'                            ',
'                            ',
'                            ',
'                            ',
'                            ',
'XXXXXXXXXXXXXXXXXXXXXXXXXXXX',
'XXXXXXXXXXXXXXXXXXXXXXXXXXXX',
'XXXXXXXXXXXXXXXXXXXXXXXXXXXX']


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load(os.path.join('assets/sprites/tile/', 'terrain_tiles.png'))
        self.rect = self.image.get_rect(topleft = pos)


class Kunai(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__() 
        self.direction = direction     
        img = pygame.image.load(os.path.join('assets/sprites/icons/', 'Kunai.png'))
        self.image = pygame.transform.scale(pygame.transform.rotate(img, 270), (int(img.get_width()*2), int(img.get_height() * .15)))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.flip = False
        if self.direction == -1:
            self.flip = True

    def update(self):
        self.rect.x += (self.direction * 4)

    def draw(self, surface):
        surface.blit(pygame.transform.flip(self.image, self.flip, False), self.rect) 

class Balloon(pygame.sprite.Sprite):
    def __init__(self, x ,y):
        super().__init__()
        img = pygame.image.load(os.path.join('assets/sprites/icons/', 'balloon.png'))
        self.image = pygame.transform.scale(img, (int(img.get_width()*.1), int(img.get_height() * .1)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
    def draw(self):
        screen.blit(self.image, self.rect)
        




class Ninja(pygame.sprite.Sprite):
    
    def __init__(self, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.speed = speed
        self.jump_counter = 0  
        self.direction = 1
        self.vel_y = 0
        self.in_air = True
        self.flip = False
        self.jump = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        animation_types = ['Idle', 'Run', 'Jump','Throw']
        for animation in animation_types:
            temp_list = []
            for i in range(10):
                img = pygame.image.load(os.path.join('assets/sprites/ninja/', f'{animation}__00{i}.png'))
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        

        
    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0
        
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        if self.jump == True and self.jump_counter < 3:            
            self.vel_y = -12
            self.jump_counter += 1
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        if self.rect.bottom + dy > 515:
            dy = 515 - self.rect.bottom
            self.in_air = False
            self.jump_counter = 0

        if self.rect.right + dx > WIDTH:
            dx = WIDTH - self.rect.right
        elif self.rect.left + dx < 0:
            dx = self.rect.left

        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        kunai_array.append(Kunai(player.rect.centerx + 40 * player.direction, player.rect.y+40, player.direction))

    def update_animation(self):
        ANIMATION_COOLDOWN = 100

        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0 
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        surface.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

player = Ninja(450,500,.2, 5)
kunai = Kunai(player.rect.centerx + 50 * player.direction, player.rect.y-40, player.direction)

screen_size = screen.get_size()
sky_size = sky_image.get_size()
mountain_size = mountain_image.get_size()
bg_pine1_size = pine_one_image.get_size()
bg_pine2_size = pine_two_image.get_size()

bg_sky = (sky_size[0] - screen_size[0]) // 2
bg_mountain = (mountain_size[0] - screen_size[0]) // 2
bg_pine1 = (bg_pine1_size[0] - screen_size[0]) // 2
bg_pine2 = (bg_pine2_size[0] - screen_size[0]) // 2



moving_left = False
moving_right = False
throwing = False
kunai_array = []
balloon_array = []

class Level:
    def __init__(self, level_data, surface):
        self.display_surface = surface
        self.setup_level(level_data)
        self.world_shift = 0

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * 64
                y = row_index * 64
                
                if cell == 'X': 
                    tile = Tile((x, y))
                    self.tiles.add(tile)
    
    def run(self):
        self.tiles.draw(self.display_surface)

level = Level(level_map, screen)


while True:
    screen.fill((0,0,0))
    screen.blit(sky_image,(bg_sky-350,-70))
    screen.blit(mountain_image,(bg_mountain-300,170))
    screen.blit(pine_one_image,(bg_pine1-300,250))
    screen.blit(pine_two_image,(bg_pine2-300,270))
    player.update_animation()
    player.draw(screen)
    level.run()
    
    
    for kunai in kunai_array:
        kunai.draw(screen)
        kunai.update()
    
    for balloon in balloon_array:
        balloon.draw()
        if pygame.sprite.collide_rect(kunai, balloon):
            balloon_array.remove(balloon)
            kunai_array.remove(kunai)

    if moving_right:
        player.update_action(1)
        bg_sky -= 1
        bg_pine1 += 1
        bg_pine2 -= 1
        bg_mountain -= 1
    elif moving_left:
        player.update_action(1)
        bg_sky += 1
        bg_pine1 -= 1
        bg_pine2 += 1
        bg_mountain += 1
    elif player.in_air:
        player.update_action(2)  
        
    else:
        player.update_action(0)

    if throwing:
         player.update_action(3)

    player.move(moving_left, moving_right)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a and player.rect.x > 0:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True  
            if event.key == pygame.K_SPACE: 
                player.jump = True 
            if event.key == pygame.K_r:
                player.shoot()
                throwing = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_r:
                throwing = False
    
        if event.type == pygame.USEREVENT+1:
            balloon = Balloon((random.randrange(0,WIDTH-30)),(random.randrange(0,HEIGHT-100)))
            balloon_array.append(balloon)
    
    

    
    pygame.display.flip()
    clock.tick(60)
