import pygame
import math
import random

# --- AYARLAR ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Renkler
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREEN = (50, 200, 50)     # Oyuncu
RED = (200, 50, 50)       # Düşman
YELLOW = (255, 255, 0)    # Mermi
BLUE = (50, 100, 255)     # XP (Materyal)
GRAY = (100, 100, 100)    # Menü Arka Planı

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brotato Klonu v2 - Level Sistemi")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)
large_font = pygame.font.SysFont("Arial", 40)

# --- SINIFLAR ---

class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.radius = 20
        self.hp = 100
        self.max_hp = 100
        self.color = GREEN
        
        # İstatistikler (Upgrade edilebilir)
        self.move_speed = 4
        self.damage = 15
        self.attack_speed = 30  # Düşük = Hızlı
        self.bullet_speed = 10
        
        self.attack_cooldown = 0 
        self.xp = 0
        self.level = 1 
        self.xp_to_next_level = 5

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.x > 0: self.x -= self.move_speed
        if keys[pygame.K_d] and self.x < WIDTH: self.x += self.move_speed
        if keys[pygame.K_w] and self.y > 0: self.y -= self.move_speed
        if keys[pygame.K_s] and self.y < HEIGHT: self.y += self.move_speed

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Can çubuğu
        pygame.draw.rect(screen, RED, (self.x - 20, self.y - 30, 40, 5))
        if self.hp > 0:
            pygame.draw.rect(screen, GREEN, (self.x - 20, self.y - 30, 40 * (self.hp/self.max_hp), 5))

class Enemy:
    def __init__(self, wave_difficulty):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top': self.x, self.y = random.randint(0, WIDTH), -30
        elif side == 'bottom': self.x, self.y = random.randint(0, WIDTH), HEIGHT + 30
        elif side == 'left': self.x, self.y = -30, random.randint(0, HEIGHT)
        else: self.x, self.y = WIDTH + 30, random.randint(0, HEIGHT)
        
        self.radius = 15
        # Dalga zorlaştıkça düşman canı artar
        self.hp = 20 + (wave_difficulty * 2)
        self.speed = 2 + (wave_difficulty * 0.1)

    def move_towards_player(self, player):
        angle = math.atan2(player.y - self.y, player.x - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)

class Bullet:
    def __init__(self, x, y, target_x, target_y, damage, speed):
        self.x, self.y = x, y
        self.damage = damage
        angle = math.atan2(target_y - y, target_x - y) # target_x - x olmalıydı, aşağıda düzelttim
        angle = math.atan2(target_y - y, target_x - x)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.radius = 5

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)

class XPDrop:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 6 
        self.value = 2

    def draw(self):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)

# --- YARDIMCI FONKSİYONLAR ---
def draw_text_centered(text, font, color, y_offset=0):
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect(center=(WIDTH//2, HEIGHT//2 + y_offset))
    screen.blit(text_obj, rect)

def get_closest_enemy(player, enemies):
    closest_dist = float('inf')
    closest_enemy = None
    for enemy in enemies:
        dist = math.hypot(enemy.x - player.x, enemy.y - player.y)
        if dist < closest_dist:
            closest_dist = dist
            closest_enemy = enemy
    return closest_enemy

# --- OYUN DEĞİŞKENLERİ ---
player = Player()
enemies = []
bullets = []
xp_drops = []
wave = 1
spawn_timer = 0
game_state = "PLAYING" # PLAYING, LEVEL_UP, GAME_OVER

# --- OYUN DÖNGÜSÜ ---
running = True
while running:
    clock.tick(FPS)
    
    # Olay Kontrolü
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Oyunu Sıfırla
                player.reset()
                enemies = []
                bullets = []
                xp_drops = []
                wave = 1
                game_state = "PLAYING"

        if game_state == "LEVEL_UP":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: # Hasar Artır
                    player.damage += 5
                    player.level += 1
                    player.xp = 0
                    player.xp_to_next_level = int(player.xp_to_next_level * 1.5)
                    game_state = "PLAYING"
                elif event.key == pygame.K_2: # Atış Hızı Artır
                    player.attack_speed = max(5, player.attack_speed - 2)
                    player.level += 1
                    player.xp = 0
                    player.xp_to_next_level = int(player.xp_to_next_level * 1.5)
                    game_state = "PLAYING"
                elif event.key == pygame.K_3: # Hareket Hızı Artır
                    player.move_speed += 0.5
                    player.level += 1
                    player.xp = 0
                    player.xp_to_next_level = int(player.xp_to_next_level * 1.5)
                    game_state = "PLAYING"

    # --- DURUM: OYNANIYOR ---
    if game_state == "PLAYING":
        screen.fill(BLACK)
        
        # 1. Player
        player.move()
        player.draw()

        # 2. Düşman Doğurma
        spawn_rate = max(10, 60 - (wave * 2)) # Wave arttıkça daha sık düşman gelir
        spawn_timer += 1
        if spawn_timer >= spawn_rate:
            enemies.append(Enemy(wave))
            spawn_timer = 0

        # 3. Otomatik Ateş
        if player.attack_cooldown > 0:
            player.attack_cooldown -= 1
        else:
            target = get_closest_enemy(player, enemies)
            if target:
                bullets.append(Bullet(player.x, player.y, target.x, target.y, player.damage, player.bullet_speed))
                player.attack_cooldown = player.attack_speed

        # 4. Mermiler
        for bullet in bullets[:]:
            bullet.move()
            bullet.draw()
            if not (0 < bullet.x < WIDTH and 0 < bullet.y < HEIGHT):
                if bullet in bullets: bullets.remove(bullet)
                continue
            
            # Mermi düşmana çarptı mı?
            for enemy in enemies[:]:
                dist = math.hypot(bullet.x - enemy.x, bullet.y - enemy.y)
                if dist < (bullet.radius + enemy.radius):
                    enemy.hp -= bullet.damage
                    if bullet in bullets: bullets.remove(bullet)
                    if enemy.hp <= 0:
                        if enemy in enemies: enemies.remove(enemy)
                        # XP Düşür
                        xp_drops.append(XPDrop(enemy.x, enemy.y))
                    break
        
        # 5. Düşmanlar
        for enemy in enemies[:]:
            enemy.move_towards_player(player)
            enemy.draw()
            # Oyuncuya çarpma
            dist = math.hypot(enemy.x - player.x, enemy.y - player.y)
            if dist < (enemy.radius + player.radius):
                player.hp -= 1
                if player.hp <= 0:
                    game_state = "GAME_OVER"

        # 6. XP Toplama
        for xp in xp_drops[:]:
            xp.draw()
            dist = math.hypot(xp.x - player.x, xp.y - player.y)
            # Mıknatıs etkisi (Yaklaşınca çeksin)
            if dist < 100:
                angle = math.atan2(player.y - xp.y, player.x - xp.x)
                xp.x += math.cos(angle) * 6
                xp.y += math.sin(angle) * 6
            
            if dist < player.radius:
                player.xp += xp.value
                xp_drops.remove(xp)
                # Level Up Kontrolü
                if player.xp >= player.xp_to_next_level:
                    game_state = "LEVEL_UP"
                    wave += 1 # Her levelde wave zorlaşsın

        # UI (Arayüz)
        xp_text = font.render(f"Level: {player.level} | XP: {player.xp}/{player.xp_to_next_level}", True, WHITE)
        screen.blit(xp_text, (10, 10))
        stats_text = font.render(f"Dmg: {player.damage} | Spd: {player.attack_speed}", True, WHITE)
        screen.blit(stats_text, (10, 35))

    # --- DURUM: LEVEL UP ---
    elif game_state == "LEVEL_UP":
        # Yarı saydam arka plan
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        
        draw_text_centered("LEVEL ATLADIN!", large_font, YELLOW, -100)
        draw_text_centered("Bir Özellik Seç:", font, WHITE, -50)
        draw_text_centered("[1] Hasar Artır (+5)", font, GREEN, 0)
        draw_text_centered("[2] Saldırı Hızı Artır", font, GREEN, 40)
        draw_text_centered("[3] Hareket Hızı Artır", font, GREEN, 80)

    # --- DURUM: OYUN BİTTİ ---
    elif game_state == "GAME_OVER":
        draw_text_centered("OYUN BİTTİ", large_font, RED, -50)
        draw_text_centered(f"Ulaşılan Level: {player.level}", font, WHITE, 0)
        draw_text_centered("Tekrar oynamak için 'R' tuşuna bas", font, GRAY, 50)

    pygame.display.flip()

pygame.quit()