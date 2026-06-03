import pygame
import random
import os
pygame.init()

screen = pygame.display.set_mode((600, 500))
pygame.display.set_caption("Sandbox Particles")
clock = pygame.time.Clock()
running = True

CELL_SIZE = 5
GRID_W, GRID_H = 100, 100

VERSION = "1.0.1"
print(f"Version: v{VERSION}")
cwd = os.getcwd()
grid = [[None for y in range(GRID_H)] for x in range(GRID_W)]
assets = os.path.join(cwd, "assets")
materials = {
    "sand": {
        "color": (218, 201, 125),
        "y": 20,
        "img": pygame.image.load(os.path.join(assets, "sand.png")).convert_alpha(),
        "sel": pygame.image.load(os.path.join(assets, "sand_selected.png")).convert_alpha()
    },
    "water": {
        "color": (61, 160, 221),
        "y": 130,
        "img": pygame.image.load(os.path.join(assets, "water.png")).convert_alpha(),
        "sel": pygame.image.load(os.path.join(assets, "water_selected.png")).convert_alpha()
    }
}
selected = "sand"


BG = (0, 0, 0)
MENU = (158,158,158)

def draw_menu():
    pygame.draw.rect(screen, MENU, (500, 0, 100, 500))
    # Reset all
    for name, data in materials.items():
        screen.blit(data["img"], (510, data["y"]))
    screen.blit(materials[selected]["sel"], (510, materials[selected]["y"]))
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if mx < 500 and my < 500:
                grid[mx // CELL_SIZE][my // CELL_SIZE] = selected
            elif mx >= 510 and mx <= 590:
                for name, data in materials.items():
                    if data["y"] <= my <= data["y"] + 80:
                        selected = name

    # Hold to place
    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        if mx < 500 and my < 500:
            grid[mx // CELL_SIZE][my // CELL_SIZE] = selected

    screen.fill(BG)
    lR = random.choice([-1, 1]) # Pick random dir once per particle
    updated = [[False for y in range(GRID_H)] for x in range(GRID_W)]
    for y in range(GRID_H-2, -1, -1):
        lR = random.choice([-1, 1])

        # Sand: right to left
        for x in range(GRID_W-1, -1, -1):
            current = grid[x][y]
            below = grid[x][y+1] if y < GRID_H-1 else None

            if current == "sand":
                # Fall down
                if below is None:
                    grid[x][y+1] = "sand"
                    grid[x][y] = None
                # Swap with water
                elif below == "water":
                    grid[x][y+1] = "sand"
                    grid[x][y] = "water"
                # Diagonal
                elif 0 <= x + lR < GRID_W and grid[x + lR][y + 1] is None:
                    grid[x+lR][y+1] = "sand"
                    grid[x][y] = None

        # Water: left to right 
        for x in range(GRID_W):
            current = grid[x][y]
            below = grid[x][y+1] if y < GRID_H-1 else None

            if current == "water":
                # Fall down
                if below is None:
                    grid[x][y+1] = "water"
                    grid[x][y] = None
                # Diagonal
                elif 0 <= x + lR < GRID_W and grid[x + lR][y + 1] is None:
                    grid[x+lR][y+1] = "water"
                    grid[x][y] = None
                # Spread sideways
                else:
                    if x > 0 and grid[x-1][y] is None:
                        grid[x-1][y] = "water"
                        grid[x][y] = None
                    elif x < GRID_W-1 and grid[x+1][y] is None:
                        grid[x+1][y] = "water"
                        grid[x][y] = None

    # Draw particles (Get color from the dictionary)
    for x in range(GRID_W):
        for y in range(GRID_H):
            particle = grid[x][y]
            if particle!= None:
                color = materials[particle]["color"]
                pygame.draw.rect(screen, color, (CELL_SIZE*x, CELL_SIZE*y, CELL_SIZE, CELL_SIZE))

    draw_menu()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
