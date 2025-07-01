import pygame
import random
import math

# 初始化
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("极速刮鳞挑战")

# 颜色配置
COLORS = {
    "bg": (8, 24, 88),
    "fish": (200, 50, 50),
    "scale": (255, 180, 50),
    "progress_bg": (40, 40, 40),
    "progress_fg": (0, 200, 100),
    "cursor": (255, 255, 200)
}

# 游戏参数
LEVELS = [
    {"scales": 10, "fish_size": (400, 200)},
    {"scales": 20, "fish_size": (500, 250)},
    {"scales": 30, "fish_size": (600, 300)},
    {"scales": 40, "fish_size": (700, 350)},
    {"scales": 50, "fish_size": (800, 400)}
]

class FishScale:
    def __init__(self, fish_rect):
        self.pos = (
            random.randint(fish_rect.left + 60, fish_rect.right - 60),
            random.randint(fish_rect.top + 60, fish_rect.bottom - 60)
        )
        self.active = True
        self.radius = 30  # 检测半径

class Game:
    def __init__(self):
        self.level = 0
        self.scales = []
        self.particles = []
        self.cursor_radius = 40
        self.init_level()
        
    def init_level(self):
        fish_w, fish_h = LEVELS[self.level]["fish_size"]
        self.fish_rect = pygame.Rect(WIDTH//2 - fish_w//2, HEIGHT//2 - fish_h//2, fish_w, fish_h)
        self.scales = [FishScale(self.fish_rect) for _ in range(LEVELS[self.level]["scales"])]
        self.total_scales = len(self.scales)  # 直接使用总数量作为完成条件

    def check_scratches(self, mouse_pos):
        for scale in self.scales[:]:
            if scale.active and math.dist(scale.pos, mouse_pos) < self.cursor_radius:
                scale.active = False
                self.create_sparks(mouse_pos)

    def create_sparks(self, pos):
        for _ in range(10):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(2, 5)
            self.particles.append([
                pos[0], pos[1],
                speed * math.cos(angle),
                speed * math.sin(angle),
                random.randint(6, 10)
            ])

    def draw_progress(self):
        remaining = sum(1 for s in self.scales if s.active)
        # 显示剩余鱼鳞数量
        font = pygame.font.Font('game.otf', 48)
        text = font.render(f"Level {self.level+1} - 剩余鳞片: {remaining}", True, COLORS["cursor"])
        screen.blit(text, (20, 20))

# 主程序
clock = pygame.time.Clock()
game = Game()

running = True
while running:
    screen.fill(COLORS["bg"])
    mouse_pos = pygame.mouse.get_pos()
    
    # 绘制鱼身
    pygame.draw.ellipse(screen, COLORS["fish"], game.fish_rect)
    
    # 处理刮除
    game.check_scratches(mouse_pos)
    
    # 绘制鱼鳞
    for scale in game.scales:
        if scale.active:
            pygame.draw.circle(screen, COLORS["scale"], scale.pos, 15)
    
    # 绘制粒子特效
    for p in game.particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 0.5
        if p[4] > 0:
            pygame.draw.circle(screen, (255, 255, 180), (int(p[0]), int(p[1])), int(p[4]))
        else:
            game.particles.remove(p)
    
    # 绘制进度信息
    game.draw_progress()
    
    # 绘制光标
    pygame.draw.circle(screen, COLORS["cursor"], mouse_pos, game.cursor_radius, 3)
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # 关卡跳转逻辑（修改部分）
    if all(not s.active for s in game.scales):  # 全部清理完成
        if game.level == 4:
            # 最终通关
            font = pygame.font.Font('game.otf', 100)
            text = font.render("挑战完成！", True, (255, 215, 0))
            screen.blit(text, (WIDTH//2 - 200, HEIGHT//2 - 50))
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False
        else:
            # 进入下一关
            game.level += 1
            game.init_level()
            # 添加关卡过渡效果
            screen.fill(COLORS["bg"])
            font = pygame.font.Font('game.otf', 80)
            text = font.render(f"第 {game.level} 关 完成！", True, COLORS["cursor"])
            screen.blit(text, (WIDTH//2 - 180, HEIGHT//2 - 40))
            pygame.display.flip()
            pygame.time.wait(1000)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()