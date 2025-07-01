import pygame
import math
from pygame.locals import *
import sys

# 初始化pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("催眠动画 - 放松你的眼睛")

# 颜色参数
hue = 0  # 色相初始值
color_speed = 2  # 颜色变化速度

# 动画参数
radius = 100       # 初始半径
growth_speed = 1  # 半径变化速度
max_radius = 250   # 最大半径
min_radius = 50    # 最小半径

clock = pygame.time.Clock()

def draw_hypnosis(surface, center, radius, hue):
    # 绘制多层同心圆
    for i in range(12):
        current_radius = radius + i * 20
        # 将HSL颜色转换为RGB
        color = pygame.Color(0)
        color.hsla = ((hue + i*30) % 360, 100, 50, 0)
        # 绘制空心圆环
        pygame.draw.circle(surface, color, center, current_radius, 5)

running = True
while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    # 清空屏幕
    screen.fill((0, 0, 0))

    # 更新参数
    # 半径变化（呼吸效果）
    radius += growth_speed
    if radius > max_radius or radius < min_radius:
        growth_speed *= -1

    # 颜色变化
    hue = (hue + color_speed) % 360

    # 绘制动画元素
    center = (WIDTH//2, HEIGHT//2)
    draw_hypnosis(screen, center, int(radius), hue)

    # 添加旋转线
    line_length = max_radius + 50
    angle = pygame.time.get_ticks() / 20  # 获取时间用于旋转
    end_pos = (
        center[0] + line_length * math.cos(math.radians(angle)),
        center[1] + line_length * math.sin(math.radians(angle))
    )
    pygame.draw.line(screen, (255, 255, 255), center, end_pos, 3)

    # 更新显示
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()