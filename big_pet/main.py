import pygame
import math
import random

# 初始化Pygame
pygame.init()

# 窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("星空捏捏乐")

# 颜色定义
GEL_COLOR = (173, 216, 230, 200)    # 半透明浅蓝色
BLUSH_COLOR = (255, 182, 193, 100)  # 腮红粉
HIGHLIGHT_COLOR = (255, 255, 255, 80)
SHADOW_COLOR = (135, 206, 235, 80)

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(1, 3)
        self.blink_speed = random.uniform(0.01, 0.03)
        self.alpha = random.randint(100, 255)

    def update(self):
        self.alpha = 100 + int(155 * abs(math.sin(pygame.time.get_ticks() * self.blink_speed)))

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 255, self.alpha), (int(self.x), int(self.y)), int(self.size))

class JellyPet:
    def __init__(self):
        self.base_radius = 80
        self.radius = self.base_radius
        self.pos = [WIDTH//2, HEIGHT//2]
        self.dragging = False
        self.press_start = 0  # 按压计时
        
        # 物理参数
        self.velocity = [0, 0]
        self.stiffness = 0.25
        self.damping = 0.88
        
        # 动画参数
        self.squeeze_factor = 0.0
        self.idle_counter = 0
        self.eye_offset = 15
        self.mouth_openness = 0.0
        self.color_multiplier = 1.0  # 颜色变化系数

    def update(self, mouse_pos):
        # 按压时间反馈
        if self.dragging:
            press_duration = pygame.time.get_ticks() - self.press_start
            self.squeeze_factor = min(1.5, 1.0 + press_duration * 0.0005)
            self.color_multiplier = 1.0 + press_duration * 0.0003
        else:
            self.color_multiplier = max(1.0, self.color_multiplier - 0.02)

        # 闲置呼吸动画
        if not self.dragging:
            self.idle_counter += 0.04
            self.pos[1] += math.sin(self.idle_counter) * 1.5
            self.mouth_openness = abs(math.sin(self.idle_counter/2)) * 5

        # 弹性恢复
        self.radius += (self.base_radius - self.radius) * 0.15
        self.squeeze_factor = max(0.0, self.squeeze_factor - 0.02)

        # 拖拽物理效果
        if self.dragging:
            target_pos = list(mouse_pos)
            self.velocity = [
                (target_pos[0] - self.pos[0]) * self.stiffness,
                (target_pos[1] - self.pos[1]) * self.stiffness
            ]
            self.mouth_openness = 8

        # 运动更新
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.velocity = [v * self.damping for v in self.velocity]

    def draw(self, surface):
        current_radius = self.radius * (1 - 0.2 * self.squeeze_factor)
        squeeze_ratio = 1 - 0.4 * self.squeeze_factor
        
        # 动态颜色计算
        current_color = (
            min(255, int(GEL_COLOR[0] * self.color_multiplier)),
            min(255, int(GEL_COLOR[1] * self.color_multiplier)),
            min(255, int(GEL_COLOR[2] * self.color_multiplier)),
            GEL_COLOR[3]
        )
        
        # 创建可变形表面
        body_surf = pygame.Surface((current_radius*2, current_radius*2), pygame.SRCALPHA)
        rect = body_surf.get_rect()
        
        # 绘制阴影层
        pygame.draw.ellipse(body_surf, SHADOW_COLOR, rect.inflate(-10, -10))
        
        # 绘制主体
        pygame.draw.ellipse(body_surf, current_color, rect)
        
        # 添加高光效果
        highlight_rect = rect.move(-10*self.squeeze_factor, -15).inflate(-30, -50)
        pygame.draw.ellipse(body_surf, HIGHLIGHT_COLOR, highlight_rect)
        
        # 添加挤压变形
        body_surf = pygame.transform.scale(body_surf, 
            (int(current_radius*2 * squeeze_ratio), int(current_radius*2)))
        
        body_rect = body_surf.get_rect(center=self.pos)
        surface.blit(body_surf, body_rect)
        
        # 绘制腮红
        blush_offset = 35 * (1 - self.squeeze_factor*0.5)
        for side in [-1, 1]:
            blush_pos = (
                self.pos[0] + side * blush_offset * 0.8,
                self.pos[1] + 15
            )
            pygame.draw.circle(surface, BLUSH_COLOR, blush_pos, 
                            int(18 * (1 + self.squeeze_factor*0.3)))
        
        # 绘制眼睛
        mouse_pos = pygame.mouse.get_pos()
        eye_dir = (mouse_pos[0]-self.pos[0], mouse_pos[1]-self.pos[1])
        if (eye_len := math.hypot(*eye_dir)) > 0:
            eye_dir = (eye_dir[0]/eye_len*self.eye_offset, 
                      eye_dir[1]/eye_len*self.eye_offset*0.6)
            eye_pos = (self.pos[0]+eye_dir[0], self.pos[1]+eye_dir[1]-5)
            
            # 眼白
            pygame.draw.circle(surface, (255,255,255,200), eye_pos, 12)
            # 瞳孔
            pygame.draw.circle(surface, (30,30,30), eye_pos, 6)
            # 高光
            pygame.draw.circle(surface, (255,255,255), 
                            (eye_pos[0]+3, eye_pos[1]-3), 3)
        
        # 绘制嘴巴
        mouth_rect = (self.pos[0]-25, self.pos[1]+20, 50, 20)
        start_ang = math.pi/6 * (1 + self.mouth_openness*0.2)
        end_ang = math.pi*5/6 * (1 - self.mouth_openness*0.1)
        pygame.draw.arc(surface, (60,60,60), mouth_rect, start_ang, end_ang, 3)

    def squeeze(self):
        self.press_start = pygame.time.get_ticks()
        self.radius *= 0.75

    def release(self):
        pass

# 初始化实例
pet = JellyPet()
clock = pygame.time.Clock()
running = True

# 创建星空
stars = [Star() for _ in range(100)]
clouds = [(
    random.randint(-200, WIDTH+200),
    random.randint(50, HEIGHT//2),
    random.uniform(0.1, 0.3)
) for _ in range(5)]

while running:
    # 动态星空背景
    screen.fill((5, 5, 30))  # 深蓝色背景
    
    # 绘制闪烁星星
    for star in stars:
        star.update()
        star.draw(screen)
    
    # 绘制流动云朵
    for i, (x, y, speed) in enumerate(clouds):
        x += pygame.time.get_ticks() * speed % (WIDTH + 400) - 200
        alpha = 30 + int(125 * (math.sin(pygame.time.get_ticks()*0.001 + i)*0.5 + 0.5))
        size = 50 + int(30 * math.sin(pygame.time.get_ticks()*0.001 + i))
        
        # 云朵形状
        pygame.draw.circle(screen, (255, 255, 255, alpha), (int(x), y), size)
        pygame.draw.circle(screen, (255, 255, 255, alpha), (int(x)+size//2, y-size//3), size//2)
        pygame.draw.circle(screen, (255, 255, 255, alpha), (int(x)-size//2, y+size//4), size//1.5)
    
    # 处理事件
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            distance = math.hypot(mouse_pos[0]-pet.pos[0], mouse_pos[1]-pet.pos[1])
            if distance < pet.radius:
                pet.dragging = True
                pet.squeeze()
        elif event.type == pygame.MOUSEBUTTONUP:
            pet.dragging = False
            pet.release()
    
    # 更新状态
    pet.update(mouse_pos if pet.dragging else None)
    
    # 绘制元素
    pet.draw(screen)
    
    # 绘制拖拽指示器
    if pet.dragging:
        t = (pygame.time.get_ticks() - pet.press_start) * 0.001
        line_alpha = min(255, int(200 * (0.5 + 0.5 * math.sin(t * 10))))
        pygame.draw.line(screen, (200,200,200,line_alpha), mouse_pos, pet.pos, 2 + int(t * 2))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()