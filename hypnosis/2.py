import pygame
import random
from pygame.locals import *

# 初始化
pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 波纹粒子系统
class Ripple:
    def __init__(self, pos, color_speed=0.8):
        self.pos = pos
        self.radius = 1
        self.max_radius = random.randint(200, 400)
        self.speed = random.uniform(1.2, 2.5)
        self.hue = random.randint(0, 360)
        self.color_speed = color_speed
        self.alpha = 255

    def update(self):
        self.radius += self.speed
        self.hue = (self.hue + self.color_speed) % 360
        self.alpha = max(0, 255 - (self.radius/self.max_radius)*380)
        return self.radius < self.max_radius

# 生成渐变色环
def draw_ripple(surface, ripple):
    color = pygame.Color(0)
    color.hsla = (ripple.hue, 100, 50, 0)
    color.a = int(ripple.alpha)
    
    # 多层绘制实现光晕效果
    for i in range(3):
        radius = ripple.radius + i*5
        width = max(1, 8 - i*2)
        pygame.draw.circle(surface, color, ripple.pos, int(radius), width)

# 初始化波纹列表
ripples = []
hue_shift = 0

running = True
while running:
    screen.fill((0, 0, 0))
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == MOUSEBUTTONDOWN:
            # 点击生成新波纹源
            for _ in range(3):
                offset = (random.randint(-30,30), random.randint(-30,30))
                ripples.append(Ripple(tuple(map(sum, zip(event.pos, offset)))))
    
    # 自动生成随机波纹
    if random.random() < 0.15:
        pos = (random.randint(200, WIDTH-200), random.randint(200, HEIGHT-200))
        ripples.append(Ripple(pos, color_speed=random.uniform(0.5, 1.2)))
    
    # 更新并绘制所有波纹
    for ripple in ripples[:]:
        if not ripple.update():
            ripples.remove(ripple)
        draw_ripple(screen, ripple)
    
    # 绘制中心焦点
    center = (WIDTH//2, HEIGHT//2)
    pygame.draw.circle(screen, (200, 200, 255), center, 8)
    pygame.draw.circle(screen, (100, 100, 255), center, 4)
    
    # 添加星空效果
    for _ in range(2):
        pygame.draw.circle(screen, 
                         (random.randint(100, 255),)*3,
                         (random.randint(0, WIDTH), random.randint(0, HEIGHT)),
                         random.randint(1, 2))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()