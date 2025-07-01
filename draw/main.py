import pygame
import sys
from pygame.locals import *

# 初始化Pygame
pygame.init()

# 窗口设置
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("天生会画")

# 加载字体

font = pygame.font.Font("Xingkai.ttc", 24)
small_font = pygame.font.Font("Xingkai.ttc", 18)

# 颜色混合函数
def mix_colors(color1, color2):
    return (
        (color1[0] + color2[0]) // 2,
        (color1[1] + color2[1]) // 2,
        (color1[2] + color2[2]) // 2
    )

# 泛洪填充算法
def flood_fill(surface, pos, fill_color):
    try:
        target_color = surface.get_at(pos)
        if target_color == fill_color:
            return
        
        q = [pos]
        surface.lock()
        
        while q:
            x, y = q.pop(0)
            if surface.get_at((x, y)) != target_color:
                continue
            
            surface.set_at((x, y), fill_color)
            
            if x > 0: q.append((x-1, y))
            if x < WIDTH-1: q.append((x+1, y))
            if y > 0: q.append((x, y-1))
            if y < HEIGHT-1: q.append((x, y+1))
        
        surface.unlock()
    except:
        pass

# 工具类型枚举
class Tool:
    BRUSH = "brush"
    ERASER = "eraser"
    LINE = "line"
    RECT = "rect"
    CIRCLE = "circle"

# 备用图标生成
def create_fallback_icon(text, size=(50,50)):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surf, (100,100,100), (0,0,*size), border_radius=8)
    text_surf = small_font.render(text[:3], True, (255,255,255))
    text_rect = text_surf.get_rect(center=(size[0]//2, size[1]//2))
    surf.blit(text_surf, text_rect)
    return surf

# 界面元素
tool_icons = {
    "brush": create_fallback_icon("画笔"),
    "eraser": create_fallback_icon("橡皮"),
    "line": create_fallback_icon("直线"),
    "rect": create_fallback_icon("矩形"),
    "circle": create_fallback_icon("圆形"),
    "clear": create_fallback_icon("清空")
}

# 创建网格模板
template_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(0, HEIGHT, 50):
    pygame.draw.line(template_surface, (200, 200, 200, 100), (0, y), (WIDTH, y), 1)
for x in range(0, WIDTH, 50):
    pygame.draw.line(template_surface, (200, 200, 200, 100), (x, 0), (x, HEIGHT), 1)

# 颜色系统
base_colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0)]
mixed_colors = []
selected_colors = []
current_color = (0, 0, 0)

# 绘图系统
canvas = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
canvas.fill((255, 255, 255, 0))
drawing = False
last_pos = None
start_pos = None
current_tool = Tool.BRUSH
brush_size = 5
temp_surface = None
is_template_mode = False

# UI参数
TOOL_SIZE = 60
UI_PADDING = 20
UI_COLOR = (34, 40, 49)
HOVER_COLOR = (78, 88, 104)

# 工具按钮布局
tools = [
    {"type": Tool.BRUSH, "pos": (UI_PADDING, UI_PADDING)},
    {"type": Tool.ERASER, "pos": (UI_PADDING, UI_PADDING*2 + TOOL_SIZE)},
    {"type": "clear", "pos": (UI_PADDING, UI_PADDING*3 + TOOL_SIZE*2)},
    {"type": Tool.LINE, "pos": (UI_PADDING, UI_PADDING*4 + TOOL_SIZE*3)},
    {"type": Tool.RECT, "pos": (UI_PADDING, UI_PADDING*5 + TOOL_SIZE*4)},
    {"type": Tool.CIRCLE, "pos": (UI_PADDING, UI_PADDING*6 + TOOL_SIZE*5)}
]

def draw_rounded_rect(surface, rect, color, radius=8):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def handle_color_mixing():
    global selected_colors, mixed_colors
    if len(selected_colors) == 2:
        new_color = mix_colors(selected_colors[0], selected_colors[1])
        if new_color not in base_colors + mixed_colors:
            mixed_colors.append(new_color)
        selected_colors = []

def draw_ui():
    # 左侧工具栏
    sidebar = pygame.Rect(0, 0, 100, HEIGHT)
    pygame.draw.rect(screen, UI_COLOR, sidebar)
    
    # 绘制工具按钮
    mouse_pos = pygame.mouse.get_pos()
    for tool in tools:
        x, y = tool["pos"]
        rect = pygame.Rect(x, y, TOOL_SIZE, TOOL_SIZE)
        color = HOVER_COLOR if rect.collidepoint(mouse_pos) else UI_COLOR
        
        # 绘制按钮背景
        draw_rounded_rect(screen, rect, color)
        
        # 绘制工具图标
        icon = tool_icons.get(tool["type"], None)
        if icon:
            icon_rect = icon.get_rect(center=rect.center)
            screen.blit(icon, icon_rect)
        
        # 当前工具高亮
        if current_tool == tool.get("type"):
            pygame.draw.rect(screen, (0, 173, 181), rect.inflate(8,8), 3, 8)
    
    # 右侧颜色面板
    color_panel = pygame.Rect(WIDTH-260, 20, 240, HEIGHT-40)
    draw_rounded_rect(screen, color_panel, UI_COLOR)
    
    # 基础颜色
    base_text = small_font.render("基础颜色", True, (255,255,255))
    screen.blit(base_text, (WIDTH-240, 30))
    for i, color in enumerate(base_colors):
        x = WIDTH - 240 + (i%2)*100
        y = 60 + (i//2)*80
        rect = pygame.Rect(x, y, 80, 60)
        draw_rounded_rect(screen, rect, color)
        if color in selected_colors:
            pygame.draw.rect(screen, (255,255,0), rect.inflate(6,6), 3, 8)
    
    # 混合颜色（多行显示）
    mix_text = small_font.render("混合颜色", True, (255,255,255))
    screen.blit(mix_text, (WIDTH-240, 180))
    
    cols = 5
    color_size = 35
    start_y = 220
    for i, color in enumerate(mixed_colors):
        row = i // cols
        col = i % cols
        x = WIDTH - 240 + col * (color_size + 5)
        y = start_y + row * (color_size + 5)
        rect = pygame.Rect(x, y, color_size, color_size)
        draw_rounded_rect(screen, rect, color, 6)
        
        if color in selected_colors:
            pygame.draw.rect(screen, (255,255,0), rect.inflate(4,4), 2, 6)

def draw_preview():
    global temp_surface
    if start_pos and pygame.mouse.get_pressed()[0]:
        end_pos = pygame.mouse.get_pos()
        temp_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        if current_tool == Tool.LINE:
            pygame.draw.line(temp_surface, current_color, start_pos, end_pos, brush_size)
        elif current_tool == Tool.RECT:
            rect = pygame.Rect(start_pos, (end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
            pygame.draw.rect(temp_surface, current_color, rect, brush_size)
        elif current_tool == Tool.CIRCLE:
            radius = int(((end_pos[0]-start_pos[0])**2 + (end_pos[1]-start_pos[1])**2)**0.5)
            pygame.draw.circle(temp_surface, current_color, start_pos, radius, brush_size)
        
        screen.blit(temp_surface, (0, 0))

# 主循环
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # 鼠标事件
        if event.type == MOUSEBUTTONDOWN:
            pos = event.pos
            
            # 工具选择
            for tool in tools:
                x, y = tool["pos"]
                rect = pygame.Rect(x, y, TOOL_SIZE, TOOL_SIZE)
                if rect.collidepoint(pos):
                    if tool["type"] == "clear":
                        canvas.fill((255,255,255,0))
                    else:
                        current_tool = tool["type"]
                        if current_tool == Tool.ERASER:
                            current_color = (255, 255, 255, 0)  # 白色全透明橡皮擦
                        else:
                            current_color = selected_colors[-1] if selected_colors else (0,0,0)
            
            # 颜色选择
            if WIDTH-240 < pos[0] < WIDTH-20 and 20 < pos[1] < HEIGHT-60:
                # 基础颜色
                for i, color in enumerate(base_colors):
                    x = WIDTH - 240 + (i%2)*100
                    y = 60 + (i//2)*80
                    if pygame.Rect(x, y, 80, 60).collidepoint(pos):
                        if event.button == 3:  # 右键删除
                            if color in base_colors and color not in [(255,0,0),(0,255,0),(0,0,255)]:
                                base_colors.remove(color)
                        else:
                            if color in selected_colors:
                                selected_colors.remove(color)
                            else:
                                if len(selected_colors) < 2:
                                    selected_colors.append(color)
                            current_color = color
                
                # 混合颜色
                cols = 5
                for i, color in enumerate(mixed_colors):
                    row = i // cols
                    col = i % cols
                    x = WIDTH - 240 + col * 40
                    y = 220 + row * 40
                    if pygame.Rect(x, y, 35, 35).collidepoint(pos):
                        if event.button == 3:  # 右键删除
                            mixed_colors.remove(color)
                        else:
                            if color in selected_colors:
                                selected_colors.remove(color)
                            else:
                                if len(selected_colors) < 2:
                                    selected_colors.append(color)
                            current_color = color
            
            # 开始绘图
            start_pos = pos
            last_pos = pos
            drawing = True

        elif event.type == MOUSEBUTTONUP:
            drawing = False
            handle_color_mixing()
            
            # 保存预览图形
            if temp_surface:
                canvas.blit(temp_surface, (0,0))
                temp_surface = None

        elif event.type == MOUSEMOTION and drawing:
            if current_tool in [Tool.BRUSH, Tool.ERASER]:
                pos = event.pos
                if last_pos:
                    # 平滑绘制算法
                    dx = pos[0] - last_pos[0]
                    dy = pos[1] - last_pos[1]
                    distance = max(abs(dx), abs(dy))
                    for i in range(distance):
                        x = int(last_pos[0] + float(i)/distance*dx)
                        y = int(last_pos[1] + float(i)/distance*dy)
                        pygame.draw.circle(canvas, current_color, (x, y), brush_size)
                    last_pos = pos

        # 键盘事件
        if event.type == KEYDOWN:
            if event.key == K_s:
                save_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                save_surface.fill((255,255,255,255))
                save_surface.blit(canvas, (0,0))
                pygame.image.save(save_surface, "painting.png")
            elif event.key == K_UP:
                brush_size = min(30, brush_size + 2)
            elif event.key == K_DOWN:
                brush_size = max(2, brush_size - 2)
            elif event.key == K_t:
                is_template_mode = not is_template_mode
            elif event.key == K_f:
                try:
                    flood_fill(canvas, pygame.mouse.get_pos(), current_color)
                except:
                    pass

    # 绘制更新
    screen.fill((255, 255, 255))
    screen.blit(canvas, (0, 0))
    draw_ui()
    
    if is_template_mode:
        screen.blit(template_surface, (0,0))
    
    if current_tool in [Tool.LINE, Tool.RECT, Tool.CIRCLE]:
        draw_preview()
    
    pygame.display.flip()
