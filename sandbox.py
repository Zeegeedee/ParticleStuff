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
VERSION = "1.1.1"
print(f"Version: v{VERSION}")
cwd = os.path.dirname(os.path.abspath(__file__))
grid = [[None for y in range(GRID_H)] for x in range(GRID_W)]
assets = os.path.join(cwd, "assets")

materials = {
    "sand": {
        "color1": (218, 201, 125),
        "color2": (255, 228, 181),
        "color3": (245, 222, 179),
        "y": 20,
        "img": pygame.image.load(os.path.join(assets, "sand.png")).convert_alpha(),
        "sel": pygame.image.load(os.path.join(assets, "sand_selected.png")).convert_alpha()
    },
    "water": {
        "color1": (61, 160, 221),
        "color2": (30, 144, 255),
        "color3": (0, 191, 255),
        "y": 130,
        "img": pygame.image.load(os.path.join(assets, "water.png")).convert_alpha(),
        "sel": pygame.image.load(os.path.join(assets, "water_selected.png")).convert_alpha()
    },
    "soil": {
        "color1": (139, 69, 19),
        "color2": (160, 82, 45),
        "color3": (101, 67, 33),
        "y": 240,
        "img": pygame.image.load(os.path.join(assets, "soil.png")).convert_alpha(),
        "sel": pygame.image.load(os.path.join(assets, "soil_selected.png")).convert_alpha()
    },
    "mud": {
        "color1": (90, 78, 70),
        "color2": (133, 119, 107),
        "color3": (175, 161, 149),
        "y": 350,
        "img": pygame.image.load(os.path.join(assets, "mud.png")).convert_alpha(),
        "sel": pygame.image.load(os.path.join(assets, "mud_selected.png")).convert_alpha()
    }
}

selected = "sand"
BG = (0, 0, 0)
MENU = (158, 158, 158)

def draw_menu():
    pygame.draw.rect(screen, MENU, (500, 0, 100, 500))
    for name, data in materials.items():
        if data["img"] is not None:
            screen.blit(data["img"], (510, data["y"]))
        if name == selected and data["sel"] is not None:
            screen.blit(data["sel"], (510, data["y"]))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if mx < 500 and my < 500:
                gx, gy = mx // CELL_SIZE, my // CELL_SIZE
                if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                    randCol = random.choice([1,2,3])
                    color = materials[selected][f"color{randCol}"]
                    grid[gx][gy] = (selected, color)
            elif mx >= 510 and mx <= 590:
                for name, data in materials.items():
                    if data["y"] <= my <= data["y"] + 80:
                        selected = name

    # Hold to place
    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        if mx < 500 and my < 500:
            gx, gy = mx // CELL_SIZE, my // CELL_SIZE
            if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                randCol = random.choice([1,2,3])
                color = materials[selected][f"color{randCol}"]
                grid[gx][gy] = (selected, color)

    screen.fill(BG)

    # Track particles that already moved this frame so they don't double-update
    updated = set()

    for y in range(GRID_H-2, -1, -1):
        lR = random.choice([-1, 1])
        
        # Create a dynamic list of X coordinates to break up the static checkerboard layout
        water_x_indices = list(range(GRID_W))
        if random.choice([True, False]):
            water_x_indices.reverse()

        # Sand: right to left 
        sand_x_indices = list(range(GRID_W-1, -1, -1))
        for x in sand_x_indices:
            current = grid[x][y]
            if current is not None and (x, y) not in updated:
                ptype, col = current
                below = grid[x][y+1] if y < GRID_H-1 else None
                if ptype == "sand":
                    # Fall down
                    if below is None:
                        grid[x][y+1] = current
                        grid[x][y] = None
                        updated.add((x, y+1))
                    # Go under water
                    elif below is not None and below[0] == "water":
                        grid[x][y+1] = current
                        grid[x][y] = below
                        updated.add((x, y+1))
                        updated.add((x, y))
                    # Diagonal
                    elif 0 <= x + lR < GRID_W and grid[x + lR][y + 1] is None:
                        grid[x+lR][y+1] = current
                        grid[x][y] = None
                        updated.add((x+lR, y+1))
                    elif 0 <= x + lR < GRID_W:
                        diag_below = grid[x+lR][y+1]
                        if diag_below is not None and diag_below[0] == "water":
                            grid[x+lR][y+1] = current
                            grid[x+lR][y] = diag_below
                            updated.add((x+lR, y+1))
                            updated.add((x, y))

        # Water: Randomized spread direction
        for x in water_x_indices:
            current = grid[x][y]
            if current is not None and (x, y) not in updated:
                ptype, col = current
                below = grid[x][y+1] if y < GRID_H-1 else None
                if ptype == "water":
                    # Fall down
                    if below is None:
                        grid[x][y+1] = current
                        grid[x][y] = None
                        updated.add((x, y+1))
                        continue
                    
                    # Mud conversion physics
                    rX = random.choice([-1, 0, 1])
                    rY = random.choice([-1, 0, 1])
                    if 0 <= x+rX < GRID_W and 0 <= y+rY < GRID_H:
                        neighbor = grid[x+rX][y+rY]
                        # Check if neighbor exists and is soil
                        if neighbor is not None and neighbor[0] == "soil":
                            # Turn neighbor into mud
                            randCol = random.choice([1, 2, 3])
                            mud_color = materials["mud"][f"color{randCol}"]
                            grid[x+rX][y+rY] = ("mud", mud_color)
                    
                    # Spread sideways
                    spread = False
                    # Randomize whether water chooses left or right side first each step
                    directionsX = [-1, 1]
                    if random.choice([True, False]):
                        directionsX.reverse()
                        
                    for dx in directionsX:
                        nx = x + dx
                        if 0 <= nx < GRID_W and grid[nx][y] is None:
                            grid[nx][y] = current
                            grid[x][y] = None
                            updated.add((nx, y))
                            spread = True
                            break
                            
                    # If it can't spread, try diagonal
                    if not spread:
                        for dx in directionsX:
                            nx = x + dx
                            if 0 <= nx < GRID_W and y+1 < GRID_H and grid[nx][y+1] is None:
                                grid[nx][y+1] = current
                                grid[x][y] = None
                                updated.add((nx, y+1))
                                break
            
        # Soil physics (Other than mud, this is quite a joke lol its just brown sand)
        soil_x_indices = list(range(GRID_W-1, -1, -1))
        for x in soil_x_indices:
            current = grid[x][y]
            if current is not None and (x, y) not in updated:
                ptype, col = current
                below = grid[x][y+1] if y < GRID_H-1 else None
                if ptype == "soil":
                    # Fall down
                    if below is None:
                        grid[x][y+1] = current
                        grid[x][y] = None
                        updated.add((x, y+1))
                    
                    # Diagonal
                    elif 0 <= x + lR < GRID_W and grid[x + lR][y + 1] is None:
                        grid[x+lR][y+1] = current
                        grid[x][y] = None
                        updated.add((x+lR, y+1))            
            
        # Mud physics (Alright this is a COMPLETE joke this is just sand again but slow)
        mud_x_indices = list(range(GRID_W-1, -1, -1))
        for x in mud_x_indices:
            current = grid[x][y]
            if current is not None and (x, y) not in updated:
                ptype, col = current
                below = grid[x][y+1] if y < GRID_H-1 else None
                
                if ptype == "mud":
                    
                    randTick = random.randint(1,17)
                    # Fall down
                    if below is None:
                        grid[x][y+1] = current
                        grid[x][y] = None
                        updated.add((x, y+1))
                    
                    # Diagonal
                    elif 0 <= x + lR < GRID_W and grid[x + lR][y + 1] is None and randTick == 7:
                         grid[x+lR][y+1] = current
                         grid[x][y] = None
                         updated.add((x+lR, y+1))         
    
    # Draw particles (uses stored color)
    for x in range(GRID_W):
        for y in range(GRID_H):
            particle = grid[x][y]
            if particle!= None:
                ptype, color = particle
                pygame.draw.rect(screen, color, (CELL_SIZE*x, CELL_SIZE*y, CELL_SIZE, CELL_SIZE))

    draw_menu()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
