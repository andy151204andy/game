import pygame
import random
import math
import noise
from pygame.locals import *
from pygame import gfxdraw
from pygame.math import Vector2, Vector3

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720), HWSURFACE|DOUBLEBUF|SCALED)
pygame.display.set_caption("电影级天气模拟器 v3.4")
clock = pygame.time.Clock()

# 高级HDR调色配置
WEATHER_PROFILES = {
    'sunny': {
        'sky_gradient': [(98, 192, 255), (135, 206, 250)],
        'light_color': (255, 255, 210, 80),
        'cloud_color': (255, 255, 255, 180),
        'sun_position': Vector2(1000, 100)
    },
    'rainy': {
        'sky_gradient': [(35, 75, 120), (15, 40, 80)],
        'light_color': (150, 180, 220, 100),
        'rain_color': (200, 220, 255),
        'lightning_prob': 0.003
    },
    'snowy': {
        'sky_gradient': [(200, 220, 240), (170, 200, 220)],
        'light_color': (255, 255, 255, 150),
        'snow_color': (240, 248, 255)
    },
    'foggy': {
        'sky_gradient': [(120, 150, 180), (160, 180, 200)],
        'fog_color': (255, 255, 255, 120),
        'fog_density': 0.8
    },
    'night': {
        'sky_gradient': [(5, 5, 30), (25, 35, 80)],
        'moon_color': (220, 230, 255, 100),
        'star_color': (255, 255, 255, 200)
    }
}

class ParticleEngine:
    def __init__(self):
        # 初始化粒子系统
        self.rain_particles = [{
            'pos': Vector2(random.randint(-100, 1380), random.randint(-500, -50)),
            'speed': random.uniform(15, 25),
            'length': random.uniform(10, 20),
            'angle': math.radians(75 + random.uniform(-5, 5))
        } for _ in range(1200)]

        self.snow_flakes = [{
            'pos': Vector3(
                random.uniform(-100, 1380),
                random.uniform(-500, -50),
                random.uniform(1, 3)
            ),
            'drift': random.uniform(-0.5, 0.5)
        } for _ in range(800)]

        self.lightning_paths = []
        self.lightning_timer = 0

    def generate_lightning(self):
        """完全修复的闪电生成"""
        path = []
        start_x = random.randint(300, 980)
        current_pos = Vector2(start_x, 50)
        direction = Vector2(0, 1)
        
        for _ in range(50):
            current_pos += direction * 15 + Vector2(random.uniform(-20,20), 0)
            path.append(Vector2(int(current_pos.x), int(current_pos.y)))  # 确保整数坐标
            direction = direction.rotate(random.uniform(-25,25))
            if random.random() < 0.1:
                break
        return path

    def update_weather(self, weather):
        """统一物理更新"""
        if weather == 'rainy':
            # 更新雨滴
            for p in self.rain_particles:
                p['pos'] += Vector2(
                    math.cos(p['angle']) * p['speed'],
                    math.sin(p['angle']) * p['speed']
                )
                if p['pos'].y > 800:
                    p['pos'] = Vector2(random.randint(-100, 1380), random.randint(-500, -50))
            
            # 生成闪电
            if random.random() < WEATHER_PROFILES['rainy']['lightning_prob']:
                self.lightning_paths = self.generate_lightning()
                self.lightning_timer = 15

        elif weather == 'snowy':
            # 更新雪花
            for flake in self.snow_flakes:
                flake['pos'] += Vector3(
                    flake['drift'] * flake['pos'].z,
                    (1 + flake['pos'].z) * 0.5,
                    0
                )
                if flake['pos'].y > 800:
                    flake['pos'] = Vector3(
                        random.uniform(-100, 1380),
                        random.uniform(-500, -50),
                        random.uniform(1, 3)
                    )

    def render_rain(self, surface):
        """完全修复的雨幕渲染"""
        profile = WEATHER_PROFILES['rainy']
        
        # 渲染雨滴
        for p in self.rain_particles:
            start = p['pos']
            end = start + Vector2(
                math.cos(p['angle']) * p['length'],
                math.sin(p['angle']) * p['length']
            )
            gfxdraw.line(surface, int(start.x), int(start.y), int(end.x), int(end.y), 
                        (*profile['rain_color'], 180))

        # 渲染闪电
        if self.lightning_timer > 0 and len(self.lightning_paths) >= 2:
            for i in range(len(self.lightning_paths)-1):
                start = self.lightning_paths[i]
                end = self.lightning_paths[i+1]
                alpha = min(200, self.lightning_timer*15)
                gfxdraw.line(surface, 
                           int(start.x), int(start.y),
                           int(end.x), int(end.y),
                           (255, 255, 255, alpha))
            self.lightning_timer -= 1

    def render_snow(self, surface):
        """3D雪花渲染"""
        profile = WEATHER_PROFILES['snowy']
        for flake in self.snow_flakes:
            scale = 0.5 + flake['pos'].z * 0.5
            size = int(3 * scale)
            pos = Vector2(
                flake['pos'].x + math.sin(flake['pos'].y * 0.01 + pygame.time.get_ticks()/1000) * 10,
                flake['pos'].y
            )

            for i in range(3):
                alpha = int(200 * (1 - i/3))
                radius = max(1, size - i)
                gfxdraw.filled_circle(surface, int(pos.x), int(pos.y), radius, 
                                    (*profile['snow_color'], alpha))
                gfxdraw.aacircle(surface, int(pos.x), int(pos.y), radius, 
                               (*profile['snow_color'], alpha))

class SkyRenderer:
    def __init__(self):
        self.weather = 'sunny'
        self.cloud_texture = self.generate_cloud_texture()
        self.star_field = self.generate_star_field()

    def generate_cloud_texture(self):
        """云层纹理生成"""
        texture = pygame.Surface((1280, 200), pygame.SRCALPHA)
        pixels = pygame.surfarray.pixels3d(texture)
        alpha = pygame.surfarray.pixels_alpha(texture)
        
        for x in range(1280):
            for y in range(200):
                n = noise.snoise2(x/300, y/100, octaves=3)
                alpha[x][y] = int(180 * max(0, n))
        return texture

    def generate_star_field(self):
        """星空生成"""
        stars = pygame.Surface((1280, 720), pygame.SRCALPHA)
        for _ in range(500):
            x = random.randint(0, 1280)
            y = random.randint(0, 720)
            radius = random.randint(1, 3)
            alpha = random.randint(100, 200)
            gfxdraw.filled_circle(stars, x, y, radius, (255, 255, 255, alpha))
        return stars

    def render_sky(self, surface):
        """天空渲染"""
        profile = WEATHER_PROFILES[self.weather]
        
        # 天空渐变
        for y in range(720):
            t = y / 720
            color = (
                int(profile['sky_gradient'][0][0]*(1-t) + profile['sky_gradient'][1][0]*t),
                int(profile['sky_gradient'][0][1]*(1-t) + profile['sky_gradient'][1][1]*t),
                int(profile['sky_gradient'][0][2]*(1-t) + profile['sky_gradient'][1][2]*t)
            )
            pygame.draw.line(surface, color, (0, y), (1280, y))

        # 天气特效
        if self.weather == 'sunny':
            self.render_sun(surface)
            self.render_clouds(surface)
        elif self.weather == 'night':
            surface.blit(self.star_field, (0, 0))

    def render_sun(self, surface):
        """太阳渲染"""
        profile = WEATHER_PROFILES['sunny']
        sun_pos = profile['sun_position']

        # 光晕效果
        for i in range(1, 5):
            radius = 80 + i * 30
            alpha = 100 - i * 20
            gfxdraw.filled_circle(surface, int(sun_pos.x), int(sun_pos.y), radius, 
                                (*profile['light_color'][:3], alpha))

        # 太阳核心
        gfxdraw.filled_circle(surface, int(sun_pos.x), int(sun_pos.y), 50, 
                            (255, 255, 210, 200))
        gfxdraw.aacircle(surface, int(sun_pos.x), int(sun_pos.y), 50, 
                       (255, 255, 230, 200))

    def render_clouds(self, surface):
        """动态云层"""
        time = pygame.time.get_ticks() / 3000
        cloud_surface = self.cloud_texture.copy()
        
        # 云层移动
        offset = int(time * 100) % 1280
        cloud_surface.scroll(offset//10, 0)
        
        # 阳光透射
        sunlight = pygame.Surface((1280, 200), pygame.SRCALPHA)
        sunlight.fill((255, 255, 200, 30))
        cloud_surface.blit(sunlight, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        surface.blit(cloud_surface, (0, 100))

# 初始化系统
sky_renderer = SkyRenderer()
particle_engine = ParticleEngine()
current_weather = 'sunny'

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key in (K_1, K_2, K_3, K_4, K_5):
                weathers = ['sunny', 'rainy', 'snowy', 'foggy', 'night']
                current_weather = weathers[event.key - K_1]
                sky_renderer.weather = current_weather
            elif event.key == K_q:
                running = False

    # 更新物理系统
    particle_engine.update_weather(current_weather)
    
    # 渲染场景
    screen.fill((0, 0, 0))
    sky_renderer.render_sky(screen)
    
    # 渲染天气特效
    if current_weather == 'rainy':
        particle_engine.render_rain(screen)
    elif current_weather == 'snowy':
        particle_engine.render_snow(screen)
    
    pygame.display.flip()
    clock.tick(60)

