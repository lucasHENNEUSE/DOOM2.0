from sprite_object import *
from collections import deque
import pygame as pg

class Weapon(AnimatedSprite):
    def __init__(self, game):
        super().__init__(game=game, path='resources/sprites/weapon/shotgun/0.png', scale=0.4, animation_time=90)
        
        self.weapon_inventory = {
            'shotgun': {'path': 'resources/sprites/weapon/shotgun', 'scale': 0.4, 'time': 90, 'damage': 50},
            'pistolet': {'path': 'resources/sprites/weapon/shotgun/pistolet', 'scale': 0.8, 'time': 80, 'damage': 20}
        }
        self.current_weapon = 'shotgun'
        self.reloading = False
        self.frame_counter = 0
        self.load_weapon(self.current_weapon)

    def load_weapon(self, name):
        conf = self.weapon_inventory[name]
        raw_images = self.get_images(conf['path'])
        
        scale = conf['scale']
        base_w = int(raw_images[0].get_width() * scale)
        base_h = int(raw_images[0].get_height() * scale)
        
        self.images = deque()
        for img in raw_images:
            scaled_img = pg.transform.smoothscale(img, (base_w, base_h))
            self.images.append(scaled_img)
        
        self.image = self.images[0]
        self.num_images = len(self.images)
        self.animation_time = conf['time']
        self.damage = conf['damage']
        self.weapon_pos = (HALF_WIDTH - base_w // 2, HEIGHT - base_h)

    def change_weapon(self):
        if not self.reloading:
            if self.current_weapon == 'shotgun':
                self.current_weapon = 'pistolet'
            else:
                self.current_weapon = 'shotgun'
            self.load_weapon(self.current_weapon)
            self.frame_counter = 0

    def animate_shot(self):
        if self.reloading:
            self.game.player.shot = False
            if self.animation_trigger:
                self.images.rotate(-1)
                self.image = self.images[0]
                self.frame_counter += 1
                if self.frame_counter == self.num_images:
                    self.reloading = False
                    self.frame_counter = 0

    def draw(self):
        self.game.screen.blit(self.images[0], self.weapon_pos)

    def update(self):
        self.check_animation_time()
        self.animate_shot()