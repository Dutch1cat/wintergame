import pygame, json, sys

# Load resolution setting
def load_resolution():
    try:
        with open("settings.txt", "r") as f:
            res_mode = int(f.readline().strip())
            if res_mode == 1:
                return 960, 540, 1.0
            elif res_mode == 2:
                return 1920, 1080, 2.0
            elif res_mode == 3:
                return 2560, 1440, 2.667
            else:
                return 960, 540, 1.0
    except:
        return 960, 540, 1.0

SCREENW, SCREENH, SCALE = load_resolution()
TILESIZE = int(32 * SCALE)
MAPW, MAPH = (960//32)*16, (540//32)*16  # Map size in base tiles

pygame.init()
screen = pygame.display.set_mode((SCREENW, SCREENH))
pygame.display.set_caption("Ice Drift Editor")
clock = pygame.time.Clock()

# Load and scale tiles
def load_scaled_tile(path):
    img = pygame.image.load(path)
    if SCALE != 1.0:
        new_size = (int(img.get_width() * SCALE), int(img.get_height() * SCALE))
        img = pygame.transform.scale(img, new_size)
    return img

tiles = {
    "ice1": load_scaled_tile("assets/images/roadstuff/ice1.png"),
    "ice2": load_scaled_tile("assets/images/roadstuff/ice2.png"),
    "ice3": load_scaled_tile("assets/images/roadstuff/ice3.png"),
    "snow1": load_scaled_tile("assets/images/roadstuff/snow1.png"),
    "snow2": load_scaled_tile("assets/images/roadstuff/snow2.png"),
    "snow3": load_scaled_tile("assets/images/roadstuff/snow3.png"),
    "cono": load_scaled_tile("assets/images/roadstuff/cono.png"),
    "start": load_scaled_tile("assets/images/roadstuff/start.png"),
    "finish": load_scaled_tile("assets/images/roadstuff/finish.png"),
}

def game_loop():
    global tiles  # Access tiles from outer scope
    
    # These need to be local to game_loop
    current_tile = "ice1"
    grid = [["ice1" for x in range(MAPW)] for y in range(MAPH)]
    cam_x, cam_y = 0, 0
    dragging = False
    last_mouse = (0,0)

    # Load selected map
    try:
        with open("selected.txt","r") as f:
            selected_map = f.readline().strip()
    except:
        selected_map = "track1.json"

    def draw_grid():
        screen.fill((100,100,100))
        for y in range(MAPH):
            for x in range(MAPW):
                draw_x = x*TILESIZE - cam_x
                draw_y = y*TILESIZE - cam_y
                if -TILESIZE < draw_x < SCREENW and -TILESIZE < draw_y < SCREENH:
                    screen.blit(tiles[grid[y][x]], (draw_x, draw_y))
                    pygame.draw.rect(screen, (50,50,50),
                                     (draw_x, draw_y, TILESIZE, TILESIZE), 1)
        
        # Draw current tile indicator
        font_size = int(20 * SCALE)
        font = pygame.font.SysFont("consolas", font_size)
        text = font.render(f"Current: {current_tile}", True, (255,255,255))
        screen.blit(text, (int(10*SCALE), SCREENH - int(30*SCALE)))

    def save_map(filename=None):
        if filename is None:
            filename = "maps/" + selected_map
        with open(filename,"w") as f:
            json.dump(grid,f)
        print(f"Map saved to {filename}!")

    def load_map(filename=None):
        nonlocal grid  # Modify the grid variable from outer scope
        if filename is None:
            filename = "maps/" + selected_map
        try:
            with open(filename,"r") as f:
                loaded = json.load(f)
                # Handle empty or malformed files
                if loaded and len(loaded) > 0 and len(loaded[0]) > 0:
                    grid = loaded
                    print(f"Map loaded from {filename}!")
                else:
                    print("Empty map file, starting fresh")
        except:
            print(f"Failed to load map from {filename}!")

    # Try to load the selected map at start
    load_map()

    running=True
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    running=False
                if event.key==pygame.K_s: save_map()
                if event.key==pygame.K_l: load_map()
                if event.key==pygame.K_1: current_tile="ice1"
                if event.key==pygame.K_2: current_tile="ice2"
                if event.key==pygame.K_3: current_tile="ice3"
                if event.key==pygame.K_4: current_tile="snow1"
                if event.key==pygame.K_5: current_tile="snow2"
                if event.key==pygame.K_6: current_tile="snow3"
                if event.key==pygame.K_c: current_tile="cono"
                if event.key==pygame.K_f: current_tile="finish"
                if event.key==pygame.K_p: current_tile="start"
            if event.type==pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx,my = pygame.mouse.get_pos()
                    gx,gy = (mx+cam_x)//TILESIZE, (my+cam_y)//TILESIZE
                    if 0 <= gx < MAPW and 0 <= gy < MAPH:
                        if current_tile == "start":
                            # Remove previous start
                            for yy in range(MAPH):
                                for xx in range(MAPW):
                                    if grid[yy][xx] == "start":
                                        grid[yy][xx] = "ice1"
                            grid[gy][gx] = "start"
                        else:
                            grid[gy][gx] = current_tile
                elif event.button == 3:
                    dragging = True
                    last_mouse = pygame.mouse.get_pos()
            if event.type==pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    dragging = False
            if event.type==pygame.MOUSEMOTION and dragging:
                mx,my = event.pos
                dx,dy = mx-last_mouse[0], my-last_mouse[1]
                cam_x -= dx
                cam_y -= dy
                last_mouse = (mx,my)

        draw_grid()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    game_loop()
    pygame.quit()
    sys.exit()