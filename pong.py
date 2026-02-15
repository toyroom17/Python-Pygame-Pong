import pygame
import sys
import random
import math
import time

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong with Back to Menu & Dynamic Speed")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
HOVER_GRAY = (150, 150, 150)
CLICK_GRAY = (200, 200, 200)
HOVER_DARK = (70, 70, 70)
CLICK_DARK = (120, 120, 120)

# Game settings
FPS = 60
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
BALL_SIZE = 15
PADDLE_SPEED = 7
BALL_SPEED = 4  # Initial ball speed
BALL_PAUSE_TIME = 1.5  # Seconds to pause when spawning
SPEED_INCREMENT = 0.5  # Increase speed after 10 hits

# Fonts
base_font_size = 50
small_font = pygame.font.SysFont(None, 36)

# Clock
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()

# Paddle and Ball Classes
class Paddle(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)

class Ball(pygame.Rect):
    def __init__(self):
        super().__init__(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
        self.speed_x = 0  # Start paused
        self.speed_y = 0
        self.spawn_time = time.time()  # Track spawn

    def activate(self):
        self.speed_x = BALL_SPEED * random.choice([-1, 1])
        self.speed_y = BALL_SPEED * random.choice([-1, 1])

# Draw rounded button with hover/click effects
def draw_button(surface, rect, base_color, hover_color, click_color, text, font, text_color, mouse_down):
    mx, my = pygame.mouse.get_pos()
    hovered = rect.collidepoint((mx, my))
    if hovered and mouse_down:
        color = click_color
    elif hovered:
        color = hover_color
    else:
        color = base_color

    pygame.draw.rect(surface, color, rect, border_radius=10)

    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    return hovered

# Main menu with heartbeat text (~20 BPM)
def main_menu():
    mouse_down = False
    while True:
        SCREEN.fill(BLACK)
        current_time = pygame.time.get_ticks() - start_time

        # Heartbeat 20 BPM → 3 sec per beat
        scale = 1 + 0.05 * math.sin(current_time * 0.000333 * 2 * math.pi)
        font_size = int(base_font_size * scale)
        heartbeat_font = pygame.font.SysFont(None, font_size)

        text_surf = heartbeat_font.render("PONG", True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 6 + font_size // 4))
        SCREEN.blit(text_surf, text_rect)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
                click = True

        # Buttons
        ai_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//3, 200, 50)
        human_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//3 + 80, 200, 50)
        easy_button = pygame.Rect(WIDTH//2 - 220, HEIGHT//3 + 160, 120, 40)
        medium_button = pygame.Rect(WIDTH//2 - 60, HEIGHT//3 + 160, 120, 40)
        hard_button = pygame.Rect(WIDTH//2 + 100, HEIGHT//3 + 160, 120, 40)

        hover_ai = draw_button(SCREEN, ai_button, GRAY, HOVER_GRAY, CLICK_GRAY, "AI Mode", small_font, WHITE, mouse_down)
        hover_human = draw_button(SCREEN, human_button, GRAY, HOVER_GRAY, CLICK_GRAY, "Human Mode", small_font, WHITE, mouse_down)
        hover_easy = draw_button(SCREEN, easy_button, DARK_GRAY, HOVER_DARK, CLICK_DARK, "Easy", small_font, WHITE, mouse_down)
        hover_medium = draw_button(SCREEN, medium_button, DARK_GRAY, HOVER_DARK, CLICK_DARK, "Medium", small_font, WHITE, mouse_down)
        hover_hard = draw_button(SCREEN, hard_button, DARK_GRAY, HOVER_DARK, CLICK_DARK, "Hard", small_font, WHITE, mouse_down)

        if click:
            if hover_ai:
                game_loop(ai_mode=True, difficulty="Medium")
            if hover_human:
                game_loop(ai_mode=False)
            if hover_easy:
                game_loop(ai_mode=True, difficulty="Easy")
            if hover_medium:
                game_loop(ai_mode=True, difficulty="Medium")
            if hover_hard:
                game_loop(ai_mode=True, difficulty="Hard")

        pygame.display.update()
        clock.tick(FPS)

# Game loop
def game_loop(ai_mode=False, difficulty="Medium"):
    clock = pygame.time.Clock()
    left_paddle = Paddle(50, HEIGHT//2 - PADDLE_HEIGHT//2)
    right_paddle = Paddle(WIDTH - 50 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2)
    ball = Ball()
    left_score = 0
    right_score = 0

    # AI settings
    if difficulty == "Easy":
        ai_speed = PADDLE_SPEED - 4
        ai_mistake_chance = 15
    elif difficulty == "Medium":
        ai_speed = PADDLE_SPEED - 2
        ai_mistake_chance = 7
    else:
        ai_speed = PADDLE_SPEED
        ai_mistake_chance = 3

    hit_count = 0  # Track paddle hits
    mouse_down = False

    running = True
    while running:
        SCREEN.fill(BLACK)
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_down = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_down = False
                click = True

        keys = pygame.key.get_pressed()
        # Left paddle (human)
        if keys[pygame.K_w] and left_paddle.top > 0:
            left_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
            left_paddle.y += PADDLE_SPEED

        # Right paddle
        if ai_mode:
            if ball.speed_x != 0 and ball.speed_x > 0:
                if right_paddle.centery < ball.centery - 10:
                    right_paddle.y += ai_speed
                elif right_paddle.centery > ball.centery + 10:
                    right_paddle.y -= ai_speed
                if random.randint(0, ai_mistake_chance) == 0:
                    right_paddle.y += random.choice([-10, 10])
            if right_paddle.top < 0:
                right_paddle.top = 0
            if right_paddle.bottom > HEIGHT:
                right_paddle.bottom = HEIGHT
        else:
            if keys[pygame.K_UP] and right_paddle.top > 0:
                right_paddle.y -= PADDLE_SPEED
            if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
                right_paddle.y += PADDLE_SPEED

        # Activate ball if pause time passed
        if ball.speed_x == 0 and time.time() - ball.spawn_time >= BALL_PAUSE_TIME:
            ball.activate()

        # Ball movement
        ball.x += ball.speed_x
        ball.y += ball.speed_y

        # Ball collision with paddles
        if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
            ball.speed_x *= -1
            hit_count += 1
            if hit_count >= 10:
                ball.speed_x += SPEED_INCREMENT if ball.speed_x > 0 else -SPEED_INCREMENT
                ball.speed_y += SPEED_INCREMENT if ball.speed_y > 0 else -SPEED_INCREMENT

        # Ball collision with walls
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball.speed_y *= -1

        # Scoring
        if ball.left <= 0:
            right_score += 1
            ball = Ball()
            hit_count = 0
        if ball.right >= WIDTH:
            left_score += 1
            ball = Ball()
            hit_count = 0

        # Draw paddles, ball, midline
        pygame.draw.rect(SCREEN, WHITE, left_paddle)
        pygame.draw.rect(SCREEN, WHITE, right_paddle)
        pygame.draw.ellipse(SCREEN, WHITE, ball)
        pygame.draw.aaline(SCREEN, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

        # Draw scores
        draw_text(str(left_score), pygame.font.SysFont(None, 50), WHITE, SCREEN, WIDTH//4, 20)
        draw_text(str(right_score), pygame.font.SysFont(None, 50), WHITE, SCREEN, WIDTH*3//4, 20)

        # Back to Menu Button
        back_button = pygame.Rect(10, 10, 150, 40)
        hover_back = draw_button(SCREEN, back_button, DARK_GRAY, HOVER_DARK, CLICK_DARK, "Back to Menu", small_font, WHITE, mouse_down)
        if click and hover_back:
            return  # Exit game loop back to main menu

        pygame.display.flip()
        clock.tick(FPS)

def draw_text(text, font, color, surface, x, y):
    txt = font.render(text, True, color)
    surface.blit(txt, (x, y))

# Start game
main_menu()
