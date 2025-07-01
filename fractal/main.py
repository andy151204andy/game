import pygame
import numpy as np
import sys
from pygame.locals import *

# 初始化
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont('consolas', 16)

# 分形参数
MAX_ITER = 256  # 最大迭代次数
ZOOM_FACTOR = 1.1  # 缩放灵敏度
COLOR_SPEED = 0.25  # 颜色变化速度

# 初始化状态
offset_x, offset_y = -0.5, 0  # 初始偏移（居中Mandelbrot）
zoom = 200  # 初始缩放级别
is_dragging = False
last_mouse_pos = (0, 0)
color_phase = 0  # 颜色相位
show_julia = False  # 是否显示Julia集

def generate_palette():
    """生成动态色盘（HSL颜色空间转换）"""
    palette = np.zeros((MAX_ITER, 3), dtype=np.uint8)
    for i in range(MAX_ITER):
        hue = i/MAX_ITER + color_phase
        sat = 100
        lum = 50 * (i/MAX_ITER)**0.5
        # HSL转RGB
        c = (1 - abs(2*lum/100 - 1)) * sat/100
        x = c * (1 - abs((hue*6) % 2 - 1))
        m = lum/100 - c/2
        
        if hue < 1/6:
            r, g, b = c, x, 0
        elif hue < 2/6:
            r, g, b = x, c, 0
        elif hue < 3/6:
            r, g, b = 0, c, x
        elif hue < 4/6:
            r, g, b = 0, x, c
        elif hue < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        palette[i] = ( (r + m)*255, (g + m)*255, (b + m)*255 )
    return palette

def mandelbrot(x, y):
    """向量化计算Mandelbrot集合"""
    c = x + y*1j
    z = np.zeros_like(c)
    mask = np.ones_like(c, dtype=bool)
    iterations = np.zeros(c.shape, dtype=int)
    
    for i in range(MAX_ITER):
        z[mask] = z[mask]**2 + c[mask]
        escaped = np.abs(z) > 2
        iterations[escaped & mask] = i
        mask[escaped] = False
        if not np.any(mask):
            break
    return iterations

def julia(x, y, cx, cy):
    """向量化计算Julia集合"""
    z = x + y*1j
    c = cx + cy*1j
    mask = np.ones_like(z, dtype=bool)
    iterations = np.zeros(z.shape, dtype=int)
    
    for i in range(MAX_ITER):
        z[mask] = z[mask]**2 + c
        escaped = np.abs(z) > 2
        iterations[escaped & mask] = i
        mask[escaped] = False
        if not np.any(mask):
            break
    return iterations

def render_fractal(surface):
    """主渲染函数"""
    global color_phase
    # 生成坐标网格
    x = (np.arange(WIDTH) - WIDTH/2)/zoom + offset_x
    y = (np.arange(HEIGHT) - HEIGHT/2)/zoom + offset_y
    X, Y = np.meshgrid(x, y)
    
    # 选择分形类型
    if show_julia:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cx = (mouse_x - WIDTH/2)/zoom + offset_x
        cy = (mouse_y - HEIGHT/2)/zoom + offset_y
        iterations = julia(X, Y, cx, cy)
    else:
        iterations = mandelbrot(X, Y)
    
    # 应用颜色
    palette = generate_palette()
    color_indices = np.clip(iterations, 0, MAX_ITER-1)
    rgb_array = palette[color_indices]
    
    # 转换为Surface
    surf = pygame.surfarray.make_surface(rgb_array.swapaxes(0,1))
    surface.blit(surf, (0,0))
    
    # 更新颜色相位
    color_phase = (color_phase + COLOR_SPEED/100) % 1

# 主循环
running = True
while running:
    # 事件处理
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键拖动
                is_dragging = True
                last_mouse_pos = event.pos
            elif event.button == 4:  # 滚轮上
                zoom *= ZOOM_FACTOR
            elif event.button == 5:  # 滚轮下
                zoom /= ZOOM_FACTOR
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                is_dragging = False
        elif event.type == MOUSEMOTION and is_dragging:
            dx = (event.pos[0] - last_mouse_pos[0]) / zoom
            dy = (event.pos[1] - last_mouse_pos[1]) / zoom
            offset_x -= dx
            offset_y -= dy
            last_mouse_pos = event.pos
        elif event.type == KEYDOWN:
            if event.key == K_j:  # J键切换Julia集
                show_julia = not show_julia
    
    # 渲染
    screen.fill((0,0,0))
    render_fractal(screen)
    
    # 显示信息
    info = f"Zoom: {zoom:.2f}x | Offset: {offset_x:.4f}, {offset_y:.4f}"
    if show_julia:
        info += " | Julia Set"
    text = font.render(info, True, (255,255,255))
    screen.blit(text, (10, HEIGHT-30))
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()