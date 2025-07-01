import pygame
import random
import sys

# 初始化Pygame
pygame.init()
pygame.mixer.quit()
pygame.mixer.init(frequency=44100, channels=8)

# 游戏窗口设置
WIDTH, HEIGHT = 800, 600
FPS = 60
AUDIO_PATH = "meteor/mixer/"

# 加载字体（需要准备中文字体文件）
try:
    font = pygame.font.Font('meteor/game.otf', 24)  # 微软雅黑字体
    title_font = pygame.font.Font('meteor/game.otf', 48)
except:
    font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 48)

# 游戏阶段配置
STAGES = [
    {  # 阶段1
        "target": 200,
        "green_prob": 0.15,
        "bad_prob": 0.25,
        "speed": 4,
        "size": 30,
        "good_score": 5,
        "bad_score": -2,
        "normal_score": 1
    },
    {  # 阶段2
        "target": 400,
        "green_prob": 0.12,
        "bad_prob": 0.3,
        "speed": 5,
        "size": 35,
        "good_score": 8,
        "bad_score": -3,
        "normal_score": 2
    },
    {  # 阶段3
        "target": 600,
        "green_prob": 0.1,
        "bad_prob": 0.35,
        "speed": 6,
        "size": 40,
        "good_score": 12,
        "bad_score": -4,
        "normal_score": 3
    },
    {  # 阶段4
        "target": 800,
        "green_prob": 0.08,
        "bad_prob": 0.4,
        "speed": 7,
        "size": 45,
        "good_score": 15,
        "bad_score": -5,
        "normal_score": 5
    },
    {  # 阶段5
        "target": 1000,
        "green_prob": 0.05,
        "bad_prob": 0.45,
        "speed": 8,
        "size": 50,
        "good_score": 20,
        "bad_score": -8,
        "normal_score": 8
    }
]

# 玩家颜色配置
PLAYER_COLORS = [
    (255, 0, 0),    # 红
    (0, 255, 0),    # 绿
    (0, 0, 255),    # 蓝
    (255, 255, 0),  # 黄
    (255, 0, 255),  # 品红
    (0, 255, 255),  # 青
    (128, 0, 128),  # 紫
    (255, 165, 0),  # 橙
    (128, 128, 128) # 灰
]

# 音频设置

bgm = pygame.mixer.Sound(f"{AUDIO_PATH}bgm.ogg")
sound_good = pygame.mixer.Sound(f"{AUDIO_PATH}green.ogg")
sound_bad = pygame.mixer.Sound(f"{AUDIO_PATH}red.ogg")
sound_normal = pygame.mixer.Sound(f"{AUDIO_PATH}normal.ogg")
sound_end = pygame.mixer.Sound(f"{AUDIO_PATH}end.ogg")
sound_buy = pygame.mixer.Sound(f"{AUDIO_PATH}buy.ogg")
sound_error = pygame.mixer.Sound(f"{AUDIO_PATH}error.ogg")
sound_stage = pygame.mixer.Sound(f"{AUDIO_PATH}stage.ogg")

# 音频通道
bgm_channel = pygame.mixer.Channel(0)
sfx_channel = pygame.mixer.Channel(1)
bgm_channel.set_volume(0.3)
sfx_channel.set_volume(1.0)

# 初始化显示
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("躲避陨石")
clock = pygame.time.Clock()

def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def show_start_screen():
    screen.fill((30, 30, 50))
    
    # 标题
    title_text = title_font.render("躲避陨石", True, (255, 255, 0))
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
    
    # 规则说明
    rules = [
        "游戏规则：",
        "1. 使用 ← → 键移动飞船",
        "2. 绿色陨石: 增加生命 (+分) | 红色陨石: 减少生命 (-分) | 蓝色: 普通",
        "3. 数字键1-9购买皮肤（基础价格 + 当前阶段数×5 + 皮肤序号×3）",
        "4. 每个阶段需要达到目标分数解锁",
        "5. 每进入新阶段获得2点生命奖励",
        "6. total score: 总得分（可购买skin），stage score: 只记录陨石落下数",
        "",
        "按 S 键开始游戏"
    ]
    
    y = 200
    for line in rules:
        text = font.render(line, True, (200, 200, 255))
        screen.blit(text, (100, y))
        y += 40
        
    pygame.display.flip()
    
    # 等待开始指令
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    return

def game_loop():
    player = pygame.Rect(WIDTH//2, HEIGHT-100, 50, 50)
    meteors = []
    meteor_timer = 0
    total_score = 0
    stage_score = 0
    current_stage = 0
    lives = 5
    game_over = False
    color_index = 0
    purchased = [False] * 9
    purchased[0] = True
    info_text = ""
    info_timer = 0
    
    bgm_channel.play(bgm, loops=-1)

    while True:
        stage_config = STAGES[current_stage]
        clock.tick(FPS)
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if not game_over and event.key in (pygame.K_1, pygame.K_2, pygame.K_3,
                                                  pygame.K_4, pygame.K_5, pygame.K_6,
                                                  pygame.K_7, pygame.K_8, pygame.K_9):
                    key_num = event.key - pygame.K_1
                    if 0 <= key_num < 9:
                        if key_num == color_index:
                            continue
                        
                        cost = 15 + (current_stage * 5) + (key_num * 3)
                        if purchased[key_num]:
                            color_index = key_num
                            sfx_channel.play(sound_buy)
                            info_text = f"切换至皮肤 {key_num+1}"
                            info_timer = 30
                        else:
                            if total_score >= cost:
                                total_score -= cost
                                purchased[key_num] = True
                                color_index = key_num
                                sfx_channel.play(sound_buy)
                                info_text = f"购买皮肤 {key_num+1} 花费 {cost}分!"
                                info_timer = 45
                            else:
                                sfx_channel.play(sound_error)
                                info_text = f"需要 {cost}分 购买此皮肤!"
                                info_timer = 60

        # 游戏逻辑
        if not game_over:
            # 阶段更新
            if stage_score >= stage_config["target"] and current_stage < 4:
                current_stage += 1
                stage_score = 0
                sfx_channel.play(sound_stage)
                info_text = f"进入阶段 {current_stage+1}!"
                info_timer = 60
                lives += 2

            # 陨石生成
            meteor_timer += 1
            if meteor_timer > (FPS // 2):
                meteor_timer = 0
                rand = random.random()
                
                if rand < stage_config["green_prob"]:
                    color = (0, 255, 0)
                    m_type = "good"
                elif rand < (stage_config["green_prob"] + stage_config["bad_prob"]):
                    color = (255, 0, 0)
                    m_type = "bad"
                else:
                    color = (0, 0, 255)
                    m_type = "normal"
                
                size = random.randint(stage_config["size"]-5, stage_config["size"]+5)
                meteors.append({
                    "rect": pygame.Rect(random.randint(0, WIDTH-size), -size, size, size),
                    "color": color,
                    "type": m_type,
                    "speed": stage_config["speed"] + random.uniform(-0.5, 0.5)
                })

            # 玩家移动
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player.left > 0:
                player.x -= 7
            if keys[pygame.K_RIGHT] and player.right < WIDTH:
                player.x += 7

            # 陨石更新
            for meteor in meteors[:]:
                meteor["rect"].y += meteor["speed"]
                
                if meteor["rect"].y > HEIGHT:
                    meteors.remove(meteor)
                    stage_score += 1
                    total_score += 1
                
                if meteor["rect"].colliderect(player):
                    if meteor["type"] == "good":
                        lives += 1
                        total_score += stage_config["good_score"]
                        sfx_channel.play(sound_good)
                    elif meteor["type"] == "bad":
                        lives += stage_config["bad_score"]
                        sfx_channel.play(sound_bad)
                    else:
                        lives -= 1
                        total_score += stage_config["normal_score"]
                        sfx_channel.play(sound_normal)
                    
                    meteors.remove(meteor)
                    if lives <= 0:
                        bgm_channel.stop()
                        sfx_channel.play(sound_end)
                        game_over = True

            # 信息计时
            if info_timer > 0:
                info_timer -= 1
                if info_timer == 0:
                    info_text = ""

        # 渲染
        screen.fill((20, 20, 30))
        pygame.draw.rect(screen, PLAYER_COLORS[color_index], player)
        
        for meteor in meteors:
            pygame.draw.ellipse(screen, meteor["color"], meteor["rect"])

        # 游戏信息
        draw_text(f"总分数: {total_score}", (255, 255, 255), 10, 10)
        draw_text(f"阶段: {current_stage+1} ({stage_score}/{stage_config['target']})", (200, 200, 255), 10, 50)
        draw_text(f"生命: {lives}", (255, 50, 50), 10, 90)
        
        # 皮肤商店
        shop_x = WIDTH - 200
        draw_text("[皮肤商店]", (255, 200, 0), shop_x, 10)
        for i in range(9):
            cost = 15 + (current_stage * 5) + (i * 3)
            status = f"{cost}分" if not purchased[i] else "已拥有"
            color = (100, 255, 100) if purchased[i] else (200, 200, 200)
            draw_text(f"{i+1}: {status}", color, shop_x, 40 + i*30)

        if info_text:
            draw_text(info_text, (255, 100, 100) if "需要" in info_text else (100, 255, 100), 
                     WIDTH//2 - 150, HEIGHT - 60)

        if game_over:
            end_text = font.render(f"游戏结束! 最终分数: {total_score}  按 R 重玩 / Q 退出", True, (255, 255, 255))
            screen.blit(end_text, (WIDTH//2 - end_text.get_width()//2, HEIGHT//2 - 20))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                return
            if keys[pygame.K_q]:
                pygame.quit()
                sys.exit()

        pygame.display.update()

def main():
    while True:
        show_start_screen()
        game_loop()

if __name__ == "__main__":
    main()