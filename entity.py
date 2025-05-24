"""
Entity classes for game objects

This module defines the base Entity class and specific entity types (Player, Enemy)
that represent interactive objects in the game world with position, health, and behavior.
"""
import math
from typing import Tuple, Optional, Any

from constants import ENEMY_MAX_HP, PLAYER_MAX_HP


class Entity:
    """Base class for all game entities (player, enemies, etc.).
    
    Provides common functionality for position management, health tracking,
    movement, and damage handling that all game entities share.
    """

    def __init__(
        self, 
        x: int, 
        y: int, 
        char: str, 
        color: Optional[Tuple[int, int, int]], 
        name: str, 
        hp: int = 100
    ) -> None:
        """Initialize a new entity with position, appearance, and health.
        
        Args:
            x: Initial X coordinate
            y: Initial Y coordinate
            char: Character symbol to display for this entity
            color: RGB color tuple for rendering, or None if set elsewhere
            name: Display name for this entity
            hp: Starting and maximum health points
        """
        self.x: int = x
        self.y: int = y
        self.char: str = char
        self.color: Optional[Tuple[int, int, int]] = color
        self.name: str = name
        self.hp: int = hp
        self.max_hp: int = hp
        self.alive: bool = True

    def move(self, dx: int, dy: int, game_map: Any) -> bool:
        """Move entity by dx, dy if the destination is not blocked.
        
        Args:
            dx: Change in X coordinate (-1, 0, or 1)
            dy: Change in Y coordinate (-1, 0, or 1)
            game_map: GameMap instance for collision detection
            
        Returns:
            True if movement was successful, False if blocked
        """
        if not game_map.is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def take_damage(self, damage: int) -> bool:
        """Apply damage to entity and check if it dies.
        
        Args:
            damage: Amount of damage to apply
            
        Returns:
            True if entity died from this damage, False if still alive
        """
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return not self.alive  # Return True if entity died

    def get_position(self) -> Tuple[int, int]:
        """Get entity position as a tuple.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self.y)

    def set_position(self, x: int, y: int) -> None:
        """Set entity position to specific coordinates.
        
        Args:
            x: New X coordinate
            y: New Y coordinate
        """
        self.x = x
        self.y = y

    def distance_to(self, other_entity: 'Entity') -> float:
        """Calculate Euclidean distance to another entity.
        
        Args:
            other_entity: Entity to calculate distance to
            
        Returns:
            Euclidean distance between this entity and the other entity
        """
        return math.sqrt(
            (other_entity.x - self.x) ** 2 + (other_entity.y - self.y) ** 2
        )


class Player(Entity):
    """Player entity with specific defaults for the player character.
    
    Represents the player-controlled character with appropriate starting
    health and display characteristics.
    """

    def __init__(self, x: int, y: int) -> None:
        """Initialize a new player entity.
        
        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
        """
        super().__init__(x, y, "@", None, "Player", PLAYER_MAX_HP)
        # Color will be set from constants in game logic


class Enemy(Entity):
    """Enemy entity with AI capabilities and specific defaults.
    
    Represents AI-controlled opponents with appropriate starting health
    and display characteristics for combat encounters.
    """

    def __init__(self, x: int, y: int, name: str = "Bandit") -> None:
        """Initialize a new enemy entity.
        
        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
            name: Display name for this enemy (defaults to "Bandit")
        """
        super().__init__(x, y, "B", None, name, ENEMY_MAX_HP)
        # Color will be set from constants in game logic

    def get_move_towards(self, target_entity: Entity) -> Tuple[int, int]:
        """Calculate movement direction towards target entity.
        
        Determines the optimal single-step movement direction to get
        closer to the specified target entity.
        
        Args:
            target_entity: Entity to move towards
            
        Returns:
            Tuple of (dx, dy) representing movement direction (-1, 0, or 1 for each axis)
        """
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