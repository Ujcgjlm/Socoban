import pygame
import sys
import os
import time

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480  # Увеличили ширину для отрисовки таймера и шагов
TILE_SIZE = 40
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

LEVELS_DIR = "levels"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sokoban")

font = pygame.font.Font(None, 36)

player_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
player_img.fill(RED)

box_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
box_img.fill(GREEN)

goal_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
goal_img.fill(BLUE)

box_on_goal_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
box_on_goal_img.fill((0, 128, 0))

def load_levels(directory):
    levels = []
    for filename in sorted(os.listdir(directory)):
        with open(os.path.join(directory, filename), 'r') as file:
            lines = file.readlines()
            level = [line for line in lines]
            print(level)
            levels.append(level)
    return levels


def find_goals(level):
    goals = []
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile == '.':
                goals.append((x, y))
    return goals

def draw_level(level, goals):
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if (x, y) in goals:
                screen.blit(goal_img, (x * TILE_SIZE, y * TILE_SIZE))
            if tile == '#':
                pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif tile == '@':
                screen.blit(player_img, (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == '$':
                screen.blit(box_img, (x * TILE_SIZE, y * TILE_SIZE))
            elif tile == '*':
                screen.blit(box_on_goal_img, (x * TILE_SIZE, y * TILE_SIZE))

def move_player(level, goals, dx, dy):
    new_level = [list(row) for row in level]
    player_pos = None
    
    for y, row in enumerate(level):
        for x, char in enumerate(row):
            if char == '@':
                player_pos = (x, y)
                break
        if player_pos:
            break
    
    moved = False
    if player_pos:
        px, py = player_pos
        nx, ny = px + dx, py + dy
        if level[ny][nx] in " .":
            new_level[py][px], new_level[ny][nx] = (' ', '@') if level[py][px] == '@' else ('.', '@')
            moved = True
        elif level[ny][nx] == '$' or level[ny][nx] == '*':
            nnx, nny = nx + dx, ny + dy
            if level[nny][nnx] in " .":
                new_level[py][px] = ' ' if level[py][px] == '@' else '.'
                new_level[ny][nx] = '@'
                new_level[nny][nnx] = '*' if level[nny][nnx] == '.' else '$'
                moved = True
    
    for (gx, gy) in goals:
        if new_level[gy][gx] == ' ':
            new_level[gy][gx] = '.'

    return [''.join(row) for row in new_level], moved

def check_win(level):
    for row in level:
        if '$' in row:
            return False
    return True

def draw_status(start_time, steps):
    elapsed_time = time.time() - start_time
    timer_text = f"Time: {int(elapsed_time)}s"
    steps_text = f"Steps: {steps}"
    timer_surface = font.render(timer_text, True, BLACK)
    steps_surface = font.render(steps_text, True, BLACK)
    
    screen.blit(timer_surface, (SCREEN_WIDTH - 200, 20))
    screen.blit(steps_surface, (SCREEN_WIDTH - 200, 60))

def main():
    levels = load_levels(LEVELS_DIR)
    current_level_index = 0
    original_level = levels[current_level_index]
    level = [row[:] for row in original_level]
    goals = find_goals(level)

    move_history = []
    steps = 0
    
    clock = pygame.time.Clock()
    start_time = time.time()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    move_history.append([row[:] for row in level])
                    if event.key == pygame.K_LEFT:
                        level, moved = move_player(level, goals, -1, 0)
                    if event.key == pygame.K_RIGHT:
                        level, moved = move_player(level, goals, 1, 0)
                    if event.key == pygame.K_UP:
                        level, moved = move_player(level, goals, 0, -1)
                    if event.key == pygame.K_DOWN:
                        level, moved = move_player(level, goals, 0, 1)
                    
                    if moved:
                        steps += 1

                if event.key == pygame.K_u and move_history:
                    level = move_history.pop()
                    if steps > 0:
                        steps -= 1
                        
                if event.key == pygame.K_r:
                    level = [row[:] for row in original_level]
                    move_history.clear()
                    steps = 0
                    start_time = time.time()
                
                if event.key == pygame.K_n:
                    current_level_index = (current_level_index + 1) % len(levels)
                    original_level = levels[current_level_index]
                    level = [row[:] for row in original_level]
                    goals = find_goals(level)
                    move_history.clear()
                    steps = 0
                    start_time = time.time()
                
                if event.key == pygame.K_p:
                    current_level_index = (current_level_index - 1) % len(levels)
                    original_level = levels[current_level_index]
                    level = [row[:] for row in original_level]
                    goals = find_goals(level)
                    move_history.clear()
                    steps = 0
                    start_time = time.time()

        if check_win(level):
            print("Уровень пройден!")
            current_level_index = (current_level_index + 1) % len(levels)
            original_level = levels[current_level_index]
            level = [row[:] for row in original_level]
            goals = find_goals(level)
            move_history.clear()
            steps = 0
            start_time = time.time()

        screen.fill(WHITE)
        draw_level(level, goals)
        draw_status(start_time, steps)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    os.makedirs(LEVELS_DIR, exist_ok=True)
    main()