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
pygame.display.set_caption("Dodge the Fireballs - Replay Mode")
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

# Ghost player variables
ghost_visible = False
ghost_column = player_column
ghost_position_index = 0

# Hardcoded predicted positions
predicted_positions = [3, 1, 3, 2, 4, 4, 3, 1, 1, 1, 1, 2, 4, 4, 3, 2, 3, 2, 1, 2, 3, 2, 3, 4, 3]

# Variables for logic
prev_player_column = player_column
move_cooldown = 0
running = True

# Game replay variables
replay_data = []
current_replay_frame = 0
replay_mode = True  # Set to True to use replay data instead of random generation

# Load replay data
def load_replay_data():
    try:
        data = []
        with open("fireballs-frames.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 5:  # Ensure row has all needed data
                    frame = int(row[0])
                    player_col = int(row[1])
                    dodge = int(row[2])
                    fireball_cols = [int(c) for c in row[3].split("|") if c]
                    fireball_ys = [float(y) for y in row[4].split("|") if y]
                    data.append({
                        'frame': frame,
                        'player_column': player_col,
                        'dodge_flag': dodge,
                        'fireball_cols': fireball_cols,
                        'fireball_ys': fireball_ys
                    })
        print(f"Loaded {len(data)} frames of replay data.")
        return data
    except FileNotFoundError:
        print("Warning: fireballs-frames.csv not found. Using random generation mode.")
        return []

# Load replay data if available
replay_data = load_replay_data()
if not replay_data:
    replay_mode = False

while running:
    clock.tick(30)
    screen.fill((30, 30, 30))
    frame_count += 1
    move_cooldown += 1
    dodge_flag = 0

    # Handle fireballs based on mode
    if replay_mode and current_replay_frame < len(replay_data):
        # Get the current frame data
        frame_data = replay_data[current_replay_frame]
        
        # Update fireballs based on replay data
        fireballs = []
        for i in range(len(frame_data['fireball_cols'])):
            col = frame_data['fireball_cols'][i]
            y_pos = frame_data['fireball_ys'][i]
            fireballs.append([col, y_pos])
            
        # Check if we should show ghost based on dodge flag in replay
        if frame_data['dodge_flag'] == 1 and ghost_position_index < len(predicted_positions):
            ghost_column = predicted_positions[ghost_position_index]
            ghost_position_index += 1
            ghost_visible = True
            
        current_replay_frame += 1
    else:
        # Original random generation logic
        if frame_count % spawn_delay == 0:
            spawn_range = 2
            col = random.randint(max(0, player_column - spawn_range), min(columns - 1, player_column + spawn_range))
            fireballs.append([col, 0])
            
        # Move fireballs
        for f in fireballs:
            f[1] += fireball_speed
        fireballs = [f for f in fireballs if f[1] < HEIGHT]

    # Player movement (allowed in both modes)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_column > 0 and move_cooldown > 10:
        player_column -= 1
        move_cooldown = 0
        dodge_flag = 1
    if keys[pygame.K_RIGHT] and player_column < columns - 1 and move_cooldown > 10:
        player_column += 1
        move_cooldown = 0
        dodge_flag = 1
        
    # In replay mode, optionally set player position to match recorded position
    if replay_mode and current_replay_frame < len(replay_data):
        if keys[pygame.K_SPACE]:  # Hold space to follow recorded path
            player_column = replay_data[current_replay_frame]['player_column']

    # Update ghost position when dodge happens (only in non-replay mode)
    if not replay_mode and dodge_flag == 1:
        # Use the next predicted position from our array
        if ghost_position_index < len(predicted_positions):
            ghost_column = predicted_positions[ghost_position_index]
            ghost_position_index += 1
            ghost_visible = True

    # Draw player
    player_x = slot_positions[player_column]
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    pygame.draw.rect(screen, (0, 255, 0), player_rect)

    # Draw ghost player (white) if visible
    if ghost_visible:
        ghost_x = slot_positions[ghost_column]
        ghost_rect = pygame.Rect(ghost_x, player_y, player_size, player_size)
        pygame.draw.rect(screen, (255, 255, 255), ghost_rect, 2)  # Outline style
        
        # Reset ghost visibility after drawing for one frame
        ghost_visible = False

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

    # Handle window close
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()