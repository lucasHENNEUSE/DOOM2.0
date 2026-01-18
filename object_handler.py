from sprite_object import *
from npc import *
from random import choices, randrange

class ObjectHandler:
    def __init__(self, game, difficulty='MEDIUM'):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.npc_positions = {}
        
        # --- CONFIGURATION SELON DIFFICULTÉ ---
        self.difficulty = difficulty
        if difficulty == 'FACILE':
            self.enemies = 5
            self.npc_types = [SoldierNPC]
            self.weights = [100]
            self.base_hp = 300
        elif difficulty == 'MEDIUM':
            self.enemies = 12
            self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC, MVNPC]
            self.weights = [40, 25, 10, 25]
            self.base_hp = 200
        else: # DIFFICILE
            self.enemies = 20
            self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC, MVNPC]
            self.weights = [20, 30, 20, 30] # Plus de monstres d'élite
            self.base_hp = 100

        self.restricted_area = {(i, j) for i in range(10) for j in range(10)}
        self.spawn_npc()

    def spawn_npc(self):
        for i in range(self.enemies):
            npc_class = choices(self.npc_types, self.weights)[0]
            pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            
            # Créer le monstre
            enemy = npc_class(self.game, pos=(x + 0.5, y + 0.5))
            # Appliquer les points de vie selon la difficulté
            enemy.health = self.base_hp
            self.add_npc(enemy)

    def check_win(self):
        if not any(npc.alive for npc in self.npc_list):
            self.game.object_renderer.win()
            pg.display.flip()
            pg.time.delay(3000)
            # Retour au menu principal après victoire
            self.game.menu_active = True
            pg.mouse.set_visible(True)
            self.game.video = cv2.VideoCapture('resources/sprites/doom.mp4')

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        for sprite in self.sprite_list[:]:
            sprite.update()
            if hasattr(sprite, 'expired') and sprite.expired:
                self.sprite_list.remove(sprite)
        [npc.update() for npc in self.npc_list]
        self.check_win()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)