#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import random
import pygame, json
from pygame.locals import *

# Constants
TILE_SIZE = 64
GRID_SIZE = 128
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
ZOOM_STEP = 8

# Set up asset directories
ASSET_DIR = 'images'
FONT_PATH = 'tahoma.ttf'
TERRAIN_TYPES = ['dirt', 'grass', 'rocky', 'urban1', 'urban2', 'water1', 'water2', 'water3']

# Initialize Pygame
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()

# Create the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)
pygame.display.set_caption("Isometric Terrain")

# Load images
images = {terrain: pygame.image.load(os.path.join(ASSET_DIR, f'cube_{terrain}.png')).convert_alpha() for terrain in TERRAIN_TYPES}

# print(images)
# pygame.quit()
# sys.exit(1)

# Load font
try:
    font = pygame.font.Font(FONT_PATH, 20)
except FileNotFoundError:
    font = pygame.font.SysFont('tahoma', 20)

grid = {}

# Terrain Block Class
class TerrainBlock:
    def __init__(self, x, y, terrain, height, key):
        self.key = key
        self.x = x
        self.y = y
        self.terrain = terrain
        self.height = height

    def to_dict(self):
        return {
            'key': self.key,
            'x': self.x,
            'y': self.y,
            'terrain': self.terrain,
            'height': self.height
        }

for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        key = f"{x}-{y}"
        grid[key] = TerrainBlock(x, y, random.choice(TERRAIN_TYPES), random.randint(0, 100), key)

# Camera Class
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0

camera = Camera()

def draw_grid():
    window.fill((0, 0, 0))  # Clear the screen

    # Get the mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()
    hovered_block = None

    # Calculate how many blocks we need to draw based on TILE_SIZE and screen dimensions
    extra_tiles = 12
    num_blocks_x = (WINDOW_WIDTH // (TILE_SIZE // 2)) + extra_tiles  # Add extra tiles to ensure full coverage
    num_blocks_y = (WINDOW_HEIGHT // (TILE_SIZE // 4)) + extra_tiles  # Add extra tiles to ensure full coverage

    # Initialize x and y offset to start drawing off-screen
    initial_offset_x = -TILE_SIZE * 2
    initial_offset_y = -TILE_SIZE * 12

    for grid_y in range(-1, num_blocks_y):
        # Calculate starting x and y for each row
        x = initial_offset_x + grid_y * (TILE_SIZE // 2)
        y = initial_offset_y + grid_y * (TILE_SIZE // 4)

        for grid_x in range(-1, num_blocks_x):
            # Check if the current tile position is within the screen bounds before drawing
            if 0 <= x < WINDOW_WIDTH and 0 <= y < WINDOW_HEIGHT:
                key = f"{grid_x + camera.x}-{grid_y + camera.y}"
                block_instance = grid.get(key)

                if block_instance:
                    block = block_instance.to_dict()
                    blit_x = x; blit_y = y

                    # Check if the mouse is hovering over this block
                    if mouse_x in range(x, x + int(TILE_SIZE * 0.8)) and mouse_y in range(y, y + int(TILE_SIZE * 0.3)):
                        hovered_block = block
                        blit_y -= 12

                    window.blit(images[block['terrain']], (blit_x, blit_y))

            # Move to the next tile position diagonally right and down
            x += TILE_SIZE // 2
            y += TILE_SIZE // 4

        # Move the initial x back for the next row and y down to start the next diagonal row
        initial_offset_x -= TILE_SIZE // 2
        initial_offset_y += TILE_SIZE // 4

    # Display camera position
    camera_text = font.render(f"Camera: ({camera.x}, {camera.y})", True, (255, 255, 255))
    window.blit(camera_text, (WINDOW_WIDTH - camera_text.get_width(), camera_text.get_height()))

    # Display the coordinates of the hovered block
    if hovered_block:
        text_surface = font.render(f"Block: ({hovered_block['x']}, {hovered_block['y']})", True, (255, 255, 255))
        window.blit(text_surface, (WINDOW_WIDTH - text_surface.get_width(), 0))

def draw_grid_OLD():
    window.fill((0, 0, 0))  # Clear the screen

    # Define base drawing coordinates at the center of the window
    base_x = WINDOW_WIDTH // 2
    base_y = 30

    # Get the mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate how many blocks we need to draw based on TILE_SIZE and screen dimensions
    num_blocks_x = (WINDOW_WIDTH // (TILE_SIZE // 2)) + 2
    num_blocks_y = (WINDOW_HEIGHT // (TILE_SIZE // 4)) + 2

    hovered_block = None

    for grid_y in range(-1, num_blocks_y):
        for grid_x in range(-1, num_blocks_x):

            # Determine the actual coordinates in the grid array
            actual_x = grid_x + int(camera.x // (TILE_SIZE // 2)) - grid_y + int(camera.y // (TILE_SIZE // 4))
            actual_y = grid_y + int(camera.y // (TILE_SIZE // 4)) + grid_x - int(camera.x // (TILE_SIZE // 2))

            key = f"{actual_x}-{actual_y}"
            block_instance = grid.get(key)

            if block_instance:
                block = block_instance.to_dict()

                # Calculate the screen position to draw the block
                draw_x = base_x + (grid_x - grid_y) * (TILE_SIZE // 2)
                draw_y = base_y + (grid_x + grid_y) * (TILE_SIZE // 4) - block['height']  # Apply height adjustment for 3D effect

                window.blit(images[block['terrain']], (draw_x, draw_y))

                # Check if the mouse is hovering over this block
                if mouse_x in range(draw_x, draw_x + TILE_SIZE) and mouse_y in range(draw_y, draw_y + TILE_SIZE // 2):
                    hovered_block = block
                    hovered_x, hovered_y = draw_x, draw_y  # Save the position to use later

    # Display the coordinates of the hovered block
    if hovered_block:
        text_surface = font.render(f"Block: ({hovered_block['x']}, {hovered_block['y']})", True, (255, 255, 255))
        window.blit(text_surface, (WINDOW_WIDTH - text_surface.get_width(), 0))

    # Display camera position
    camera_text = font.render(f"Camera: ({camera.x}, {camera.y})", True, (255, 255, 255))
    window.blit(camera_text, (WINDOW_WIDTH - camera_text.get_width(), camera_text.get_height()))

# Main loop
running = True
while running:
    clock.tick(30)
    draw_grid()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
                pygame.quit()
                sys.exit()
            elif event.key == K_MINUS:
                TILE_SIZE = max(48, TILE_SIZE - ZOOM_STEP)
            elif event.key == K_EQUALS:
                TILE_SIZE = min(256, TILE_SIZE + ZOOM_STEP)
            elif event.key in [K_UP, K_w]:
                camera.y -= 1
            elif event.key in [K_DOWN, K_s]:
                camera.y += 1
            elif event.key in [K_LEFT, K_a]:
                camera.x -= 1
            elif event.key in [K_RIGHT, K_d]:
                camera.x += 1

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                TILE_SIZE = min(256, TILE_SIZE + ZOOM_STEP)
            elif event.button == 5:  # Scroll down
                TILE_SIZE = max(48, TILE_SIZE - ZOOM_STEP)

pygame.quit()
