import pygame as pg

class Sound:
    def __init__(self, game):
        self.game = game
        self.path = 'resources/sound/'
        
        # Chargement
        self.shotgun = pg.mixer.Sound(self.path + 'shotgun.wav')
        self.npc_pain = pg.mixer.Sound(self.path + 'npc_pain.wav')
        self.npc_death = pg.mixer.Sound(self.path + 'npc_death.wav')
        self.npc_shot = pg.mixer.Sound(self.path + 'tir_pistolet.mp3')
        self.player_pain = pg.mixer.Sound(self.path + 'player_pain.wav')
        self.feu = pg.mixer.Sound(self.path + 'feu.mp3')

        # RÉGLAGE VOLUME BAS POUR ÉVITER LA DISTORSION
        self.set_volume(0.2) 

    def set_volume(self, volume):
        self.shotgun.set_volume(volume)
        self.npc_pain.set_volume(volume)
        self.npc_death.set_volume(volume)
        self.npc_shot.set_volume(volume)
        self.player_pain.set_volume(volume)
        self.feu.set_volume(volume)

    def play_menu_music(self):
        pg.mixer.music.load(self.path + 'menu.mp3')
        pg.mixer.music.set_volume(0.15)
        pg.mixer.music.play(-1)

    def play_theme(self):
        pg.mixer.music.load(self.path + 'theme.mp3')
        pg.mixer.music.set_volume(0.15)
        pg.mixer.music.play(-1)