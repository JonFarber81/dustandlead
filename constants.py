"""
Game constants and configuration
"""
import tcod

# Screen dimensions
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 50

# Colors
COLOR_PLAYER = tcod.white
COLOR_ENEMY = tcod.red
COLOR_WALL = tcod.dark_gray
COLOR_FLOOR = tcod.darker_gray
COLOR_BULLET = tcod.yellow
COLOR_BLOOD = tcod.dark_red

# New terrain colors
COLOR_TREE = tcod.dark_green
COLOR_WATER = tcod.blue
COLOR_DIRT = tcod.dark_sepia
COLOR_ROCK = tcod.gray
COLOR_CACTUS = tcod.green
COLOR_BUILDING = tcod.dark_amber

# Game settings
PLAYER_MAX_HP = 100
ENEMY_MAX_HP = 100
MAX_SHOOTING_RANGE = 15
MIN_ACCURACY = 0.3
DAMAGE_MIN = 25
DAMAGE_MAX = 40

# Bonus system
BONUS_TOUGH_HP = 20
BONUS_LONGSHOT_RANGE_MULTIPLIER = 1.5
BONUS_LONGSHOT_ACCURACY_PENALTY = 0.3
BONUS_QUICKDRAW_DAMAGE_BONUS = 10
BONUS_EAGLE_EYE_ACCURACY_BONUS = 0.2
BONUS_GUNSLINGER_CRIT_CHANCE = 0.15
BONUS_DESPERADO_DAMAGE_TAKEN_MULTIPLIER = 1.5
BONUS_DESPERADO_DAMAGE_DEALT_MULTIPLIER = 1.4

# Animation settings
BULLET_ANIMATION_DELAY = 0.05
IMPACT_ANIMATION_DELAY = 0.2
HIT_ANIMATION_DELAY = 0.3

# Map generation
MIN_WALL_CLUSTERS = 15
MAX_WALL_CLUSTERS = 25
MIN_CLUSTER_SIZE = 1
MAX_CLUSTER_SIZE = 4

# Terrain generation settings
TREE_CLUSTERS = (3, 8)  # Min, max tree clusters
TREE_CLUSTER_SIZE = (2, 6)  # Min, max trees per cluster
WATER_FEATURES = (0, 2)  # Min, max water features (rivers/ponds)
WATER_SIZE = (3, 8)  # Min, max size of water features
ROCK_FORMATIONS = (2, 5)  # Min, max rock formations
CACTUS_PATCHES = (1, 4)  # Min, max cactus patches
BUILDING_RUINS = (0, 3)  # Min, max old building ruins