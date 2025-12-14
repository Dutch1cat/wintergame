import pygame, json, sys, math
from skater import Skater
from client import GameClient

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
pygame.display.set_caption("Ice Drift - Multiplayer")
clock = pygame.time.Clock()

# Load and scale tiles
def load_scaled_tile(path):
    img = pygame.image.load(path).convert_alpha()
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
font_size = int(22 * SCALE)
font = pygame.font.SysFont("consolas", font_size)

def game_loop(multiplayer=False, server_ip='rke2.fsmn.xyz:5555'):
    # Initialize network client if multiplayer
    client = None
    if multiplayer:
        client = GameClient(server_ip)
    
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

    # Player
    skater = Skater(start_pos, SCALE)
    
    # Connect to server if multiplayer
    if multiplayer:
        print("Connecting to server...")
        if not client.connect(skater.pos.x, skater.pos.y, skater.angle):
            print("Failed to connect to server!")
            return
        print("Connected successfully!")
    
    # Other players (multiplayer only)
    other_skaters = {}  # {player_id: Skater}

    def draw_map(cam_x, cam_y):
        start_x = max(0, cam_x//TILESIZE)
        start_y = max(0, cam_y//TILESIZE)
        end_x = min(MAPW, (cam_x+WIDTH)//TILESIZE+2)
        end_y = min(MAPH, (cam_y+HEIGHT)//TILESIZE+2)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = grid[y][x]
                draw_x = x*TILESIZE - cam_x
                draw_y = y*TILESIZE - cam_y
                screen.blit(tiles[tile], (draw_x, draw_y))

    def apply_surface_effects():
        gx, gy = int(skater.pos.x//TILESIZE), int(skater.pos.y//TILESIZE)
        if 0 <= gy < MAPH and 0 <= gx < MAPW:
            tile = grid[gy][gx]
            if "snow" in tile:
                skater.vx *= 0.95
                skater.vy *= 0.95
            elif "ice" in tile:
                skater.vx *= 1.02
                skater.vy *= 1.02
            elif "cono" in tile:
                cone_rect = pygame.Rect(gx*TILESIZE, gy*TILESIZE, TILESIZE, TILESIZE)
                if skater.rect.colliderect(cone_rect):
                    skater.vx *= -0.4
                    skater.vy *= -0.4
                    if skater.rect.centerx < cone_rect.centerx:
                        skater.pos.x = cone_rect.left - skater.rect.width//2
                    else:
                        skater.pos.x = cone_rect.right + skater.rect.width//2
                    if skater.rect.centery < cone_rect.centery:
                        skater.pos.y = cone_rect.top - skater.rect.height//2
                    else:
                        skater.pos.y = cone_rect.bottom + skater.rect.height//2
                    skater.rect.center = skater.pos
                    skater.crashes += 1
            elif "finish" in tile:
                return True
        return False

    def draw_hud(time_sec):
        t_ms = int(time_sec*1000)
        text = font.render(f"Tempo: {t_ms//1000}.{t_ms%1000:03d}s", True, (230,230,255))
        screen.blit(text, (int(20*SCALE), int(20*SCALE)))
        speed = math.hypot(skater.vx, skater.vy)
        v_text = font.render(f"Vel: {speed:05.2f}", True, (230,230,255))
        screen.blit(v_text, (int(20*SCALE), int(50*SCALE)))
        c_text = font.render(f"Crash: {skater.crashes}", True, (230,230,255))
        screen.blit(c_text, (int(20*SCALE), int(80*SCALE)))
        
        if multiplayer and client:
            player_count = len(client.get_other_players()) + 1
            p_text = font.render(f"Players: {player_count}", True, (230,230,255))
            screen.blit(p_text, (int(20*SCALE), int(110*SCALE)))

    def show_stats(final_time, crashes):
        screen.fill((0,0,0))
        big_font_size = int(40 * SCALE)
        big_font = pygame.font.SysFont("consolas", big_font_size)
        text1 = big_font.render("Gara finita!", True, (255,255,255))
        text2 = big_font.render(f"Tempo: {final_time:.2f} s", True, (255,255,255))
        text3 = big_font.render(f"Crash: {crashes}", True, (255,255,255))
        screen.blit(text1, (WIDTH//2 - text1.get_width()//2, HEIGHT//2 - int(60*SCALE)))
        screen.blit(text2, (WIDTH//2 - text2.get_width()//2, HEIGHT//2))
        screen.blit(text3, (WIDTH//2 - text3.get_width()//2, HEIGHT//2 + int(60*SCALE)))
        pygame.display.flip()
        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT or e.type == pygame.KEYDOWN:
                    waiting = False

    # Loop
    running=True
    race_time=0.0
    finished=False
    update_counter = 0
    
    while running and not finished:
        dt = clock.tick(FPS)/1000
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                running=False
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_ESCAPE:
                    running=False

        keys = pygame.key.get_pressed()
        skater.update(keys, dt)
        if apply_surface_effects():
            finished=True

        # Send updates to server (every 2 frames for efficiency)
        if multiplayer and client:
            update_counter += 1
            if update_counter >= 2:
                client.send_update(skater.pos.x, skater.pos.y, skater.angle, 
                                 skater.vx, skater.vy, skater.crashes)
                update_counter = 0
            
            # Update other players
            other_players_data = client.get_other_players()
            
            # Remove players who disconnected
            for pid in list(other_skaters.keys()):
                if pid not in other_players_data:
                    del other_skaters[pid]
            
            # Update/create other players
            for pid, data in other_players_data.items():
                if pid not in other_skaters:
                    other_skaters[pid] = Skater((data['x'], data['y']), SCALE)
                else:
                    # Smooth interpolation for other players
                    other_skaters[pid].pos.x = data['x']
                    other_skaters[pid].pos.y = data['y']
                    other_skaters[pid].angle = data['angle']
                    other_skaters[pid].vx = data.get('vx', 0)
                    other_skaters[pid].vy = data.get('vy', 0)
                    other_skaters[pid].crashes = data.get('crashes', 0)
                    other_skaters[pid].rect.center = other_skaters[pid].pos

        race_time += dt

        cam_x = int(skater.pos.x - WIDTH//2)
        cam_y = int(skater.pos.y - HEIGHT//2)
        cam_x = max(0, min(cam_x, MAPW*TILESIZE - WIDTH))
        cam_y = max(0, min(cam_y, MAPH*TILESIZE - HEIGHT))

        screen.fill((30,40,55))
        draw_map(cam_x, cam_y)
        
        # Draw other players first (behind local player)
        if multiplayer:
            for other in other_skaters.values():
                other.draw(screen, cam_x, cam_y)
        
        # Draw local player
        skater.draw(screen, cam_x, cam_y)
        draw_hud(race_time)
        pygame.display.flip()

    # Disconnect from server
    if multiplayer and client:
        client.disconnect()

    # Show final stats
    if finished:
        show_stats(race_time, skater.crashes)

if __name__ == "__main__":
    # Ask user if multiplayer
    print("1. Singleplayer")
    print("2. Multiplayer")
    choice = input("Select mode: ")
    
    if choice == "2":
        server_ip = input("Server IP (default 127.0.0.1): ").strip()
        if not server_ip:
            server_ip = "127.0.0.1"
        game_loop(multiplayer=True, server_ip=server_ip)
    else:
        game_loop(multiplayer=False)
    
    pygame.quit()
    sys.exit()