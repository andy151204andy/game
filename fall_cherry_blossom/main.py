import pygame
import random
import math

# 初始化Pygame
pygame.init()

# 窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("落樱效果")
clock = pygame.time.Clock()

# 颜色定义
WHITE = (255, 255, 255)
PINK = (255, 182, 193)
DARK_PINK = (255, 105, 180)
BG = (171,127,197)

class SakuraPetal:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # 初始位置在屏幕上方随机分布
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        
        # 随机大小
        self.size = random.randint(2, 5)
        
        # 下落速度参数
        self.fall_speed = random.uniform(0.5, 1.5)  # 基础下落速度
        self.wind_speed = random.uniform(-0.5, 0.5)  # 水平方向风速
        
        # 旋转参数
        self.angle = random.randint(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        
        # 轨迹参数
        self.amplitude = random.randint(10, 50)  # 波动幅度
        self.frequency = random.uniform(0.01, 0.05)  # 波动频率
        
        # 生命周期
        self.time = 0
        
    def update(self):
        self.time += 1
        
        # 垂直下落
        self.y += self.fall_speed
        
        # 水平波动（正弦波）
        self.x += math.sin(self.time * self.frequency) * 2 + self.wind_speed
        
        # 自动旋转
        self.angle += self.rotation_speed
        
        # 重置位置当花瓣超出屏幕
        if self.y > HEIGHT + 10 or self.x < -10 or self.x > WIDTH + 10:
            self.reset()
        
    def draw(self):
        # 创建旋转后的花瓣图形
        petal_surf = pygame.Surface((self.size*3, self.size*3), pygame.SRCALPHA)
        
        # 绘制花瓣形状（由两个半圆组成的椭圆）
        pygame.draw.ellipse(petal_surf, PINK, 
                           (0, self.size, self.size*3, self.size*2))
        pygame.draw.ellipse(petal_surf, DARK_PINK, 
                           (0, self.size, self.size*3, self.size*2), 1)
        
        # 旋转并显示
        rotated_surf = pygame.transform.rotate(petal_surf, self.angle)
        screen.blit(rotated_surf, 
                   (self.x - rotated_surf.get_width()//2, 
                    self.y - rotated_surf.get_height()//2))

# 创建花瓣列表
petals = [SakuraPetal() for _ in range(100)]

# 主循环
running = True
while running:
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            running = False
    
    # 更新和绘制
    screen.fill(BG)
    
    # 更新并绘制所有花瓣
    for petal in petals:
        petal.update()
        petal.draw()
    
    # 控制帧率
    pygame.display.flip()
    clock.tick(60)

pygame.quit()