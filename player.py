from settings import *
import pygame as pg
import math

class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.shot = False
        self.health = PLAYER_MAX_HEALTH
        self.rel = 0
        self.health_recovery_delay = 700
        self.time_prev = pg.time.get_ticks()
        self.ammo = {'shotgun': 20, 'pistolet': 50}
        pg.mouse.set_visible(False)

    def recover_health(self):
        if self.check_health_recovery_delay() and self.health < PLAYER_MAX_HEALTH:
            self.health += 1

    def check_health_recovery_delay(self):
        time_now = pg.time.get_ticks()
        if time_now - self.time_prev > self.health_recovery_delay:
            self.time_prev = time_now
            return True

    def check_game_over(self):
        if self.health < 1:
            self.game.object_renderer.game_over()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def get_damage(self, damage):
        self.health -= damage
        self.game.object_renderer.player_damage()
        self.game.sound.player_pain.play()
        self.check_game_over()

    def single_fire_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.fire()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.fire()
            if event.key == pg.K_e:
                self.interact()

    def interact(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        check_x = int(self.x + cos_a * 0.5)
        check_y = int(self.y + sin_a * 0.5)
        
        if (check_x, check_y) in self.game.map.world_map:
            if self.game.map.world_map[(check_x, check_y)] == 11:
                # VÉRIFICATION : Reste-t-il des monstres vivants ?
                enemies_alive = any(npc.alive for npc in self.game.object_handler.npc_list)
                
                if not enemies_alive:
                    # VICTOIRE
                    self.game.object_renderer.victory_mode = True
                else:
                    # ÉCHEC : Dégâts éclairs (20 points)
                    self.get_damage(20)
                    self.game.object_renderer.trigger_lightning_trap()

    def check_interaction(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        check_x = int(self.x + cos_a * 0.5)
        check_y = int(self.y + sin_a * 0.5)
        if (check_x, check_y) in self.game.map.world_map and \
           self.game.map.world_map[(check_x, check_y)] == 11:
            self.game.object_renderer.show_interact_msg = True
        else:
            self.game.object_renderer.show_interact_msg = False

    def fire(self):
        current_weapon = self.game.weapon.current_weapon
        if not self.shot and not self.game.weapon.reloading and self.ammo[current_weapon] > 0:
            if current_weapon == 'pistolet':
                self.game.sound.tir_pistolet.play()
            else:
                self.game.sound.shotgun.play()
            self.shot = True
            self.game.weapon.reloading = True
            self.ammo[current_weapon] -= 1 

    def movement(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        speed = PLAYER_SPEED * self.game.delta_time
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a
        keys = pg.key.get_pressed()
        if keys[pg.K_z]:
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            dx += -speed_cos
            dy += -speed_sin
        if keys[pg.K_q]:
            self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        if keys[pg.K_d]:
            self.angle += PLAYER_ROT_SPEED * self.game.delta_time
        self.check_wall_collision(dx, dy)
        if keys[pg.K_LEFT]:
            self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        if keys[pg.K_RIGHT]:
            self.angle += PLAYER_ROT_SPEED * self.game.delta_time
        self.angle %= math.tau

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        scale = PLAYER_SIZE_SCALE / self.game.delta_time
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    def update(self):
        self.movement()
        self.recover_health()
        self.check_interaction()

    @property
    def pos(self): return self.x, self.y
    @property
    def map_pos(self): return int(self.x), int(self.y)