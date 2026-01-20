import pygame as pg
from sprite_object import *
from random import randint, random
import math

# --- PROJECTILE : Boule de feu ---
class Fireball(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/npc/mv/attack/1.png', pos=(11.5, 3.5), 
                 scale=0.4, shift=0.2, animation_time=100):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.speed = 0.15
        self.angle = math.atan2(game.player.y - pos[1], game.player.x - pos[0])
        self.damage = 10
        self.hit_player = False
        self.explosion_image = pg.image.load('resources/sprites/npc/mv/attack/2.png').convert_alpha()
        self.expired = False
        self.timer = 0
        self.explosion_duration = 400

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        if not self.hit_player:
            self.move()
            self.check_collision()
        else:
            self.timer += self.game.delta_time
            if self.timer > self.explosion_duration:
                self.expired = True

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def check_collision(self):
        dist = math.hypot(self.game.player.x - self.x, self.game.player.y - self.y)
        if dist < 0.4 or (int(self.x), int(self.y)) in self.game.map.world_map:
            self.hit_player = True
            self.image = self.explosion_image
            if dist < 0.4: self.game.player.get_damage(self.damage)

# --- CLASSE DE BASE NPC ---
class NPC(AnimatedSprite):
    def __init__(self, game, path, pos, scale, shift, animation_time):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images = self.get_images(self.path + '/walk')
        self.attack_dist = randint(3, 6)
        self.speed = 0.03
        self.size = 20
        self.health = 100 
        self.attack_damage = 10
        self.accuracy = 0.15
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.last_attack_time = pg.time.get_ticks()

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()

    def animate_death(self):
        if not self.alive:
            # On anime la chute tant qu'on n'a pas atteint la dernière image
            if self.game.global_trigger and self.frame_counter < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1
            
            # Une fois l'animation finie, on force l'affichage de POSSU0
            if self.frame_counter >= len(self.death_images) - 1:
                # On bloque sur la dernière image de la liste (qui doit être POSSU0)
                self.image = self.death_images[0]

    def run_logic(self):
        if self.alive:
            self.ray_cast_value = self.ray_cast_player_npc()
            self.check_hit_in_npc()
            if self.pain:
                self.animate(self.pain_images)
                if self.animation_trigger: self.pain = False
            elif self.ray_cast_value:
                if self.dist < self.attack_dist:
                    self.animate(self.attack_images)
                    self.attack()
                else:
                    self.animate(self.walk_images)
                    self.movement()
            else: self.animate(self.idle_images)
        else:
            self.animate_death()

    @property
    def map_pos(self): return int(self.x), int(self.y)

    def ray_cast_player_npc(self):
        if self.game.player.map_pos == self.map_pos: return True
        ox, oy = self.game.player.pos
        angle = math.atan2(oy - self.y, ox - self.x)
        sin_a = math.sin(angle); cos_a = math.cos(angle)
        dist_to_player = math.hypot(ox - self.x, oy - self.y)
        for j in range(int(dist_to_player)):
            test_x = self.x + j * cos_a
            test_y = self.y + j * sin_a
            if (int(test_x), int(test_y)) in self.game.map.world_map: return False
        return True

    def check_hit_in_npc(self):
        if self.ray_cast_value and self.game.player.shot:
            if HALF_WIDTH - self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:
                self.game.sound.npc_pain.play()
                self.game.player.shot = False
                self.pain = True
                self.health -= self.game.weapon.damage
                if self.health < 1:
                    self.alive = False
                    self.frame_counter = 0 # Crucial : on repart de zéro pour la mort
                    self.game.sound.npc_death.play()

    def movement(self):
        next_pos = self.game.pathfinding.get_path(self.map_pos, self.game.player.map_pos)
        next_x, next_y = next_pos
        angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

# --- CLASSES SPÉCIFIQUES ---

class SoldierNPC(NPC):
    def __init__(self, game, pos=(10.5, 5.5)):
        super().__init__(game, path='resources/sprites/npc/soldier/0.png', pos=pos, scale=0.6, shift=0.38, animation_time=180)
        self.attack_cooldown = 2000 

    def attack(self):
        now = pg.time.get_ticks()
        if self.animation_trigger and now - self.last_attack_time > self.attack_cooldown:
            self.game.sound.npc_shot.play()
            if random() < self.accuracy: self.game.player.get_damage(self.attack_damage)
            self.last_attack_time = now

class CacoDemonNPC(NPC):
    def __init__(self, game, pos=(10.5, 6.5)):
        super().__init__(game, path='resources/sprites/npc/caco_demon/0.png', pos=pos, scale=0.7, shift=0.27, animation_time=250)
        self.attack_dist = 1.0; self.attack_damage = 2

    def attack(self):
        if self.animation_trigger:
            self.game.sound.npc_shot.play()
            if random() < self.accuracy: self.game.player.get_damage(self.attack_damage)

class CyberDemonNPC(NPC):
    def __init__(self, game, pos=(11.5, 6.0)):
        super().__init__(game, path='resources/sprites/npc/cyber_demon/0.png', pos=pos, scale=1.0, shift=0.04, animation_time=210)
        self.attack_dist = 6; self.attack_damage = 15

    def attack(self):
        if self.animation_trigger:
            self.game.sound.npc_shot.play()
            if random() < self.accuracy: self.game.player.get_damage(self.attack_damage)

class MVNPC(NPC):
    def __init__(self, game, pos=(12.5, 7.5)):
        super().__init__(game, path='resources/sprites/npc/mv/0.png', pos=pos, scale=0.8, shift=0.15, animation_time=200)
        self.speed = 0.04; self.attack_dist = 8; self.attack_cooldown = 2500 
    
    def attack(self):
        now = pg.time.get_ticks()
        if self.animation_trigger and now - self.last_attack_time > self.attack_cooldown:
            self.game.sound.feu.play()
            fire = Fireball(self.game, pos=(self.x, self.y))
            self.game.object_handler.add_sprite(fire)
            self.last_attack_time = now