import math

# --- RÉSOLUTION PLUS GRANDE ET ÉCRAN LARGE ---
# 1355x760 est parfait pour un affichage moderne et confortable
RES = WIDTH, HEIGHT = 1348, 750
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 60

# --- PARAMÈTRES JOUEUR ---
PLAYER_POS = 1.5, 5  
PLAYER_ANGLE = 0
PLAYER_SPEED = 0.004
PLAYER_ROT_SPEED = 0.002
PLAYER_SIZE_SCALE = 60
PLAYER_MAX_HEALTH = 300

# --- SOURIS (Sensibilité réajustée pour 1600x900) ---
# On augmente légèrement la sensibilité pour compenser la largeur de l'écran
MOUSE_SENSITIVITY = 0.00020 
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - MOUSE_BORDER_LEFT

# --- RENDU (FOV et Raycasting) ---
# FOV de 90 degrés pour une vision immersive sans déformation
FOV = math.pi / 2 
HALF_FOV = FOV / 2
# On garde NUM_RAYS proportionnel à la largeur pour la précision
NUM_RAYS = WIDTH // 2 
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20

SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

# --- TEXTURES ET COULEURS ---
TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2
FLOOR_COLOR = (30, 30, 30)