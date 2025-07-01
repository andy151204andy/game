import pygame
import random
import math
from pygame import Color

# 初始化
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
BOOM = pygame.mixer.Sound("boom.ogg")
pygame.display.set_caption("紫蓝星空烟花秀")

# 颜色配置
COLORS = [
    (255, 100, 100),  # 粉红
    (100, 255, 150),  # 薄荷
    (150, 200, 255),  # 天蓝
    (255, 200, 100),  # 香槟金
    (200, 150, 255)   # 薰衣草
]

# 修改为紫色到蓝色渐变
NIGHT_SKY_COLORS = [
    (70, 0, 100),     # 深紫色（顶部）
    (0, 50, 150)      # 深蓝色（底部）
]

class Particle:
    """粒子类（保持原有逻辑）"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.base_color = color
        self.size = random.uniform(2, 4)
        self.life = 1.0
        angle = math.radians(random.uniform(0, 360))
        speed = random.uniform(1, 5)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.fade_speed = random.uniform(0.01, 0.03)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.fade_speed
        self.vx *= 0.98
        self.vy *= 0.98

    def get_color(self):
        return Color(self.base_color).lerp(
            (255, 255, 255), 1 - self.life
        )

    def draw(self, surface):
        if self.life > 0:
            alpha = int(self.life * 255)
            color = self.get_color().lerp(
                (0, 0, 0, 0), 1 - self.life
            )
            pygame.draw.circle(
                surface, color,
                (int(self.x), int(self.y)),
                int(self.size * self.life)
            )

class Firework:
    """烟花类"""
    def __init__(self):
        self.x = random.randint(WIDTH//4, 3*WIDTH//4)
        self.y = HEIGHT
        self.speed = random.uniform(1.5, 2.5)
        self.target_y = random.randint(200, 350)
        self.color = random.choice(COLORS)
        self.particles = []
        self.exploded = False

    def explode(self):
        for _ in range(50):
            self.particles.append(Particle(self.x, self.y, self.color))

    def update(self):
        if not self.exploded:
            self.y -= self.speed
            if self.y <= self.target_y:
                self.explode()
                self.exploded = True
        else:
            for p in self.particles[:]:
                p.update()
                if p.life <= 0:
                    self.particles.remove(p)

    def draw(self, surface):
        if not self.exploded:
            trail_length = 10
            for i in range(trail_length):
                alpha = 255 - i*25
                pygame.draw.circle(
                    surface, (*self.color, alpha),
                    (int(self.x), int(self.y + i*5)),
                    3 - i*0.2
                )
        else:
            for p in self.particles:
                p.draw(surface)

class Background:
    """背景类（仅修改渐变颜色）"""
    def __init__(self):
        self.stars = [self.create_star() for _ in range(200)]
    
    def create_star(self):
        return {
            'pos': (random.randint(0, WIDTH), random.randint(0, HEIGHT//2)),
            'size': random.uniform(0.5, 1.5),
            'twinkle': random.uniform(0.5, 2)
        }
    
    def draw_gradient(self, surface):
        """实现紫蓝渐变"""
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            # 红色通道从70渐变到0
            r = int(NIGHT_SKY_COLORS[0][0] * (1 - ratio))
            # 绿色通道保持0渐变到50
            g = int(NIGHT_SKY_COLORS[1][1] * ratio)
            # 蓝色通道从100渐变到150
            b = int(NIGHT_SKY_COLORS[0][2] + (NIGHT_SKY_COLORS[1][2]-NIGHT_SKY_COLORS[0][2])*ratio)
            pygame.draw.line(surface, (r,g,b), (0,y), (WIDTH,y))
    
    def draw_stars(self, surface):
        for star in self.stars:
            alpha = abs(int(127 * math.sin(pygame.time.get_ticks()/1000 * star['twinkle'])))
            pygame.draw.circle(
                surface, (200, 200, 255, alpha),  # 微调星星为冷白色
                star['pos'], int(star['size'])
            )
    
    def draw(self, surface):
        self.draw_gradient(surface)
        self.draw_stars(surface)

# 初始化系统
background = Background()
fireworks = []
pygame.time.set_timer(pygame.USEREVENT, 800)

# 主循环（保持不变）
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.USEREVENT:
            fireworks.append(Firework())

    screen.fill((0, 0, 0))
    background.draw(screen)
    
    for fw in fireworks[:]:
        fw.update()
        fw.draw(screen)

        if fw.exploded and not fw.particles:
            BOOM.play()
            fireworks.remove(fw)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
