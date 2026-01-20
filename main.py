import pygame as pg
import sys
import cv2
import math
import os
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *

class Game:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        pg.mixer.quit()
        pg.mixer.pre_init(22050, -16, 2, 1024)
        pg.init()
        pg.mixer.set_num_channels(64)
        
        pg.mouse.set_visible(True)
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        
        self.menu_active = True
        self.difficulty_menu_active = False
        
        self.start_time = pg.time.get_ticks() 
        self.text_delay = 8000 

        self.difficulty_options = ['FACILE', 'MEDIUM', 'DIFFICILE']
        self.difficulty_index = 0
        self.font_menu = pg.font.SysFont('Arial', 70, bold=True)
        
        self.video = cv2.VideoCapture('resources/sprites/doom.mp4')
        self.last_frame = None 
        
        # --- LOGO OPAQUE AU BORD EXTRÊME ---
        logo_img = pg.image.load('resources/sprites/l.png').convert_alpha()
        
        # Taille du logo
        self.logo_size = 180
        self.logo_overlay = pg.transform.smoothscale(logo_img, (self.logo_size, self.logo_size))
        
        # On s'assure que l'alpha est au maximum (Opaque)
        self.logo_overlay.set_alpha(255) 
        
        # Position : Bord extrême avec une marge de 5 pixels
        self.logo_pos = (WIDTH - self.logo_size - 5, HEIGHT - self.logo_size - 5)
        
        # Curseur
        tm_img = pg.image.load('resources/sprites/tm.png').convert_alpha()
        self.skull_cursor = pg.transform.scale(tm_img, (60, 60))
        
        self.new_game()
        self.sound.play_menu_music()

    def new_game(self, difficulty='MEDIUM'):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self, difficulty)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)

    def draw_difficulty_menu(self):
        self.screen.fill('black')
        title = self.font_menu.render('CHOISIS TA DIFFICULTÉ', True, 'red')
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 6))

        for i, option in enumerate(self.difficulty_options):
            color = 'white' if i == self.difficulty_index else 'gray'
            text = self.font_menu.render(option, True, color)
            pos_y = HEIGHT // 2.5 + i * 110
            pos_x = WIDTH // 2 - text.get_width() // 2
            self.screen.blit(text, (pos_x, pos_y))
            
            if i == self.difficulty_index:
                self.screen.blit(self.skull_cursor, (pos_x - 90, pos_y + 5))
        pg.display.flip()

    def draw_menu(self):
        ret, frame = self.video.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, RES)
            self.last_frame = pg.surfarray.make_surface(frame.swapaxes(0, 1))
        
        if self.last_frame:
            self.screen.blit(self.last_frame, (0, 0))
        
        # Affichage du logo opaque
        self.screen.blit(self.logo_overlay, self.logo_pos)
        
        current_time = pg.time.get_ticks()
        if current_time - self.start_time > self.text_delay:
            if math.sin(current_time * 0.005) > 0:
                msg = self.font_menu.render('APPUYEZ SUR ENTRÉE', True, 'white')
                msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                self.screen.blit(msg, msg_rect)
            
        pg.display.flip()

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            
            if self.menu_active:
                if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    self.sound.npc_shot.play()
                    self.menu_active = False
                    self.difficulty_menu_active = True
                    self.video.release()

            elif self.difficulty_menu_active:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        self.difficulty_index = (self.difficulty_index - 1) % len(self.difficulty_options)
                    elif event.key == pg.K_DOWN:
                        self.difficulty_index = (self.difficulty_index + 1) % len(self.difficulty_options)
                    elif event.key == pg.K_RETURN:
                        self.sound.npc_shot.play()
                        selected_diff = self.difficulty_options[self.difficulty_index]
                        self.difficulty_menu_active = False
                        self.new_game(selected_diff)
                        pg.mouse.set_visible(False)
                        pg.event.set_grab(True)
                        self.sound.play_theme()
            else:
                if event.type == self.global_event:
                    self.global_trigger = True
                
                # CHANGEMENT D'ARME AVEC TOUCHE R
                if event.type == pg.KEYDOWN and event.key == pg.K_r:
                    self.weapon.change_weapon()
                    
                self.player.single_fire_event(event)

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'FPS: {self.clock.get_fps() :.1f}')

    def run(self):
        while True:
            self.check_events()
            if self.menu_active:
                self.draw_menu()
                self.clock.tick(21)
            elif self.difficulty_menu_active:
                self.draw_difficulty_menu()
                self.clock.tick(60)
            else:
                self.update()
                self.object_renderer.draw()
                self.weapon.draw()
                pg.display.flip()

if __name__ == '__main__':
    game = Game()
    game.run()