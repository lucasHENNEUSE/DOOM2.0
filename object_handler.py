from sprite_object import *
from npc import *
from random import choices, randrange
import cv2

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
            self.base_hp = 200
        elif difficulty == 'MEDIUM':
            self.enemies = 12
            self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC, MVNPC]
            self.weights = [40, 25, 10, 25]
            self.base_hp = 150
        else: # DIFFICILE
            self.enemies = 20
            self.npc_types = [SoldierNPC, CacoDemonNPC, CyberDemonNPC, MVNPC]
            self.weights = [20, 30, 20, 30] 
            self.base_hp = 100

        self.restricted_area = {(i, j) for i in range(10) for j in range(10)}
        # Le spawn est déplacé dans la méthode setup() appelée par Game

    def setup(self):
        self.spawn_npc()
        self.spawn_ammo()

    def spawn_ammo(self):
        # On définit les deux munitions : image 0 (shotgun) et image 1 (pistolet)
        ammo_configs = [
            {'path': 'resources/sprites/weapon/munition/0.png', 'type': 'shotgun', 'amount': 10},
            {'path': 'resources/sprites/weapon/munition/1.png', 'type': 'pistolet', 'amount': 20}
        ]
        
        for config in ammo_configs:
            pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            # On cherche une case vide (pas un mur et pas la zone de départ)
            while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            
            # On crée l'objet Munition
            self.add_sprite(AmmoItem(self.game, config['path'], (x + 0.5, y + 0.5), 
                                     config['type'], config['amount']))

    def spawn_npc(self):
        for i in range(self.enemies):
            npc_class = choices(self.npc_types, self.weights)[0]
            pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            while (pos in self.game.map.world_map) or (pos in self.restricted_area):
                pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
            
            enemy = npc_class(self.game, pos=(x + 0.5, y + 0.5))
            enemy.health = self.base_hp
            self.add_npc(enemy)

    def check_win(self):
        # Désactivé : c'est maintenant l'interrupteur qui gère la fin de partie
        pass

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        
        # Mise à jour et nettoyage des sprites (munitions ou projectiles)
        for sprite in self.sprite_list[:]:
            sprite.update()
            # On supprime si c'est une boule de feu expirée OU une munition ramassée
            if (hasattr(sprite, 'expired') and sprite.expired) or (hasattr(sprite, 'picked_up') and sprite.picked_up):
                self.sprite_list.remove(sprite)
                
        [npc.update() for npc in self.npc_list]
        self.check_win()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)