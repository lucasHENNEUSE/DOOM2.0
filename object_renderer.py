import pygame as pg
from settings import *

class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0
        self.blood_screen = self.get_texture('resources/textures/blood_screen.png', RES)
        
        self.digit_size = 70
        self.digit_images = [self.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        
        self.font = pg.font.SysFont('Arial', 50, bold=True)
        self.pickup_font = pg.font.SysFont('Arial', 40, bold=True)
        self.mission_font = pg.font.SysFont('Arial', 60, bold=True)
        
        self.consignes_img = self.get_texture('resources/textures/consignes.png', RES)
        self.text_font = pg.font.SysFont('Arial', 35, bold=True)
        self.load_font = pg.font.SysFont('Arial', 50, bold=True)
        
        self.button_off = self.get_texture('resources/textures/b0.png')
        self.button_on = self.get_texture('resources/textures/b1.png')
        self.interact_font = pg.font.SysFont('Arial', 30, bold=True)
        
        self.lightning_images = [
            self.get_texture('resources/textures/e0.png', RES),
            self.get_texture('resources/textures/e1.png', RES)
        ]
        self.lightning_trigger = False
        self.lightning_time = 0
        self.show_interact_msg = False
        self.victory_mode = False

        self.show_pickup_msg = False
        self.pickup_msg_time = 0
        self.pickup_msg_duration = 2000

        self.game_over_image = self.get_texture('resources/textures/game_over.png', RES)
        self.win_image = self.get_texture('resources/textures/win.png', RES)
        self.wall_10 = self.get_texture('resources/textures/10.png')
        self.wall_11 = self.get_texture('resources/textures/11.png')
        self.wall_anim_speed = 500

        # --- NOUVEAU : SYSTEME DE VISAGE ---
        self.face_images = self.load_face_images()
        try:
            self.face_grin_image = self.get_texture('resources/textures/face/grin.png', (80, 90))
        except:
            self.face_grin_image = self.face_images[0]
            
        self.face_grin_time = 0
        self.grin_duration = 1000

    def load_face_images(self):
        face_paths = [
            'resources/textures/face/80_100.png',
            'resources/textures/face/60_80.png',
            'resources/textures/face/40_60.png',
            'resources/textures/face/20_40.png',
            'resources/textures/face/0_20.png'
        ]
        faces = []
        for path in face_paths:
            try:
                faces.append(self.get_texture(path, (80, 90)))
            except:
                surf = pg.Surface((80, 90))
                surf.fill('red')
                faces.append(surf)
        return faces

    def draw_player_face(self):
        # Position en bas à gauche
        pos_x = 10
        pos_y = HEIGHT - 100
        
        if pg.time.get_ticks() - self.face_grin_time < self.grin_duration:
            self.screen.blit(self.face_grin_image, (pos_x, pos_y))
            return

        health_percent = (self.game.player.health / self.game.object_handler.base_hp) * 100
        
        if health_percent > 80: idx = 0
        elif health_percent > 60: idx = 1
        elif health_percent > 40: idx = 2
        elif health_percent > 20: idx = 3
        else: idx = 4
        
        look_offset = 0
        keys = pg.key.get_pressed()
        if keys[pg.K_q] or keys[pg.K_LEFT]: look_offset = -10
        if keys[pg.K_d] or keys[pg.K_RIGHT]: look_offset = 10
        
        self.screen.blit(self.face_images[idx], (pos_x + look_offset, pos_y))

    def draw_loading_screen(self):
        self.screen.blit(self.consignes_img, (0, 0))
        
        lines = [
            "Pour te déplacer, sers-toi des touches : Z, Q, S, D",
            "Pour tirer : ESPACE",
            "Pour changer d'arme : R",
            "Pour interagir : E",
            "",
            "Objectif : Accomplis ta mission avant d'activer",
            "l'interrupteur, sinon tu vas le regretter !!",
        ]
        
        for i, line in enumerate(lines):
            color = 'yellow' if "Objectif" in line else 'white'
            txt = self.text_font.render(line, True, color)
            txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 3 + i * 55))
            self.screen.blit(txt, txt_rect)

        num_dots = (pg.time.get_ticks() // 500) % 4
        dots = "." * num_dots
        load_txt = self.load_font.render(f"Chargement{dots}", True, 'white')
        load_rect = load_txt.get_rect(bottomright=(WIDTH - 50, HEIGHT - 50))
        self.screen.blit(load_txt, load_rect)

    def draw(self):
        self.update_wall_animation()
        self.draw_background()
        self.render_game_objects()
        self.draw_player_health()
        self.draw_player_ammo()
        self.draw_pickup_message()
        self.draw_player_face() 
        
        if self.show_interact_msg and not self.victory_mode:
            msg = self.interact_font.render("APPUYEZ SUR E POUR TERMINER", True, 'white')
            msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            self.screen.blit(msg, msg_rect)
            
        self.draw_lightning_trap()
        if self.victory_mode:
            self.win()

    def trigger_lightning_trap(self):
        self.lightning_trigger = True
        self.lightning_time = pg.time.get_ticks()

    def draw_lightning_trap(self):
        if self.lightning_trigger:
            time_now = pg.time.get_ticks()
            if time_now - self.lightning_time < 1000:
                img = self.lightning_images[(time_now // 100) % 2]
                self.screen.blit(img, (0, 0))
                msg = self.mission_font.render("TU DOIS FINIR TA MISSION !", True, 'red')
                msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.blit(msg, msg_rect)
            else:
                self.lightning_trigger = False

    def update_wall_animation(self):
        time_now = pg.time.get_ticks()
        if (time_now // self.wall_anim_speed) % 2 == 0:
            self.wall_textures[10] = self.wall_10
        else:
            self.wall_textures[10] = self.wall_11
        if not self.victory_mode:
            self.wall_textures[11] = self.button_off
        else:
            self.wall_textures[11] = self.button_on

    def draw_pickup_message(self):
        if self.show_pickup_msg:
            time_now = pg.time.get_ticks()
            if time_now - self.pickup_msg_time < self.pickup_msg_duration:
                self.face_grin_time = self.pickup_msg_time
                msg = self.pickup_font.render("MUNITIONS RÉCUPÉRÉES !", True, 'green')
                msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 4))
                self.screen.blit(msg, msg_rect)
            else:
                self.show_pickup_msg = False

    def draw_player_health(self):
        health = str(self.game.player.health)
        # Décalé à droite du visage (face à 10px + 80px largeur + marge)
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char], (100 + i * self.digit_size, HEIGHT - self.digit_size - 10))

    def draw_player_ammo(self):
        current_weapon = self.game.weapon.current_weapon
        ammo_count = self.game.player.ammo[current_weapon]
        ammo_str = str(ammo_count)
        text_surf = self.font.render("AMMO: ", True, 'white')
        text_rect = text_surf.get_rect(bottomright=(WIDTH - (len(ammo_str) * self.digit_size) - 10, HEIGHT - 10))
        self.screen.blit(text_surf, text_rect)
        color_tint = None
        if ammo_count <= 5:
            if (pg.time.get_ticks() // 250) % 2 == 0:
                color_tint = (255, 0, 0)
        for i, char in enumerate(ammo_str):
            char_img = self.digits[char].copy()
            if color_tint:
                char_img.fill(color_tint, special_flags=pg.BLEND_RGB_MULT)
            pos_x = WIDTH - (len(ammo_str) - i) * self.digit_size - 10
            self.screen.blit(char_img, (pos_x, HEIGHT - self.digit_size - 10))

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

    def render_game_objects(self):
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    def win(self): self.screen.blit(self.win_image, (0, 0))
    def game_over(self): self.screen.blit(self.game_over_image, (0, 0))

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/textures/1.png'),
            2: self.get_texture('resources/textures/2.png'),
            3: self.get_texture('resources/textures/3.png'),
            4: self.get_texture('resources/textures/4.png'),
            5: self.get_texture('resources/textures/5.png'),
            6: self.get_texture('resources/textures/6.png'),
            7: self.get_texture('resources/textures/7.png'),
            8: self.get_texture('resources/textures/8.png'),
            9: self.get_texture('resources/textures/9.png'),
            10: self.get_texture('resources/textures/10.png'),
            11: self.get_texture('resources/textures/b0.png'),
        }