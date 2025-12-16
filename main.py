import pygame
import random
import sys
import os

# Inisialisasi Pygame
pygame.init()
pygame.mixer.init()

# Konstanta game
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Membuat player dengan gambar atau bentuk default
        self.image = pygame.Surface((50, 40))
        self.image.fill(GREEN)
        pygame.draw.polygon(self.image, BLUE, [(25, 0), (0, 40), (50, 40)])
        
        # Jika ada file player.png, gunakan itu
        if os.path.exists("assets/player.png"):
            try:
                loaded_image = pygame.image.load("assets/player.png").convert_alpha()
                self.image = pygame.transform.scale(loaded_image, (50, 40))
            except:
                pass
        
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 8
        self.health = 100
        self.shoot_delay = 250  # ms
        self.last_shot = pygame.time.get_ticks()
        
    def update(self):
        # Kontrol player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed
            
        # Batasi player di dalam layar
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
    
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            return bullet
        return None
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        return self.health <= 0

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Membuat enemy dengan gambar atau bentuk default
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        pygame.draw.circle(self.image, YELLOW, (20, 20), 15)
        
        # Jika ada file enemy.png, gunakan itu
        if os.path.exists("assets/enemy.png"):
            try:
                loaded_image = pygame.image.load("assets/enemy.png").convert_alpha()
                self.image = pygame.transform.scale(loaded_image, (40, 40))
            except:
                pass
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speed_y = random.randint(1, 4)
        self.speed_x = random.randint(-2, 2)
        self.health = 30
        
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        # Jika enemy keluar layar, reset posisi
        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > SCREEN_WIDTH + 25:
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speed_y = random.randint(1, 4)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Membuat bullet dengan gambar atau bentuk default
        self.image = pygame.Surface((5, 15))
        self.image.fill(YELLOW)
        
        # Jika ada file bullet.png, gunakan itu
        if os.path.exists("assets/bullet.png"):
            try:
                loaded_image = pygame.image.load("assets/bullet.png").convert_alpha()
                self.image = pygame.transform.scale(loaded_image, (8, 20))
            except:
                pass
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = -10
    
    def update(self):
        self.rect.y += self.speed_y
        # Hapus bullet jika keluar layar
        if self.rect.bottom < 0:
            self.kill()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Game Tembak-Tembakan")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.score = 0
        self.level = 1
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 1000  # ms
        
        # Grup sprite
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        
        # Buat player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Buat beberapa enemy awal
        for _ in range(8):
            enemy = Enemy()
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
        
        # Load background jika ada
        self.background = None
        if os.path.exists("assets/background.png"):
            try:
                self.background = pygame.image.load("assets/background.png").convert()
                self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except:
                self.background = None
        
        # Font
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Sound effects (jika tersedia)
        self.shoot_sound = None
        self.explosion_sound = None
        
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            
            if not self.game_over:
                self.update()
            
            self.draw()
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    bullet = self.player.shoot()
                    if bullet:
                        self.all_sprites.add(bullet)
                        self.bullets.add(bullet)
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        # Update semua sprite
        self.all_sprites.update()
        
        # Spawn enemy
        now = pygame.time.get_ticks()
        if now - self.enemy_spawn_timer > self.enemy_spawn_delay:
            self.enemy_spawn_timer = now
            enemy = Enemy()
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)
        
        # Cek tabrakan bullet dengan enemy
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets in hits.items():
            enemy.health -= 10 * len(bullets)
            if enemy.health <= 0:
                enemy.kill()
                self.score += 10
                # Spawn enemy baru
                new_enemy = Enemy()
                self.all_sprites.add(new_enemy)
                self.enemies.add(new_enemy)
        
        # Cek tabrakan player dengan enemy
        hits = pygame.sprite.spritecollide(self.player, self.enemies, True)
        for hit in hits:
            if self.player.take_damage(20):
                self.game_over = True
            # Spawn enemy baru
            new_enemy = Enemy()
            self.all_sprites.add(new_enemy)
            self.enemies.add(new_enemy)
        
        # Update level berdasarkan skor
        self.level = self.score // 100 + 1
        self.enemy_spawn_delay = max(200, 1000 - (self.level * 100))  # Enemy spawn lebih cepat di level tinggi
    
    def draw(self):
        # Gambar background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BLACK)
            # Tambahkan bintang-bintang di background
            for _ in range(50):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                pygame.draw.circle(self.screen, WHITE, (x, y), 1)
        
        # Gambar semua sprite
        self.all_sprites.draw(self.screen)
        
        # Gambar UI
        # Health bar
        pygame.draw.rect(self.screen, RED, (10, 10, 200, 20))
        pygame.draw.rect(self.screen, GREEN, (10, 10, self.player.health * 2, 20))
        pygame.draw.rect(self.screen, WHITE, (10, 10, 200, 20), 2)
        
        # Skor dan level
        score_text = self.font.render(f"Skor: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 10))
        self.screen.blit(level_text, (SCREEN_WIDTH - 150, 50))
        
        # Kontrol
        controls = [
            "Kontrol:",
            "A/W/S/D atau Panah: Gerak",
            "Spasi: Tembak",
            "R: Restart",
            "ESC: Keluar"
        ]
        
        for i, text in enumerate(controls):
            control_text = self.small_font.render(text, True, WHITE)
            self.screen.blit(control_text, (10, SCREEN_HEIGHT - 120 + i * 25))
        
        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, RED)
            final_score = self.font.render(f"Skor Akhir: {self.score}", True, WHITE)
            restart_text = self.font.render("Tekan R untuk restart", True, GREEN)
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
        
        pygame.display.flip()
    
    def reset_game(self):
        self.game_over = False
        self.score = 0
        self.level = 1
        
        # Hapus semua sprite kecuali player
        for sprite in self.all_sprites:
            if sprite != self.player:
                sprite.kill()
        
        # Reset player
        self.player.rect.centerx = SCREEN_WIDTH // 2
        self.player.rect.bottom = SCREEN_HEIGHT - 10
        self.player.health = 100
        
        # Buat enemy baru
        for _ in range(8):
            enemy = Enemy()
            self.all_sprites.add(enemy)
            self.enemies.add(enemy)

if __name__ == "__main__":
    game = Game()
    game.run()
