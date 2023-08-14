import pygame
import random
import os

FPS = 60
WIDTH = 500
HEIGHT = 600

WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)
BLACK = (0,0,0)

pygame.init() # 初始化
pygame.mixer.init() # 初始化
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My first game")
clock = pygame.time.Clock()

# load image
background_img = pygame.image.load(os.path.join("img", "background.png")).convert() # 用os.path.join比較不會有路徑問題，convert()轉換格式
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
mini_player_img = pygame.transform.scale(player_img,(25, 19))
mini_player_img.set_colorkey(BLACK)
pygame.display.set_icon(mini_player_img)
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert()) # 字串前加入f可以在字串中使用變數
explosion_animation = {} # 使用dic存放
explosion_animation["large"] = [] # list
explosion_animation["small"] = []
explosion_animation["player"] = []
for i in range(9):
    explosion_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    explosion_img.set_colorkey(BLACK)
    explosion_animation["large"].append(pygame.transform.scale(explosion_img,(75,75))) # pygame.transform.scale(explosion_img,(75,75)) 將圖片縮放
    explosion_animation["small"].append(pygame.transform.scale(explosion_img,(30,30)))
    player_explosion_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    player_explosion_img.set_colorkey(BLACK)
    explosion_animation["player"].append(player_explosion_img)

power_imgs = {}
power_imgs["shield"] = pygame.image.load(os.path.join("img", "shield.png")).convert()
power_imgs["gun"] = pygame.image.load(os.path.join("img", "gun.png")).convert()

# load music
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
explore_sound = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.5)

font_name = os.path.join("font.ttf")
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp / 100)*BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT) # 外框
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT) # 填滿
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2) # 最後一個參數2是兩像素

def new_rock():
    rock = Rock()
    all_sprites.add(rock)
    rocks.add(rock)

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30*i
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_menu():
    screen.blit(background_img, (0, 0))
    draw_text(screen, "太空生存戰", 64, WIDTH/2, HEIGHT/4)
    draw_text(screen, "← →移動飛船 空白鍵射子彈", 22, WIDTH/2, HEIGHT/2)
    draw_text(screen, "按任意鍵開始遊戲", 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50,38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 21
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius) # 劃出碰撞區
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and pygame.time.get_ticks() - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT - 10        

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_d]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_a]:
            self.rect.x -= self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.top)
                bullet2 = Bullet(self.rect.right, self.rect.top)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self): # 死掉時消失
        self.hidden = True
        self.hide_time = pygame.time.get_ticks() # 取得以隱藏時間
        self.rect.center = (WIDTH/2, HEIGHT+500) # 消失效果將player移出場景

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_original = random.choice(rock_imgs)
        self.image_original.set_colorkey(BLACK)
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width *0.87 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius) # 劃出碰撞區
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(2, 6)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rotate_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rotate_degree
        self.total_degree = self.total_degree % 360 # 轉動不超過360度
        self.image = pygame.transform.rotate(self.image_original, self.total_degree)
        center = self.rect.center # 舊的中心點
        self.rect = self.image.get_rect() # 轉動後重新取得rect
        self.rect.center = center # 將舊的中心點傳給新的中心點

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 6)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_animation[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks() # pygame.time.get_ticks()取得現在時間
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_animation[self.size]):
                self.kill()
            else:
                self.image = explosion_animation[self.size][self.frame]
                center = self.rect.center # 重新定位
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield", "gun"])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

player = Player()
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
rocks = pygame.sprite.Group()
powers = pygame.sprite.Group()
all_sprites.add(player)
for i in range(8):
    new_rock()

score = 0
pygame.mixer.music.play(-1)

# game loop
show_init = True    
running = True
while running:
    if show_init:
        close = draw_menu()
        if close:
            break
        show_init = False
        player = Player()
        all_sprites = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        powers = pygame.sprite.Group()
        all_sprites.add(player)
        for i in range(8):
            new_rock()
        score = 0
    clock.tick(FPS)

    # input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
    # update
    all_sprites.update()
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits:
        random.choice(explore_sound).play()
        score += hit.radius
        explosion = Explosion(hit.rect.center, "large")
        all_sprites.add(explosion)
        if random.random() > 0.9:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()

    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle) # collide_circle需要給self.radius屬性
    for hit in hits:
        new_rock()
        player.health -= hit.radius
        explosion = Explosion(hit.rect.center, "small")
        all_sprites.add(explosion)
        if player.health <= 0:
            die = Explosion(player.rect.center, "player")
            all_sprites.add(die)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()

    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == "shield":
            player.health += 20
            if player.health > 100:
                player.health = 100
            shield_sound.play()    
        elif hit.type == "gun":
            player.gunup()
            gun_sound.play()

    if player.lives == 0 and not(die.alive()): # alive() 判斷是否播完
        show_init = True

    # display
    screen.fill(BLACK)
    screen.blit(background_img, (0, 0)) # blit是畫, (0, 0)座標
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH/2, 10)
    draw_health(screen, player.health, 5, 18)
    draw_lives(screen, player.lives, mini_player_img, WIDTH - 100,15)
    pygame.display.update()

pygame.quit()