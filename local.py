import pygame, json, sys, math
from local_skater import LocalSkater
import os

def resource_path(relative_path):
    # Funziona sia in sviluppo che in build
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

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

WIDTH, HEIGHT, SCALE = load_resolution()
TILESIZE = int(32 * SCALE)
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ice Drift - Local Multiplayer")
clock = pygame.time.Clock()

# Load and scale tiles
def load_scaled_tile(path):
    img = pygame.image.load(resource_path(path)).convert_alpha()
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

# HUD fonts
font_size = int(18 * SCALE)
font = pygame.font.SysFont("consolas", font_size)

def game_loop():
    # Load map
    try:
        with open("selected.txt", "r") as f:
            selected_map = f.readline().strip()
    except:
        selected_map = "track1.json"
    
    with open("maps/" + selected_map) as f:
        grid = json.load(f)

    MAPW, MAPH = len(grid[0]), len(grid)

    # Find start position
    start_pos = None
    for y in range(MAPH):
        for x in range(MAPW):
            if grid[y][x] == "start":
                start_pos = (x*TILESIZE + TILESIZE//2, y*TILESIZE + TILESIZE//2)
                break
        if start_pos:
            break

    if not start_pos:
        start_pos = (100, 100)

    # Create two players with different controls
    # Player 1: WASD
    player1 = LocalSkater(start_pos, SCALE, control_scheme='wasd')
    # Player 2: Arrow keys, spawn slightly offset
    player2_spawn = (start_pos[0] + int(50*SCALE), start_pos[1])
    player2 = LocalSkater(player2_spawn, SCALE, control_scheme='arrows')

    # Split screen dimensions
    split_width = WIDTH // 2
    split_height = HEIGHT

    def draw_map(surface, cam_x, cam_y, view_width, view_height):
        start_x = max(0, cam_x//TILESIZE)
        start_y = max(0, cam_y//TILESIZE)
        end_x = min(MAPW, (cam_x+view_width)//TILESIZE+2)
        end_y = min(MAPH, (cam_y+view_height)//TILESIZE+2)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = grid[y][x]
                draw_x = x*TILESIZE - cam_x
                draw_y = y*TILESIZE - cam_y
                surface.blit(tiles[tile], (draw_x, draw_y))

    def apply_surface_effects(player):
        gx, gy = int(player.pos.x//TILESIZE), int(player.pos.y//TILESIZE)
        if 0 <= gy < MAPH and 0 <= gx < MAPW:
            tile = grid[gy][gx]
            if "snow" in tile:
                player.vx *= 0.95
                player.vy *= 0.95
            elif "ice" in tile:
                player.vx *= 1.02
                player.vy *= 1.02
            elif "cono" in tile:
                cone_rect = pygame.Rect(gx*TILESIZE, gy*TILESIZE, TILESIZE, TILESIZE)
                if player.rect.colliderect(cone_rect):
                    player.vx *= -0.4
                    player.vy *= -0.4
                    if player.rect.centerx < cone_rect.centerx:
                        player.pos.x = cone_rect.left - player.rect.width//2
                    else:
                        player.pos.x = cone_rect.right + player.rect.width//2
                    if player.rect.centery < cone_rect.centery:
                        player.pos.y = cone_rect.top - player.rect.height//2
                    else:
                        player.pos.y = cone_rect.bottom + player.rect.height//2
                    player.rect.center = player.pos
                    player.crashes += 1
            elif "finish" in tile and not player.finished:
                return True
        return False

    def draw_hud(surface, player, x_offset, y_offset, player_num, time_sec):
        t_ms = int(time_sec*1000)
        
        # Player label
        label = font.render(f"P{player_num}", True, (255, 255, 100))
        surface.blit(label, (x_offset + int(10*SCALE), y_offset + int(10*SCALE)))
        
        # Time
        if not player.finished:
            text = font.render(f"Time: {t_ms//1000}.{t_ms%1000:03d}s", True, (230,230,255))
        else:
            final_ms = int(player.finish_time*1000)
            text = font.render(f"Time: {final_ms//1000}.{final_ms%1000:03d}s", True, (100,255,100))
        surface.blit(text, (x_offset + int(10*SCALE), y_offset + int(35*SCALE)))
        
        # Speed
        speed = math.hypot(player.vx, player.vy)
        v_text = font.render(f"Vel: {speed:05.2f}", True, (230,230,255))
        surface.blit(v_text, (x_offset + int(10*SCALE), y_offset + int(60*SCALE)))
        
        # Crashes
        c_text = font.render(f"Crash: {player.crashes}", True, (230,230,255))
        surface.blit(c_text, (x_offset + int(10*SCALE), y_offset + int(85*SCALE)))
        
        # Finished indicator
        if player.finished:
            finished_text = font.render("FINISHED!", True, (100,255,100))
            surface.blit(finished_text, (x_offset + int(10*SCALE), y_offset + int(110*SCALE)))

    def show_stats(p1_time, p1_crashes, p2_time, p2_crashes):
        screen.fill((0,0,0))
        big_font_size = int(40 * SCALE)
        small_font_size = int(30 * SCALE)
        big_font = pygame.font.SysFont("consolas", big_font_size)
        small_font = pygame.font.SysFont("consolas", small_font_size)
        
        # Title
        text1 = big_font.render("Race finished!", True, (255,255,255))
        screen.blit(text1, (WIDTH//2 - text1.get_width()//2, int(50*SCALE)))
        
        # Determine winner
        if p1_time < p2_time:
            winner_text = big_font.render("Player 1 WINS!", True, (255,215,0))
        elif p2_time < p1_time:
            winner_text = big_font.render("Player 2 WINS!", True, (255,215,0))
        else:
            winner_text = big_font.render("TIE!", True, (255,215,0))
        screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, int(120*SCALE)))
        
        # Player 1 stats
        p1_label = small_font.render("Player 1 (WASD)", True, (100,200,255))
        p1_time_text = small_font.render(f"Time: {p1_time:.2f}s", True, (200,200,200))
        p1_crash_text = small_font.render(f"Crash: {p1_crashes}", True, (200,200,200))
        
        y_pos = int(200*SCALE)
        screen.blit(p1_label, (WIDTH//4 - p1_label.get_width()//2, y_pos))
        screen.blit(p1_time_text, (WIDTH//4 - p1_time_text.get_width()//2, y_pos + int(40*SCALE)))
        screen.blit(p1_crash_text, (WIDTH//4 - p1_crash_text.get_width()//2, y_pos + int(80*SCALE)))
        
        # Player 2 stats
        p2_label = small_font.render("Player 2 (Arrows)", True, (255,100,100))
        p2_time_text = small_font.render(f"Time: {p2_time:.2f}s", True, (200,200,200))
        p2_crash_text = small_font.render(f"Crash: {p2_crashes}", True, (200,200,200))
        
        screen.blit(p2_label, (3*WIDTH//4 - p2_label.get_width()//2, y_pos))
        screen.blit(p2_time_text, (3*WIDTH//4 - p2_time_text.get_width()//2, y_pos + int(40*SCALE)))
        screen.blit(p2_crash_text, (3*WIDTH//4 - p2_crash_text.get_width()//2, y_pos + int(80*SCALE)))
        
        pygame.display.flip()
        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT or e.type == pygame.KEYDOWN:
                    waiting = False

    # Create surfaces for split screen
    left_surface = pygame.Surface((split_width, split_height))
    right_surface = pygame.Surface((split_width, split_height))

    # Loop
    running = True
    race_time = 0.0
    
    while running:
        dt = clock.tick(FPS)/1000
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        
        # Update players
        player1.update(keys, dt)
        player2.update(keys, dt)
        
        # Apply surface effects
        if apply_surface_effects(player1) and not player1.finished:
            player1.finished = True
            player1.finish_time = race_time
        
        if apply_surface_effects(player2) and not player2.finished:
            player2.finished = True
            player2.finish_time = race_time

        race_time += dt

        # Check if both finished
        if player1.finished and player2.finished:
            show_stats(player1.finish_time, player1.crashes, 
                      player2.finish_time, player2.crashes)
            running = False
            continue

        # Calculate cameras
        cam1_x = int(player1.pos.x - split_width//2)
        cam1_y = int(player1.pos.y - split_height//2)
        cam1_x = max(0, min(cam1_x, MAPW*TILESIZE - split_width))
        cam1_y = max(0, min(cam1_y, MAPH*TILESIZE - split_height))

        cam2_x = int(player2.pos.x - split_width//2)
        cam2_y = int(player2.pos.y - split_height//2)
        cam2_x = max(0, min(cam2_x, MAPW*TILESIZE - split_width))
        cam2_y = max(0, min(cam2_y, MAPH*TILESIZE - split_height))

        # Draw left screen (Player 1)
        left_surface.fill((30,40,55))
        draw_map(left_surface, cam1_x, cam1_y, split_width, split_height)
        player1.draw(left_surface, cam1_x, cam1_y)
        player2.draw(left_surface, cam1_x, cam1_y)  # Draw other player too
        draw_hud(left_surface, player1, 0, 0, 1, race_time)

        # Draw right screen (Player 2)
        right_surface.fill((30,40,55))
        draw_map(right_surface, cam2_x, cam2_y, split_width, split_height)
        player1.draw(right_surface, cam2_x, cam2_y)  # Draw other player too
        player2.draw(right_surface, cam2_x, cam2_y)
        draw_hud(right_surface, player2, 0, 0, 2, race_time)

        # Combine to main screen
        screen.blit(left_surface, (0, 0))
        screen.blit(right_surface, (split_width, 0))
        
        # Draw divider line
        pygame.draw.line(screen, (100, 100, 100), (split_width, 0), (split_width, HEIGHT), 3)

        pygame.display.flip()

if __name__ == "__main__":
    game_loop()
    pygame.quit()
    sys.exit()