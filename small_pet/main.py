import pygame
import math
import random
from pygame import gfxdraw

class Config:
    WIDTH, HEIGHT = 800, 600
    FPS = 60
    
    # 颜色配置（腮红颜色增强）
    SKIN = (255, 228, 196)
    BLUSH_COLOR = (255, 180, 180)  # 更饱和的粉色
    EYE_WHITE = (250, 250, 255)
    IRIS_BLUE = (30, 144, 255)
    MOUTH_COLOR = (255, 105, 180)
    NIGHT_SKY = (5, 5, 30)
    
    # 宠物参数
    HEAD_RADIUS = 100
    HEAD_FLOAT_AMP = 5
    EYE_OFFSET_X = 40
    EYE_OFFSET_Y = -15
    EYE_RADIUS = 30
    BLINK_DURATION = 0.4
    BLINK_INTERVAL = (2.5, 3.5)
    MOUTH_RANGE = (0.2, 0.8)
    
    # 星空参数
    STAR_COUNT = 150
    STAR_TWINKLE_SPEED = 0.8

class Star:
    def __init__(self):
        self.x = random.randint(0, Config.WIDTH)
        self.y = random.randint(0, Config.HEIGHT)
        self.base_radius = random.uniform(1.0, 2.5)
        self.phase = random.uniform(0, math.pi*2)
        self.alpha = 150
        
    def update(self, dt):
        self.phase += dt * Config.STAR_TWINKLE_SPEED
        self.alpha = 150 + int(math.sin(self.phase) * 100)
        
    @property
    def radius(self):
        return self.base_radius * (0.8 + 0.2*math.sin(self.phase))

class Eye:
    def __init__(self, base_pos):
        self.base_pos = base_pos
        self.blink_timer = 0.0
        self.is_blinking = False
        self.pupil_pos = base_pos
        
    def start_blink(self):
        if not self.is_blinking:
            self.is_blinking = True
            self.blink_timer = Config.BLINK_DURATION
            
    def update(self, mouse_pos, dt):
        dx = mouse_pos[0] - self.base_pos[0]
        dy = mouse_pos[1] - self.base_pos[1]
        distance = math.hypot(dx, dy)
        
        max_move = Config.EYE_RADIUS * 0.6
        if distance > max_move:
            scale = max_move / distance
            dx *= scale
            dy *= scale
            
        self.pupil_pos = (
            self.base_pos[0] + dx*0.8, 
            self.base_pos[1] + dy*0.8
        )
        
        if self.is_blinking:
            self.blink_timer -= dt
            if self.blink_timer <= 0:
                self.is_blinking = False
                
    def draw(self, surface):
        pygame.draw.circle(surface, Config.EYE_WHITE, self.base_pos, Config.EYE_RADIUS)
        
        if not self.is_blinking:
            pygame.draw.circle(surface, Config.IRIS_BLUE, self.pupil_pos, Config.EYE_RADIUS//2)
            pygame.draw.circle(surface, (0,0,60), self.pupil_pos, Config.EYE_RADIUS//4)
            
            highlight_pos = (
                int(self.pupil_pos[0] - Config.EYE_RADIUS//3),
                int(self.pupil_pos[1] - Config.EYE_RADIUS//3)
            )
            gfxdraw.filled_circle(surface, *highlight_pos, Config.EYE_RADIUS//6, (255,255,255))
        
        if self.is_blinking:
            progress = 1 - (self.blink_timer / Config.BLINK_DURATION)
            close_amount = math.sin(progress * math.pi) * Config.EYE_RADIUS
            
            eyelid_rect = pygame.Rect(
                self.base_pos[0] - Config.EYE_RADIUS,
                self.base_pos[1] - Config.EYE_RADIUS + close_amount,
                Config.EYE_RADIUS * 2,
                Config.EYE_RADIUS * 2
            )
            pygame.draw.ellipse(surface, Config.SKIN, eyelid_rect)
            
            shadow_line = [
                (self.base_pos[0] - Config.EYE_RADIUS, eyelid_rect.centery),
                (self.base_pos[0] + Config.EYE_RADIUS, eyelid_rect.centery)
            ]
            pygame.draw.line(surface, (170,140,110), *shadow_line, 2)

class Mouth:
    def __init__(self):
        self.openness = 0.5
        self.target_openness = 0.5
        
    def update(self, mouse_y, dt):
        target = 1 - (mouse_y / Config.HEIGHT)
        min_open, max_open = Config.MOUTH_RANGE
        self.target_openness = min_open + (max_open-min_open)*target
        self.openness += (self.target_openness - self.openness) * dt*5
        
    def draw(self, surface, head_pos):
        center = (head_pos[0], head_pos[1] + Config.HEAD_RADIUS*0.4)
        width = Config.HEAD_RADIUS * 0.6
        height = Config.HEAD_RADIUS * 0.3 * self.openness
        
        mouth_rect = pygame.Rect(0, 0, width, height)
        mouth_rect.center = center
        pygame.draw.ellipse(surface, Config.MOUTH_COLOR, mouth_rect)
        
        inner_rect = mouth_rect.inflate(-10, -10)
        pygame.draw.ellipse(surface, (200, 60, 100), inner_rect)

class BlinkController:
    def __init__(self):
        self.next_blink = random.uniform(*Config.BLINK_INTERVAL)
        
    def update(self, dt, eyes):
        self.next_blink -= dt
        if self.next_blink <= 0:
            for eye in eyes:
                eye.start_blink()
            self.next_blink = random.uniform(*Config.BLINK_INTERVAL)

class Pet:
    def __init__(self):
        self.head_pos = [Config.WIDTH//2, Config.HEIGHT//2]
        self.float_angle = 0
        
        self.eyes = [
            Eye((Config.WIDTH//2 - Config.EYE_OFFSET_X, 
                Config.HEIGHT//2 + Config.EYE_OFFSET_Y)),
            Eye((Config.WIDTH//2 + Config.EYE_OFFSET_X, 
                Config.HEIGHT//2 + Config.EYE_OFFSET_Y))
        ]
        self.mouth = Mouth()
        self.blink_controller = BlinkController()
        
    def update(self, mouse_pos, dt):
        self.float_angle += dt * 2
        self.head_pos[1] = Config.HEIGHT//2 + \
            math.sin(self.float_angle) * Config.HEAD_FLOAT_AMP
        
        self.blink_controller.update(dt, self.eyes)
        for eye in self.eyes:
            eye.update(mouse_pos, dt)
        self.mouth.update(mouse_pos[1], dt)
        
    def draw(self, surface):
        # 先绘制头部
        pygame.draw.circle(surface, Config.SKIN, 
                          (int(self.head_pos[0]), int(self.head_pos[1])), 
                          Config.HEAD_RADIUS)
        
        # 然后绘制其他器官
        for eye in self.eyes:
            eye.draw(surface)
        self.mouth.draw(surface, self.head_pos)
        
        # 最后绘制腮红（确保在最上层）
        self.draw_blush(surface)
    
    def draw_blush(self, surface):
        """修复腮红颜色显示的新方法"""
        for x_offset in [-1, 1]:
            pos = (
                int(self.head_pos[0] + x_offset * Config.HEAD_RADIUS * 0.6),
                int(self.head_pos[1] + Config.HEAD_RADIUS * 0.3)
            )
            radius = Config.HEAD_RADIUS // 3
            
            # 创建带透明度的表面
            blush_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            
            # 使用增强后的颜色（RGB+Alpha）
            color = (*Config.BLUSH_COLOR, 255)  # 增加不透明度到200
            
            # 绘制渐变腮红
            for r in range(radius, 0, -1):
                alpha = int(255 * (r/radius)**0.8)  # 非线性衰减
                gfxdraw.filled_circle(
                    blush_surf, 
                    radius, radius, r, 
                    (*Config.BLUSH_COLOR, alpha)
                )
            
            surface.blit(blush_surf, (pos[0]-radius, pos[1]-radius))

class Background:
    def __init__(self):
        self.stars = [Star() for _ in range(Config.STAR_COUNT)]
        
    def update(self, dt):
        for star in self.stars:
            star.update(dt)
            
    def draw(self, surface):
        surface.fill(Config.NIGHT_SKY)
        for star in self.stars:
            x = int(star.x)
            y = int(star.y)
            radius = int(star.radius)
            temp_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            gfxdraw.filled_circle(temp_surf, radius, radius, radius, (255, 255, 200, star.alpha))
            surface.blit(temp_surf, (x-radius, y-radius))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption("解压小宠物")
        self.background = Background()
        self.pet = Pet()
        self.clock = pygame.time.Clock()
        
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(Config.FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            mouse_pos = pygame.mouse.get_pos()
            self.background.update(dt)
            self.pet.update(mouse_pos, dt)
            
            self.background.draw(self.screen)
            self.pet.draw(self.screen)
            
            pygame.display.flip()
            
if __name__ == "__main__":
    game = Game()
    game.run()