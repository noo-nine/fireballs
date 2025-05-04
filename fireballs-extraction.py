import pygame
import random
import csv
import time
import math
import pickle

# === Load trained model (optional, for ghost prediction) ===
# model = pickle.load(open("your_model.pkl", "rb"))

# Initialize Pygame
pygame.init()

# Set up game window and clock
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge the Fireballs - Logging Mode")
clock = pygame.time.Clock()

# Player setup
player_size = 40
player_column = 2  # Initial position of the player
player_y = HEIGHT - player_size - 10
player_speed = 2
columns = 6
gap = 60  # Increased gap between columns
column_width = (WIDTH - (columns + 1) * gap) // columns
slot_positions = [gap + i * (column_width + gap) for i in range(columns)]

# Fireball setup
fireballs = []
fireball_size = 40
fireball_speed = 4
spawn_delay = 25
frame_count = 0

# Data collection
record_file = open("fireballs-features.csv", "w", newline='')
frame_file = open("fireballs-frames.csv", "w", newline='')

record_writer = csv.writer(record_file)
frame_writer = csv.writer(frame_file)

# Headers for model training file
record_writer.writerow([
    'previous_position', 'player_position', 'density_col_0', 'density_col_1',
    'density_col_2', 'density_col_3', 'density_col_4', 'density_col_5',
    'ETA_nearest', 'offset_from_nearest', 'safe_zone_width',
    'edge_awareness', 'final_position'
])

# Headers for all-frame file
frame_writer.writerow([
    'frame', 'player_column', 'dodge_flag', 'fireball_cols', 'fireball_ys'
])

# Variables for logic
prev_player_column = player_column
move_cooldown = 0
running = True

while running:
    clock.tick(30)
    screen.fill((30, 30, 30))
    frame_count += 1
    move_cooldown += 1
    dodge_flag = 0

    # Spawn fireballs
    if frame_count % spawn_delay == 0:
        spawn_range = 2
        col = random.randint(max(0, player_column - spawn_range), min(columns - 1, player_column + spawn_range))
        fireballs.append([col, 0])

    # Move fireballs
    for f in fireballs:
        f[1] += fireball_speed
    fireballs = [f for f in fireballs if f[1] < HEIGHT]

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_column > 0 and move_cooldown > 10:
        player_column -= 1
        move_cooldown = 0
        dodge_flag = 1
    if keys[pygame.K_RIGHT] and player_column < columns - 1 and move_cooldown > 10:
        player_column += 1
        move_cooldown = 0
        dodge_flag = 1

    # Draw player
    player_x = slot_positions[player_column]
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    pygame.draw.rect(screen, (0, 255, 0), player_rect)

    # Draw fireballs and track nearest
    nearest_distance = float("inf")
    nearest_x_offset = 0
    density = [0] * columns
    fireball_cols = []
    fireball_ys = []

    for f in fireballs:
        fb_x = slot_positions[f[0]]
        fb_y = f[1]
        fireball_rect = pygame.Rect(fb_x, fb_y, fireball_size, fireball_size)
        pygame.draw.rect(screen, (255, 0, 0), fireball_rect)

        dist = math.sqrt((fb_x - player_x) ** 2 + (fb_y - player_y) ** 2)
        if dist < nearest_distance:
            nearest_distance = dist
            nearest_x_offset = fb_y - player_y

        density[f[0]] += 1
        fireball_cols.append(f[0])
        fireball_ys.append(f[1])

        # Collision check
        if player_rect.colliderect(fireball_rect):
            print("💥 Game Over!")
            running = False

    # Safe zone and edge awareness
    safe_zone_width = density.count(0)
    edge_awareness = min(player_column, columns - 1 - player_column)

    # Record frame data
    frame_writer.writerow([
        frame_count,
        player_column,
        dodge_flag,
        "|".join(map(str, fireball_cols)),
        "|".join(map(str, fireball_ys))
    ])

    # Record training data only on movement (dodge)
    if dodge_flag:
        record_writer.writerow([
            prev_player_column,
            player_column,
            *density,
            round(nearest_distance, 2),
            round(nearest_x_offset, 2),
            safe_zone_width,
            edge_awareness,
            player_column
        ])
        prev_player_column = player_column

    # Handle window close
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

# Close files
record_file.close()
frame_file.close()
pygame.quit()
