import pygame, os
from pygame.math import Vector2
import math
import sys

def resource_path(relative_path):
    # Funziona sia in sviluppo che in build
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def load_frames(path, scale=1.0):
    frames = []
    for fname in sorted(os.listdir(path)):
        if fname.endswith(".png"):
            img = pygame.image.load(resource_path(os.path.join(path, fname))).convert_alpha()
            if scale != 1.0:
                new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
                img = pygame.transform.scale(img, new_size)
            frames.append(img)
    return frames

class Skater:
    def __init__(self, spawn_point, scale=1.0):
        self.scale = scale
        self.idle_frames = load_frames("assets/images/thing/idle", scale)
        self.sprint_frames = load_frames("assets/images/thing/sprint", scale)
        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.frame_timer = 0.0
        self.frame_speed = 0.15

        self.pos = Vector2(spawn_point)
        self.vx = 0.0
        self.vy = 0.0
        self.angle = 0.0
        self.rect = self.idle_frames[0].get_rect(center=spawn_point)

        # Scale physics parameters
        self.accel = 90 * scale
        self.max_speed = 300 * scale
        self.turn_rate = 200
        self.friction = 0.98

        self.crashes = 0

    def update(self, keys, dt):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= self.turn_rate * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += self.turn_rate * dt

        forward = Vector2(
            math.cos(math.radians(self.angle - 90)),
            math.sin(math.radians(self.angle - 90))
        )

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vx += forward.x * self.accel * dt
            self.vy += forward.y * self.accel * dt

        self.vx *= self.friction
        self.vy *= self.friction

        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            scale_factor = self.max_speed / speed
            self.vx *= scale_factor
            self.vy *= scale_factor

        self.pos.x += self.vx * dt
        self.pos.y += self.vy * dt
        self.rect.center = self.pos

        # Animation threshold scaled
        if speed > 20 * self.scale:
            self.current_frames = self.sprint_frames
        else:
            self.current_frames = self.idle_frames

        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)

    def update_animation(self, dt):
        """Update animation frames for remote players"""
        speed = math.hypot(self.vx, self.vy)
        
        # Animation threshold scaled
        if speed > 20 * self.scale:
            self.current_frames = self.sprint_frames
        else:
            self.current_frames = self.idle_frames

        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)

    def draw(self, surface, cam_x, cam_y):
        frame = self.current_frames[self.frame_index]
        rotated = pygame.transform.rotate(frame, -(self.angle))
        rect = rotated.get_rect(center=(self.pos.x - cam_x,
                                        self.pos.y - cam_y))
        surface.blit(rotated, rect)