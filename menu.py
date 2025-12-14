import pygame, sys, os, json
import main as m, editor as ed, main_multiplayer as mm, local as lc
import tkinter as tk
from tkinter import simpledialog

def ask_track_name():
    root = tk.Tk()
    root.withdraw()  # nasconde la finestra principale
    name = simpledialog.askstring("New Track", "Inserisci il nome della nuova pista:")
    root.destroy()
    return name

pygame.init()

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
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ice Drift - Menu")
clock = pygame.time.Clock()

font_size = int(28 * SCALE)
font = pygame.font.SysFont("consolas", font_size)

# Menu states
state = "main"  # "main", "play", "editor", "settings"
scroll_offset = 0

def draw_text(text, x, y, hover=False):
    color = (255,255,255) if not hover else (200,200,50)
    surf = font.render(text, True, color)
    screen.blit(surf, (int(x), int(y)))
    return surf.get_rect(topleft=(int(x), int(y)))

def list_tracks():
    files = [f for f in os.listdir("maps") if f.endswith(".json")]
    return sorted(files)

def run_game(track):
    # Write BEFORE running the game
    with open("selected.txt", "w") as f:
        f.write(track)
    m.game_loop()

def run_editor(track):
    # Write BEFORE running the editor
    with open("selected.txt", "w") as f:
        f.write(track)
    ed.game_loop()

def save_settings(option):
    with open("settings.txt","w") as f:
        f.write(str(option))

running=True
last_click = False  # Track click state to avoid multiple triggers

while running:
    for e in pygame.event.get():
        if e.type==pygame.QUIT: 
            running=False
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_ESCAPE: 
                state="main"
                scroll_offset=0
        if e.type==pygame.MOUSEBUTTONDOWN:
            if e.button==4: scroll_offset = max(0, scroll_offset-int(40*SCALE))
            if e.button==5: scroll_offset += int(40*SCALE)

    screen.fill((30,30,30))

    mx,my = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    
    # Only register click on the frame it becomes True
    clicked_this_frame = click and not last_click
    last_click = click

    if state=="main":
        # Calculate text widths for proper centering
        play_width = font.render("Play", True, (255,255,255)).get_width()
        multiplayer_width = font.render("Online", True, (255,255,255)).get_width()
        local_width = font.render("Local", True, (255,255,255)).get_width()
        editor_width = font.render("Editor", True, (255,255,255)).get_width()
        settings_width = font.render("Settings", True, (255,255,255)).get_width()
        
        r1 = draw_text("Play", WIDTH//2 - play_width//2, HEIGHT//2-int(120*SCALE), 
                      pygame.Rect(WIDTH//2 - play_width//2, HEIGHT//2-int(120*SCALE),
                                  play_width, int(35*SCALE)).collidepoint(mx,my))
        r2 = draw_text("Online", WIDTH//2 - multiplayer_width//2, HEIGHT//2-int(60*SCALE), 
                      pygame.Rect(WIDTH//2 - multiplayer_width//2, HEIGHT//2-int(60*SCALE),
                                  multiplayer_width, int(35*SCALE)).collidepoint(mx,my))
        r5 = draw_text("Local", WIDTH//2 - local_width//2, HEIGHT//2, 
              pygame.Rect(WIDTH//2 - local_width//2, HEIGHT//2,
                          local_width, int(35*SCALE)).collidepoint(mx,my))

        r3 = draw_text("Editor", WIDTH//2 - editor_width//2, HEIGHT//2+int(60*SCALE), 
                    pygame.Rect(WIDTH//2 - editor_width//2, HEIGHT//2+int(60*SCALE),
                                editor_width, int(35*SCALE)).collidepoint(mx,my))

        r4 = draw_text("Settings", WIDTH//2 - settings_width//2, HEIGHT//2+int(120*SCALE), 
                    pygame.Rect(WIDTH//2 - settings_width//2, HEIGHT//2+int(120*SCALE),
                                settings_width, int(35*SCALE)).collidepoint(mx,my))
        if clicked_this_frame:
            if r1.collidepoint(mx,my): 
                state="play"
                scroll_offset=0
            elif r2.collidepoint(mx,my):
                mm.game_loop(multiplayer=True)
            elif r5.collidepoint(mx,my): 
                lc.game_loop()
            elif r3.collidepoint(mx,my): 
                state="editor"
                scroll_offset=0
            elif r4.collidepoint(mx,my): 
                state="settings"

    elif state=="play":
        draw_text("Select Track (ESC to return)", int(100*SCALE), int(10*SCALE), False)
        y=int(40*SCALE)-scroll_offset
        spacing = int(40*SCALE)
        for track in list_tracks():
            rect = draw_text(track, int(100*SCALE), y, 
                           pygame.Rect(int(100*SCALE),y,int(300*SCALE),int(30*SCALE)).collidepoint(mx,my))
            if clicked_this_frame and rect.collidepoint(mx,my):
                run_game(track)
            y+=spacing

    elif state=="editor":
        draw_text("Select Track (ESC to return)", int(100*SCALE), int(10*SCALE), False)
        y=int(40*SCALE)-scroll_offset
        spacing = int(40*SCALE)
        for track in list_tracks():
            rect = draw_text(track, int(100*SCALE), y, 
                           pygame.Rect(int(100*SCALE),y,int(300*SCALE),int(30*SCALE)).collidepoint(mx,my))
            if clicked_this_frame and rect.collidepoint(mx,my):
                run_editor(track)
            y+=spacing
        # New Track button
        rect = draw_text("[ New Track ]", int(100*SCALE), y+int(20*SCALE), 
                        pygame.Rect(int(100*SCALE),y+int(20*SCALE),int(300*SCALE),int(30*SCALE)).collidepoint(mx,my))
        if clicked_this_frame and rect.collidepoint(mx,my):
            # Create a simple empty grid
            empty_grid = [["ice1" for x in range((960//32)*16)] for y in range((540//32)*16)]
            name = ask_track_name()
            if name:
                if not name.endswith(".json"):
                    name += ".json"
                path = os.path.join("maps", name)
                with open(path,"w") as f:
                    json.dump(empty_grid, f)
                run_editor(name)

    elif state=="settings":
        draw_text("Resolution Settings (ESC to return)", int(100*SCALE), int(50*SCALE), False)
        opt1 = draw_text("960x540", int(100*SCALE), int(100*SCALE), 
                        pygame.Rect(int(100*SCALE),int(100*SCALE),int(200*SCALE),int(30*SCALE)).collidepoint(mx,my))
        opt2 = draw_text("1920x1080", int(100*SCALE), int(150*SCALE), 
                        pygame.Rect(int(100*SCALE),int(150*SCALE),int(200*SCALE),int(30*SCALE)).collidepoint(mx,my))
        draw_text("Restart required after changing", int(100*SCALE), int(280*SCALE), False)
        if clicked_this_frame:
            if opt1.collidepoint(mx,my): 
                save_settings(1)
                draw_text("Saved!", int(350*SCALE), int(100*SCALE), False)
            elif opt2.collidepoint(mx,my): 
                save_settings(2)
                draw_text("Saved!", int(350*SCALE), int(150*SCALE), False)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()