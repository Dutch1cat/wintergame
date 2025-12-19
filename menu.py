import pygame, sys, os, json
import main as m, editor as ed, main_multiplayer as mm, local as lc
import tkinter as tk
from tkinter import simpledialog
from songfunction import play_menu_music

def ask_track_name():
    root = tk.Tk()
    root.withdraw()  # nasconde la finestra principale
    name = simpledialog.askstring(
        "Track name",
        "Name of the new track (use tab to move between the buttons and enter to press one):",
        parent=root
    )
    root.destroy()
    return name


pygame.init()

def load_resolution():
    try:
        with open("settings.txt", "r") as f:
            lines = f.readlines()
            res_mode = int(lines[0].strip())
            volume = float(lines[1].strip()) if len(lines) > 1 else 0.5
            
            if res_mode == 1:
                return 960, 540, 1.0, volume
            elif res_mode == 2:
                return 1920, 1080, 2.0, volume
            elif res_mode == 3:
                return 2560, 1440, 2.667, volume
            else:
                return 960, 540, 1.0, volume
    except:
        return 960, 540, 1.0, 0.5

WIDTH, HEIGHT, SCALE, VOLUME = load_resolution()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ice Drift - Menu")
clock = pygame.time.Clock()

font_size = int(28 * SCALE)
font = pygame.font.SysFont("consolas", font_size)
font2 = pygame.font.Font("assets/fonts/mainfont.ttf", font_size)
font3 = pygame.font.Font("assets/fonts/titlefont.otf", int(64 * SCALE))

play_menu_music()

# Menu states
state = "main"  # "main", "play", "editor", "settings"
scroll_offset = 0
current_volume = VOLUME
dragging_slider = False

def draw_text(text, x, y, hover=False, title=False):
    if title:
        surf = font3.render(text, True, (255,255,255))
        screen.blit(surf, (int(x), int(y)))
        return surf.get_rect(topleft=(int(x), int(y)))
    else:
        color = (255,255,255) if not hover else (200,200,50)
        surf = font2.render(text, True, color)
        screen.blit(surf, (int(x), int(y)))
        return surf.get_rect(topleft=(int(x), int(y)))

def draw_slider(x, y, width, value):
    # Background bar
    bar_rect = pygame.Rect(int(x), int(y), int(width), int(10 * SCALE))
    pygame.draw.rect(screen, (100, 100, 100), bar_rect)
    
    # Filled portion
    filled_width = int(width * value)
    filled_rect = pygame.Rect(int(x), int(y), filled_width, int(10 * SCALE))
    pygame.draw.rect(screen, (200, 200, 50), filled_rect)
    
    # Handle
    handle_x = int(x + width * value)
    handle_rect = pygame.Rect(handle_x - int(8 * SCALE), int(y - 5 * SCALE), 
                               int(16 * SCALE), int(20 * SCALE))
    pygame.draw.rect(screen, (255, 255, 255), handle_rect)
    
    return bar_rect, handle_rect

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

def save_settings(option, volume):
    with open("settings.txt","w") as f:
        f.write(str(option) + "\n")
        f.write(str(volume))

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
        if e.type==pygame.MOUSEBUTTONUP:
            if e.button==1:
                dragging_slider = False

    screen.fill((30,30,30))

    mx,my = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    
    # Only register click on the frame it becomes True
    clicked_this_frame = click and not last_click
    last_click = click

    if state=="main":
        # Calculate text widths for proper centering
        title_width = font2.render("Ice Drifter", True, (255,255,255)).get_width()
        play_width = font2.render("Play", True, (255,255,255)).get_width()
        multiplayer_width = font2.render("Online", True, (255,255,255)).get_width()
        local_width = font2.render("Local", True, (255,255,255)).get_width()
        editor_width = font2.render("Editor", True, (255,255,255)).get_width()
        settings_width = font2.render("Settings", True, (255,255,255)).get_width()
        exit_width = font2.render("Exit", True, (255,255,255)).get_width()

        title = draw_text("Ice Drifter", WIDTH//2 - title_width//2-(40*SCALE), HEIGHT//2 - int(200*SCALE), title=True)


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
        
        r6 = draw_text("Exit", WIDTH//2 - exit_width//2, HEIGHT//2+int(180*SCALE), 
                    pygame.Rect(WIDTH//2 - exit_width//2, HEIGHT//2+int(180*SCALE),
                                exit_width, int(35*SCALE)).collidepoint(mx,my))
    

        if clicked_this_frame:
            if r1.collidepoint(mx,my): 
                state="play"
                scroll_offset=0
            elif r2.collidepoint(mx,my):
                mm.game_loop(multiplayer=True)
            elif r5.collidepoint(mx,my): 
                state="local"
            elif r3.collidepoint(mx,my): 
                state="editor"
                scroll_offset=0
            elif r4.collidepoint(mx,my): 
                state="settings"
            
            elif r6.collidepoint(mx,my): 
                running=False

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
    elif state=="local":
        draw_text("Select Track (ESC to return)", int(100*SCALE), int(10*SCALE), False)
        y=int(40*SCALE)-scroll_offset
        spacing = int(40*SCALE)
        for track in list_tracks():
            rect = draw_text(track, int(100*SCALE), y, 
                           pygame.Rect(int(100*SCALE),y,int(300*SCALE),int(30*SCALE)).collidepoint(mx,my))
            if clicked_this_frame and rect.collidepoint(mx,my):
                with open("selected.txt", "w") as f:
                    f.write(track)
                lc.game_loop()
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
        draw_text("Settings (ESC to return)", int(100*SCALE), int(50*SCALE), False)
        
        # Resolution settings
        draw_text("Resolution:", int(100*SCALE), int(100*SCALE), False)
        opt1 = draw_text("960x540", int(100*SCALE), int(140*SCALE), 
                        pygame.Rect(int(100*SCALE),int(140*SCALE),int(200*SCALE),int(30*SCALE)).collidepoint(mx,my))
        opt2 = draw_text("1920x1080", int(100*SCALE), int(180*SCALE), 
                        pygame.Rect(int(100*SCALE),int(180*SCALE),int(200*SCALE),int(30*SCALE)).collidepoint(mx,my))
        
        # Volume slider
        draw_text("Volume:", int(100*SCALE), int(250*SCALE), False)
        slider_x = int(100*SCALE)
        slider_y = int(290*SCALE)
        slider_width = int(300*SCALE)
        
        bar_rect, handle_rect = draw_slider(slider_x, slider_y, slider_width, current_volume)
        
        # Display volume percentage
        volume_percent = int(current_volume * 100)
        draw_text(f"{volume_percent}", slider_x + slider_width + int(20*SCALE), int(280*SCALE), False)
        
        # Handle slider interaction
        if click and (handle_rect.collidepoint(mx, my) or dragging_slider):
            dragging_slider = True
            # Calculate new volume based on mouse position
            new_volume = max(0.0, min(1.0, (mx - slider_x) / slider_width))
            current_volume = new_volume
            # Save immediately while dragging
            with open("settings.txt", "r") as f:
                lines = f.readlines()
            res_mode = int(lines[0].strip()) if lines else 1
            save_settings(res_mode, current_volume)
            # Update music volume
            pygame.mixer.music.set_volume(current_volume)
        
        
        draw_text("Restart required after changing resolution", int(100*SCALE), int(360*SCALE), False)
        
        if clicked_this_frame:
            if opt1.collidepoint(mx,my): 
                save_settings(1, current_volume)
                draw_text("Saved!", int(350*SCALE), int(140*SCALE), False)
            elif opt2.collidepoint(mx,my): 
                save_settings(2, current_volume)
                draw_text("Saved!", int(350*SCALE), int(180*SCALE), False)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()