import pygame
import random
import csv
import time
import math

# Initialize Pygame
pygame.init()

# Set up game window and clock
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge the Fireballs")
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
fireball_speed = 4  # Speed of fireballs
spawn_delay = 25  # Spawn delay for fireballs
frame_count = 0

# Data collection setup (CSV file)
data_file = open("dodge_features.csv", "w", newline='')
csv_writer = csv.writer(data_file)
csv_writer.writerow([
    "previous_position", 
    "player_position", 
    "density_col_0", "density_col_1", "density_col_2", "density_col_3", "density_col_4", "density_col_5", 
    "ETA_nearest", 
    "offset_from_nearest", 
    "safe_zone_width", 
    "edge_awareness", 
    "final_position"
])

# Variables for gameplay
prev_player_column = player_column
move_cooldown = 0

# Game loop
running = True
while running:
    clock.tick(30)  # Control the frame rate
    screen.fill((30, 30, 30))  # Clear the screen with dark background
    frame_count += 1
    move_cooldown += 1

    # Spawn fireballs around the player (biased spawn near player)
    if frame_count % spawn_delay == 0:
        spawn_range = 2  # +-2 columns around the player
        col = random.randint(max(0, player_column - spawn_range), min(columns - 1, player_column + spawn_range))
        fireballs.append([col, 0])

    # Move fireballs down
    for f in fireballs:
        f[1] += fireball_speed
    fireballs = [f for f in fireballs if f[1] < HEIGHT]  # Remove fireballs that have gone off-screen

    # Handle player movement with keyboard
    keys = pygame.key.get_pressed()
    moved = False
    if keys[pygame.K_LEFT] and player_column > 0 and move_cooldown > 10:
        player_column -= 1
        moved = True
        move_cooldown = 0  # Reset cooldown after move
    if keys[pygame.K_RIGHT] and player_column < columns - 1 and move_cooldown > 10:
        player_column += 1
        moved = True
        move_cooldown = 0  # Reset cooldown after move

    # Draw player
    player_x = slot_positions[player_column]
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    pygame.draw.rect(screen, (0, 255, 0), player_rect)

    # Fireball collision detection and drawing
    fireball_data = []
    nearest_distance = float("inf")
    is_above = False

    for f in fireballs:
        fb_x = slot_positions[f[0]]
        fb_y = f[1]
        fireball_rect = pygame.Rect(fb_x, fb_y, fireball_size, fireball_size)
        pygame.draw.rect(screen, (255, 0, 0), fireball_rect)

        # Collision detection with player
        if player_rect.colliderect(fireball_rect):
            print("💥 Game Over!")
            running = False

        # Track nearest fireball distance
        dist = math.sqrt((fb_x - player_x) ** 2 + (fb_y - player_y) ** 2)
        if dist < nearest_distance:
            nearest_distance = dist

    # Fireball density and safe zone calculations
    density = [0] * columns
    for f in fireballs:
        density[f[0]] += 1

    # Calculate the safe zone width and other metrics
    safe_zone_width = columns - sum(density)
    edge_awareness = min(player_column, columns - player_column - 1)

    # Collect data when dodge happens (when player moves)
    if moved:
        final_position = player_column
        csv_writer.writerow([
            prev_player_column, 
            player_column, 
            *density, 
            round(nearest_distance, 2), 
            round(nearest_distance - player_y, 2), 
            safe_zone_width, 
            edge_awareness, 
            final_position
        ])
        prev_player_column = player_column

    # Handle exit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

# Close the CSV file and Pygame when the game ends
data_file.close()
pygame.quit()