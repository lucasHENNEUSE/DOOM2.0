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
        self.pickup_font = pg.font.SysFont('Arial', 40, bold=True) # Police pour le message vert
        
        # Variables pour le message de munitions
        self.show_pickup_msg = False
        self.pickup_msg_time = 0
        self.pickup_msg_duration = 2000 # 2 secondes

        self.game_over_image = self.get_texture('resources/textures/game_over.png', RES)
        self.win_image = self.get_texture('resources/textures/win.png', RES)
        self.wall_10 = self.get_texture('resources/textures/10.png')
        self.wall_11 = self.get_texture('resources/textures/11.png')
        self.wall_anim_speed = 500

    def draw(self):
        self.update_wall_animation()
        self.draw_background()
        self.render_game_objects()
        self.draw_player_health()
        self.draw_player_ammo()
        self.draw_pickup_message() # NOUVELLE MÉTHODE

    def draw_pickup_message(self):
        if self.show_pickup_msg:
            time_now = pg.time.get_ticks()
            if time_now - self.pickup_msg_time < self.pickup_msg_duration:
                msg = self.pickup_font.render("MUNITIONS RÉCUPÉRÉES !", True, 'green')
                msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 4))
                self.screen.blit(msg, msg_rect)
            else:
                self.show_pickup_msg = False

    def update_wall_animation(self):
        time_now = pg.time.get_ticks()
        if (time_now // self.wall_anim_speed) % 2 == 0:
            self.wall_textures[10] = self.wall_10
        else:
            self.wall_textures[10] = self.wall_11

    def draw_player_health(self):
        health = str(self.game.player.health)
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char], (i * self.digit_size, 10))

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
        }