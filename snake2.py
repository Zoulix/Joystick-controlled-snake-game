import pygame
import random
import numpy as np
import serial  # pour la communication série

# Initialisation série avec l’Arduino (ajuste le port COM)
ser = serial.Serial('COM3', 9600, timeout=1)  # <-- Change COM3 si nécessaire

# Initialisation Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-8, channels=2)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("SNAKE Game")
clock = pygame.time.Clock()

# Couleurs
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Taille des cases
BLOCK_SIZE = 20

# Génère un son 8-bit
def generate_beep(freq=600, duration_ms=100, volume=0.5):
    sample_rate = 44100
    t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), endpoint=False)
    wave = 127 * volume * np.sign(np.sin(2 * np.pi * freq * t)) + 128
    wave = wave.astype(np.uint8)
    stereo_wave = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(stereo_wave)

eat_sound = generate_beep()

font = pygame.font.SysFont(None, 35)

def show_score(score):
    value = font.render("Score: " + str(score), True, WHITE)
    screen.blit(value, [10, 10])

def read_joystick_direction():
    try:
        line = ser.readline().decode('utf-8').strip()
        if line:
            parts = line.split(',')
            if len(parts) == 2:
                x = int(parts[0])
                y = int(parts[1])
                print(f"{x},{y}")

                if y == 0:
                    return 'LEFT'
                elif y > 900:
                    return 'RIGHT'
                elif x > 900:
                    return 'UP'
                elif x == 0:
                    return 'DOWN'
    except:
        pass
    return None

def game_loop():
    game_over = False
    game_close = False

    x = 300
    y = 300
    dx = BLOCK_SIZE
    dy = 0

    snake = []
    length = 1

    food_x = round(random.randrange(0, 800 - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    food_y = round(random.randrange(0, 600 - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE

    while not game_over:
        while game_close:
            screen.fill(BLACK)
            msg = font.render("Game Over! Appuie sur R pour rejouer ou Q pour quitter", True, RED)
            screen.blit(msg, [50, 250])
            show_score(length - 1)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_r:
                        game_loop()

        # Contrôle clavier
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and dx == 0:
                    dx = -BLOCK_SIZE
                    dy = 0
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx = BLOCK_SIZE
                    dy = 0
                elif event.key == pygame.K_UP and dy == 0:
                    dy = -BLOCK_SIZE
                    dx = 0
                elif event.key == pygame.K_DOWN and dy == 0:
                    dy = BLOCK_SIZE
                    dx = 0

        # Contrôle joystick
        direction = read_joystick_direction()
        if direction == 'LEFT' and dx == 0:
            dx = -BLOCK_SIZE
            dy = 0
        elif direction == 'RIGHT' and dx == 0:
            dx = BLOCK_SIZE
            dy = 0
        elif direction == 'UP' and dy == 0:
            dy = -BLOCK_SIZE
            dx = 0
        elif direction == 'DOWN' and dy == 0:
            dy = BLOCK_SIZE
            dx = 0

        x += dx
        y += dy

        # Collision avec les bords
        if x < 0 or x >= 800 or y < 0 or y >= 600:
            game_close = True

        head = [x, y]
        snake.append(head)
        if len(snake) > length:
            del snake[0]

        for segment in snake[:-1]:
            if segment == head:
                game_close = True

        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, [food_x, food_y, BLOCK_SIZE, BLOCK_SIZE])
        for segment in snake:
            pygame.draw.rect(screen, GREEN, [segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE])

        show_score(length - 1)
        pygame.display.update()

        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, 800 - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            food_y = round(random.randrange(0, 600 - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            length += 1
            eat_sound.play()

        clock.tick(10)

    pygame.quit()

game_loop()
