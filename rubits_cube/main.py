import pygame
import time
import json

# 初始化 Pygame
pygame.init()

# 定义常量
WIDTH, HEIGHT = 800, 600
# 背景色
BACKGROUND_COLOR = (240, 240, 240)
# 文字颜色
TEXT_COLOR = (50, 50, 50)
# 按钮背景色
BUTTON_COLOR = (0, 123, 255)
# 按钮悬停背景色
BUTTON_HOVER_COLOR = (0, 100, 205)
# 按钮文字颜色
BUTTON_TEXT_COLOR = (255, 255, 255)
# 标题字体
TITLE_FONT = pygame.font.Font('game.ttc', 72)
# 普通字体
FONT = pygame.font.Font('game.ttc', 36)

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("魔方游戏")

# 初始化账户和计时相关变量
account = "默认账户"
timer_running = False
start_time = 0
elapsed_time = 0

# 每次运行重置时间
elapsed_time = 0

# 段位划分
ranks = {
    30: "大师",
    60: "高手",
    120: "能手",
    float('inf'): "新手"
}

# 加载账户信息
try:
    with open("progress.json", "r") as file:
        data = json.load(file)
        account = data.get("account", "默认账户")
except FileNotFoundError:
    pass


def get_rank(time):
    for limit, rank in ranks.items():
        if time <= limit:
            return rank


# 绘制按钮函数
def draw_button(x, y, width, height, text, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, (x, y, width, height))
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, (x, y, width, height))

    button_text = FONT.render(text, True, BUTTON_TEXT_COLOR)
    screen.blit(button_text, (x + (width - button_text.get_width()) // 2,
                              y + (height - button_text.get_height()) // 2))


# 开始计时函数
def start_timer():
    global timer_running, start_time
    if not timer_running:
        start_time = time.time()
        timer_running = True


# 停止计时函数
def stop_timer():
    global timer_running, elapsed_time
    if timer_running:
        elapsed_time = time.time() - start_time
        timer_running = False


# 主循环
running = True
while running:
    screen.fill(BACKGROUND_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 更新计时
    if timer_running:
        current_time = time.time() - start_time
    else:
        current_time = elapsed_time

    # 绘制标题
    title_text = TITLE_FONT.render("魔方游戏", True, TEXT_COLOR)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    # 显示账户
    account_text = FONT.render(f"账户: {account}", True, TEXT_COLOR)
    screen.blit(account_text, (WIDTH // 2 - account_text.get_width() // 2, 150))

    # 显示时间
    minutes = int(current_time // 60)
    seconds = int(current_time % 60)
    time_text = FONT.render(f"时间: {minutes:02d}:{seconds:02d}", True, TEXT_COLOR)
    screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, 200))

    # 显示段位
    rank = get_rank(current_time)
    rank_text = FONT.render(f"段位: {rank}", True, TEXT_COLOR)
    screen.blit(rank_text, (WIDTH // 2 - rank_text.get_width() // 2, 250))

    # 绘制按钮
    draw_button(250, 350, 150, 50, "开始", start_timer)
    draw_button(450, 350, 150, 50, "停止", stop_timer)

    pygame.display.flip()

# 保存账户信息
data = {
    "account": account
}
try:
    with open("progress.json", "w") as file:
        json.dump(data, file)
except Exception as e:
    print(f"保存进度时出错: {e}")

# 退出 Pygame
pygame.quit()
    