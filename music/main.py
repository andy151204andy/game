import pygame
import random
import sys
import math

# 初始化 Pygame
pygame.init()
pygame.mixer.init()

# 屏幕设置
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("节奏大师 - 长粒子版")

# 颜色定义
TRACK_BG = (30, 30, 50)
TARGET_LINE_COLOR = (0, 150, 255)
TEXT_COLOR = (255, 255, 255)
TRACK_BORDER = (50, 100, 150)
PARTICLE_COLORS = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,165,0)]

# 游戏参数
TRACK_COUNT = 4
TRACK_WIDTH = 120
TRACK_HEIGHT = HEIGHT - 120
NOTE_SPEED = 5
JUDGE_RANGE = 40  # 增大判定范围到40像素
COMBO_MULTIPLIER = 0.5
PARTICLE_SIZE = 15
PARTICLE_LIFE = 150  # 延长到2.5秒（60帧/秒 × 2.5秒）
PARTICLE_COUNT = 20

# 轨道配置
TRACKS = [
    {"x": 100, "key": "a"},
    {"x": 300, "key": "s"},
    {"x": 500, "key": "d"},
    {"x": 700, "key": "f"}
]

class Note:
    def __init__(self, track_idx):
        self.track_idx = track_idx
        self.x = TRACKS[track_idx]["x"] + TRACK_WIDTH//2 - 20
        self.y = 0
        self.key = TRACKS[track_idx]["key"]
        self.active = True
        self.hit = False
        self.color = random.choice(PARTICLE_COLORS)
        self.particles = []

    def update(self):
        self.y += NOTE_SPEED
        if self.y > HEIGHT:
            self.active = False

    def draw(self):
        if self.active and not self.hit:
            pygame.draw.rect(screen, self.color, 
                (self.x, self.y, 40, 40), border_radius=8)
        else:
            for p in self.particles[:]:
                p.update()
                p.draw()
                if p.life <= 0:
                    self.particles.remove(p)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi*2)
        speed = random.uniform(2, 4)  # 降低速度以延长可见时间
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.size = random.randint(PARTICLE_SIZE//2, PARTICLE_SIZE*2)
        self.life = PARTICLE_LIFE
        self.color = random.choice(PARTICLE_COLORS)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # 减轻重力影响
        self.life -= 0.4  # 更慢的生命衰减

    def draw(self):
        if self.life <= 0:
            return
        alpha = int(self.life * 1.7)  # 透明度映射（0-255）
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        screen.blit(s, (self.x-self.size, self.y-self.size))

def init_game():
    clock = pygame.time.Clock()
    score = 0
    combo = 0
    notes = []
    
    try:
        pygame.mixer.music.load("music/365sunshine.mp3")
        pygame.mixer.music.play(-1)
    except:
        print("音乐文件未找到，继续运行但无声音")

    def draw_tracks():
        for i, track in enumerate(TRACKS):
            track_x = track["x"]
            pygame.draw.rect(screen, TRACK_BG, 
                (track_x, HEIGHT-120, TRACK_WIDTH, TRACK_HEIGHT))
            pygame.draw.rect(screen, TRACK_BORDER, 
                (track_x, HEIGHT-120, TRACK_WIDTH, TRACK_HEIGHT), 2)
            font = pygame.font.Font('music/game.ttc', 36)
            key_text = font.render(track["key"].upper(), True, TEXT_COLOR)
            screen.blit(key_text, (track_x + TRACK_WIDTH//2 - 10, HEIGHT-80))

    def draw_timeline():
        current_pos = pygame.mixer.music.get_pos() / 1000
        font = pygame.font.Font('music/game.ttc', 36)
        time_text = font.render(f"时间: {current_pos:.1f}s", True, TEXT_COLOR)
        screen.blit(time_text, (WIDTH//2 - 70, 20))

    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_tracks()
        draw_timeline()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                for note in notes:
                    if note.active and not note.hit:
                        distance = abs(note.y - (HEIGHT-100))
                        if distance < JUDGE_RANGE:
                            if pygame.key.name(event.key) == note.key:
                                note.particles = [Particle(note.x+20, note.y+20) for _ in range(PARTICLE_COUNT)]
                                score += 100 + int(combo * COMBO_MULTIPLIER)
                                combo += 1
                            else:
                                combo = 0

        if random.random() < 0.05:
            track_idx = random.randint(0, TRACK_COUNT-1)
            notes.append(Note(track_idx))

        for note in notes[:]:
            note.update()
            note.draw()
            if not note.active:
                notes.remove(note)

        combo_text = pygame.font.Font('music/game.ttc', 64).render(f"COMBO x{combo}", True, 
            (255, 165, 0) if combo > 5 else TEXT_COLOR)
        text_rect = combo_text.get_rect(center=(WIDTH//2, HEIGHT-80))
        screen.blit(combo_text, text_rect)

        pygame.draw.line(screen, TARGET_LINE_COLOR, 
            (0, HEIGHT-100), (WIDTH, HEIGHT-100), 3)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    init_game()