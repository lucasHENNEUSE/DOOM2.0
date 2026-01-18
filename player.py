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
        # On remet le curseur visible ou on le laisse caché selon ton choix
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
        # Tir avec le clic gauche (optionnel) OU la barre ESPACE
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.fire()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.fire()

    def fire(self):
        if not self.shot and not self.game.weapon.reloading:
            self.game.sound.shotgun.play()
            self.shot = True
            self.game.weapon.reloading = True

    def movement(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        speed = PLAYER_SPEED * self.game.delta_time
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        keys = pg.key.get_pressed()
        
        # --- COMMANDES CLAVIER UNIQUEMENT ---
        # Z : Avancer
        if keys[pg.K_z]:
            dx += speed_cos
            dy += speed_sin
        # S : Reculer
        if keys[pg.K_s]:
            dx += -speed_cos
            dy += -speed_sin
            
        # Q : Pivoter à GAUCHE (Rotation de l'angle)
        if keys[pg.K_q]:
            self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        # D : Pivoter à DROITE (Rotation de l'angle)
        if keys[pg.K_d]:
            self.angle += PLAYER_ROT_SPEED * self.game.delta_time

        # Application des collisions après mouvement Z/S
        self.check_wall_collision(dx, dy)

        # Rotation supplémentaire avec les flèches (toujours utile)
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

    def draw(self):
        # Dessin mini-map
        pg.draw.line(self.game.screen, 'yellow', (self.x * 100, self.y * 100),
                    (self.x * 100 + WIDTH * math.cos(self.angle),
                     self.y * 100 + WIDTH * math.sin(self.angle)), 2)
        pg.draw.circle(self.game.screen, 'green', (self.x * 100, self.y * 100), 15)

    def update(self):
        self.movement()
        self.recover_health()

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)