import pygame
import sys

# 初始化pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("专业MBTI性格测试")

# 颜色方案
BACKGROUND = (51, 51, 51)  # 深灰背景
CARD_BG = (240, 240, 240)  # 浅灰卡片
PRIMARY = (0, 122, 255)    # 蓝色主色
SECONDARY = (255, 152, 0)  # 橙色辅色
TEXT_COLOR = (33, 33, 33)
HIGHLIGHT = (100, 100, 100)

# 字体设置

font_large = pygame.font.Font('mbti.otf', 48)
font_heading = pygame.font.Font('mbti.otf', 36)
font_body = pygame.font.Font('mbti.otf', 28)
font_small = pygame.font.Font('mbti.otf', 24)
font_caption = pygame.font.Font('game.ttc', 20)


# MBTI维度定义
class GameState:
    def __init__(self):
        self.state = 'start'
        self.current_q = 0
        # 修复点：使用维度名称作为字典键
        self.scores = {dim['name']: {k:0 for k in dim['pairs'][0]} for dim in DIMENSIONS}
        self.progress = 0

# 确保DIMENSIONS定义格式正确（示例）：
DIMENSIONS = [
    {
        'name': '外向(E) - 内向(I)', 
        'pairs': [('E', 'I')]
    },
    {
        'name': '实感(S) - 直觉(N)', 
        'pairs': [('S', 'N')]
    },
    {
        'name': '思考(T) - 情感(F)', 
        'pairs': [('T', 'F')]
    },
    {
        'name': '判断(J) - 知觉(P)', 
        'pairs': [('J', 'P')]
    }
]

# 科学的问题库（完整30题示例）
questions = [
    {
        'text': "参加派对时，你通常：",
        'options': [
            {'text': "主动与多人交流，感到精力充沛 (E)", 'scores': {'E': 1}},
            {'text': "与熟悉的人深入交谈 (I)", 'scores': {'I': 1}}
        ]
    },
    {
        'text': "做决策时更依赖：",
        'options': [
            {'text': "逻辑分析和客观事实 (T)", 'scores': {'T': 1}},
            {'text': '个人价值观和他人感受 (F)', 'scores': {'F': 1}}
        ]
    },
    {
        'text': "你更喜欢的周末安排是：",
        'options': [
            {'text': "详细规划的活动 (J)", 'scores': {'J': 1}},
            {'text': '灵活随性的活动 (P)', 'scores': {'P': 1}}
        ]
    },
    {
        'text': "处理问题时倾向于：",
        'options': [
            {'text': "关注具体细节和现实情况 (S)", 'scores': {'S': 1}},
            {'text': '探索可能性与未来趋势 (N)', 'scores': {'N': 1}}
        ]
    },
    # 此处可继续添加更多问题...
]

# 游戏状态管理
class GameState:
    def __init__(self):
        self.state = 'start'
        self.current_q = 0
        self.scores = {dim['name']: {k:0 for k in dim['pairs'][0]} for dim in DIMENSIONS}
        self.progress = 0

game = GameState()

# 主循环
clock = pygame.time.Clock()
running = True

def draw_centered_text(text, font, color, y_offset=0):
    rendered = font.render(text, True, color)
    screen.blit(rendered, (SCREEN_WIDTH//2 - rendered.get_width()//2, 
                          SCREEN_HEIGHT//2 - rendered.get_height()//2 + y_offset))

while running:
    screen.fill(BACKGROUND)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if game.state == 'start':
                if event.key == pygame.K_SPACE:
                    game.state = 'quiz'
            
            elif game.state == 'quiz':
                if event.key in [pygame.K_1, pygame.K_2]:
                    choice = event.key - pygame.K_1
                    current_q = questions[game.current_q]
                    
                    # 更新得分
                    for key in current_q['options'][choice]['scores']:
                        game.scores[next(dim for dim in DIMENSIONS 
                                       if any(k in dim['pairs'][0] for k in key))][key] += 1
                    
                    game.current_q += 1
                    game.progress = min(100, (game.current_q / len(questions)) * 100)
                    
                    if game.current_q >= len(questions):
                        game.state = 'result'
            
            elif game.state == 'result':
                if event.key == pygame.K_r:
                    game.state = 'start'
                    game.current_q = 0
                    game.progress = 0
                    game.scores = {dim['name']: {k:0 for k in dim['pairs'][0]} for dim in DIMENSIONS}

    # 绘制界面
    if game.state == 'start':
        draw_centered_text("MBTI专业测评", font_large, PRIMARY, 50)
        draw_centered_text("发现你的性格密码 · 30道科学问题", font_heading, SECONDARY, 100)
        draw_centered_text("按空格键开始测试", font_caption, TEXT_COLOR, 200)
    
    elif game.state == 'quiz':
        # 进度条
        pygame.draw.rect(screen, CARD_BG, (100, 80, 600, 20))
        pygame.draw.rect(screen, PRIMARY, 
                        (100, 80, int(600 * game.progress/100), 20))
        
        # 当前题目
        q = questions[game.current_q]
        draw_centered_text(q['text'], font_body, TEXT_COLOR)
        
        # 选项
        y_pos = 250
        for i, opt in enumerate(q['options']):
            color = PRIMARY if i == 0 else SECONDARY
            opt_text = font_caption.render(f"{i+1}. {opt['text']}", True, color)
            screen.blit(opt_text, (150, y_pos))
            pygame.draw.line(screen, HIGHLIGHT, (100, y_pos+30), (700, y_pos+30), 2)
            y_pos += 80
        
        # 导航提示
        nav_text = font_small.render(f"进度：{game.current_q}/{len(questions)}", True, TEXT_COLOR)
        screen.blit(nav_text, (SCREEN_WIDTH-250, 550))
    
    elif game.state == 'result':
        # 结果标题
        draw_centered_text("测试结果", font_large, PRIMARY, 50)
        draw_centered_text("你的MBTI人格类型", font_heading, SECONDARY, 100)
        
        # 生成结果
        result = []
        for dim in DIMENSIONS:
            a, b = dim['pairs'][0]
            result.append(f"{a}: {game.scores[a]} vs {b}: {game.scores[b]}")
        result_type = ''.join([dim['pairs'][0][0] if game.scores[dim['pairs'][0][0]] > game.scores[dim['pairs'][0][1]] 
                              else dim['pairs'][0][1] for dim in DIMENSIONS])
        
        # 显示结果
        result_text = font_body.render(f"你的MBTI类型是：{result_type}", True, PRIMARY)
        screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, 250))
        
        # 显示详细得分
        details = ["各维度详细分析："] + result
        for i, text in enumerate(details):
            render_text = font_small.render(text, True, TEXT_COLOR)
            screen.blit(render_text, (100, 350 + i*30))
        
        restart_text = font_caption.render("按R键重新测试", True, SECONDARY)
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 550))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()