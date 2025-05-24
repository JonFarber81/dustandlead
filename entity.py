"""
Entity classes for game objects
"""
from constants import ENEMY_MAX_HP, PLAYER_MAX_HP


class Entity:
    """Base class for all game entities (player, enemies, etc.)"""

    def __init__(self, x, y, char, color, name, hp=100):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.alive = True

    def move(self, dx, dy, game_map):
        """Move entity by dx, dy if the destination is not blocked"""
        if not game_map.is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def take_damage(self, damage):
        """Apply damage to entity and check if it dies"""
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return not self.alive  # Return True if entity died

    def get_position(self):
        """Get entity position as tuple"""
        return (self.x, self.y)

    def set_position(self, x, y):
        """Set entity position"""
        self.x = x
        self.y = y

    def distance_to(self, other_entity):
        """Calculate distance to another entity"""
        import math

        return math.sqrt(
            (other_entity.x - self.x) ** 2 + (other_entity.y - self.y) ** 2
        )


class Player(Entity):
    """Player entity with specific defaults"""

    def __init__(self, x, y):
        super().__init__(x, y, "@", None, "Player", PLAYER_MAX_HP)
        # Color will be set from constants in game logic


class Enemy(Entity):
    """Enemy entity with AI capabilities"""

    def __init__(self, x, y, name="Bandit"):
        super().__init__(x, y, "B", None, name, ENEMY_MAX_HP)
        # Color will be set from constants in game logic

    def get_move_towards(self, target_entity):
        """Calculate movement direction towards target"""
        dx = 0
        dy = 0

        if target_entity.x > self.x:
            dx = 1
        elif target_entity.x < self.x:
            dx = -1

        if target_entity.y > self.y:
            dy = 1
        elif target_entity.y < self.y:
            dy = -1

        return dx, dy
