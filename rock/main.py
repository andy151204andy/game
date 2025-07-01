import pygame
import random

# 初始化Pygame
pygame.init()

# 游戏窗口设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("矿工模拟器")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

# 游戏状态
class GameState:
    def __init__(self):
        self.money = 0
        self.pickaxe_level = 1
        self.inventory = {
            "coal": 0,
            "iron": 0,
            "gold": 0
        }
        self.miner_x = SCREEN_WIDTH // 2
        self.miner_y = SCREEN_HEIGHT // 2
        self.miner_speed = 5
        self.ores = []
        self.max_ores = 10

# 创建游戏状态实例
game_state = GameState()

# 矿石属性
ORE_TYPES = [
    {"name": "coal", "color": BLACK, "value": 10},
    {"name": "iron", "color": GRAY, "value": 20},
    {"name": "gold", "color": YELLOW, "value": 50}
]

# 生成矿石
def generate_ore():
    if len(game_state.ores) < game_state.max_ores:
        ore_type = random.choice(ORE_TYPES)
        return {
            "type": ore_type,
            "x": random.randint(50, SCREEN_WIDTH - 50),
            "y": random.randint(50, SCREEN_HEIGHT - 50),
            "progress": 0
        }
    return None

# 游戏循环
running = True
clock = pygame.time.Clock()
mining = False
current_ore = None

while running:
    screen.fill(BROWN)  # 背景颜色
    
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:  # 卖矿
                for ore in game_state.inventory:
                    game_state.money += game_state.inventory[ore] * ORE_TYPES[[o["name"] for o in ORE_TYPES].index(ore)]["value"]
                game_state.inventory = {k: 0 for k in game_state.inventory}
            
            if event.key == pygame.K_u:  # 升级工具
                if game_state.money >= 100 * game_state.pickaxe_level:
                    game_state.money -= 100 * game_state.pickaxe_level
                    game_state.pickaxe_level += 1

    # 矿工移动
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        game_state.miner_x = max(20, game_state.miner_x - game_state.miner_speed)
    if keys[pygame.K_d]:
        game_state.miner_x = min(SCREEN_WIDTH - 20, game_state.miner_x + game_state.miner_speed)
    if keys[pygame.K_w]:
        game_state.miner_y = max(20, game_state.miner_y - game_state.miner_speed)
    if keys[pygame.K_s]:
        game_state.miner_y = min(SCREEN_HEIGHT - 20, game_state.miner_y + game_state.miner_speed)

    # 挖矿逻辑
    if keys[pygame.K_SPACE]:
        for ore in game_state.ores[:]:
            distance = ((game_state.miner_x - ore["x"])**2 + (game_state.miner_y - ore["y"])**2)**0.5
            if distance < 30:
                ore["progress"] += 0.5 / game_state.pickaxe_level
                if ore["progress"] >= 1:
                    game_state.inventory[ore["type"]["name"]] += 1
                    game_state.ores.remove(ore)
                break
    else:
        current_ore = None

    # 生成新矿石
    if random.random() < 0.02:
        new_ore = generate_ore()
        if new_ore:
            game_state.ores.append(new_ore)

    # 绘制矿石
    for ore in game_state.ores:
        pygame.draw.circle(screen, ore["type"]["color"], (ore["x"], ore["y"]), 10)
        if ore["progress"] > 0:
            pygame.draw.rect(screen, WHITE, (ore["x"]-15, ore["y"]-20, 30, 5))
            pygame.draw.rect(screen, GREEN, (ore["x"]-15, ore["y"]-20, 30 * ore["progress"], 5))

    # 绘制矿工
    pygame.draw.circle(screen, BLUE, (game_state.miner_x, game_state.miner_y), 15)
    
    # 绘制UI
    font = pygame.font.Font('game.otf', 24)
    text = font.render(f"金钱: {game_state.money}", True, WHITE)
    screen.blit(text, (10, 10))
    
    text = font.render(f"镐等级: {game_state.pickaxe_level}", True, WHITE)
    screen.blit(text, (10, 40))
    
    inventory_text = "背包: " + ", ".join([f"{k}:{v}" for k, v in game_state.inventory.items()])
    text = font.render(inventory_text, True, WHITE)
    screen.blit(text, (10, 70))
    
    controls = "移动: WASD  挖矿: 空格  卖矿: E  升级: U"
    text = font.render(controls, True, WHITE)
    screen.blit(text, (SCREEN_WIDTH//2 - 150, 10))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()