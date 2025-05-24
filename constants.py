"""
Game constants and configuration

This module contains all game configuration constants including screen dimensions,
colors, game balance settings, bonus system parameters, and map generation settings.
"""
import tcod
from typing import Tuple

# Screen dimensions
SCREEN_WIDTH: int = 80
SCREEN_HEIGHT: int = 50
MAP_WIDTH: int = 80
MAP_HEIGHT: int = 50

# Colors - RGB tuples for various game elements
COLOR_PLAYER: Tuple[int, int, int] = (255, 255, 255)  # white
COLOR_ENEMY: Tuple[int, int, int] = (255, 0, 0)  # red
COLOR_WALL: Tuple[int, int, int] = (64, 64, 64)  # dark_gray
COLOR_FLOOR: Tuple[int, int, int] = (32, 32, 32)  # darker_gray
COLOR_BULLET: Tuple[int, int, int] = (255, 255, 0)  # yellow
COLOR_BLOOD: Tuple[int, int, int] = (128, 0, 0)  # dark_red

# New terrain colors
COLOR_TREE: Tuple[int, int, int] = (0, 128, 0)  # dark_green
COLOR_WATER: Tuple[int, int, int] = (0, 0, 255)  # blue
COLOR_DIRT: Tuple[int, int, int] = (127, 101, 63)  # dark_sepia
COLOR_ROCK: Tuple[int, int, int] = (128, 128, 128)  # gray
COLOR_CACTUS: Tuple[int, int, int] = (0, 255, 0)  # green
COLOR_BUILDING: Tuple[int, int, int] = (255, 192, 0)  # dark_amber

# Game settings - Core gameplay balance parameters
PLAYER_MAX_HP: int = 100
ENEMY_MAX_HP: int = 100
MAX_SHOOTING_RANGE: int = 15
MIN_ACCURACY: float = 0.3
DAMAGE_MIN: int = 25
DAMAGE_MAX: int = 40

# Bonus system - Parameters for player bonus effects
BONUS_TOUGH_HP: int = 20
BONUS_LONGSHOT_RANGE_MULTIPLIER: float = 1.5
BONUS_LONGSHOT_ACCURACY_PENALTY: float = 0.3
BONUS_QUICKDRAW_DAMAGE_BONUS: int = 10
BONUS_EAGLE_EYE_ACCURACY_BONUS: float = 0.2
BONUS_GUNSLINGER_CRIT_CHANCE: float = 0.15
BONUS_DESPERADO_DAMAGE_TAKEN_MULTIPLIER: float = 1.5
BONUS_DESPERADO_DAMAGE_DEALT_MULTIPLIER: float = 1.4

# Animation settings - Timing for visual effects
BULLET_ANIMATION_DELAY: float = 0.05
IMPACT_ANIMATION_DELAY: float = 0.2
HIT_ANIMATION_DELAY: float = 0.3

# Map generation - Basic wall/cover generation parameters
MIN_WALL_CLUSTERS: int = 15
MAX_WALL_CLUSTERS: int = 25
MIN_CLUSTER_SIZE: int = 1
MAX_CLUSTER_SIZE: int = 4

# Terrain generation settings - Parameters for Old West themed terrain
TREE_CLUSTERS: Tuple[int, int] = (3, 8)  # Min, max tree clusters
TREE_CLUSTER_SIZE: Tuple[int, int] = (2, 6)  # Min, max trees per cluster
WATER_FEATURES: Tuple[int, int] = (0, 2)  # Min, max water features (rivers/ponds)
WATER_SIZE: Tuple[int, int] = (3, 8)  # Min, max size of water features
ROCK_FORMATIONS: Tuple[int, int] = (2, 5)  # Min, max rock formations
CACTUS_PATCHES: Tuple[int, int] = (1, 4)  # Min, max cactus patches
BUILDING_RUINS: Tuple[int, int] = (0, 3)  # Min, max old building ruins