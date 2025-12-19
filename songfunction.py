import pygame
import random
import os

def play_random():
    files = [f for f in os.listdir("assets/sounds/songs/race")]
    random_song = random.choice(files)
    pygame.mixer.music.stop()
    pygame.mixer.music.load("assets/sounds/songs/race/" + random_song)
    volume()
    pygame.mixer.music.play(-1)
def play_menu_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.load("assets/sounds/songs/menu/cyber_shop.ogg")
    volume()
    pygame.mixer.music.play(-1)
def stop_music():
    pygame.mixer.music.stop()
def get_volume():
    with open("settings.txt", "r") as f:
        lines = f.readlines()
        line = lines[1].strip()
        try:
            volume = float(line)
            return max(0.0, min(1.0, volume))
        except:
            return 1.0
def set_volume(volume):
    pygame.mixer.music.set_volume(volume)

def volume():
    volume = get_volume()
    set_volume(volume)

def win():
    pygame.mixer.music.stop()
    pygame.mixer.music.load("assets/sounds/sfx/win.mp3")
    volume()
    pygame.mixer.music.play()
def crash():
    sound = pygame.mixer.Sound("assets/sounds/sfx/hurt.wav")
    volume = get_volume()
    sound.set_volume(volume)
    sound.play()