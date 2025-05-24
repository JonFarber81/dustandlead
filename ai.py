"""
AI system for enemy behavior

This module contains the AI controller that manages enemy decision-making,
including movement tactics, shooting decisions, and behavioral patterns.
"""
import random
from typing import Tuple, List, Optional, Any

from constants import MAX_SHOOTING_RANGE


class EnemyAI:
    """AI controller for enemy entities.
    
    Manages enemy decision-making including when to shoot, how to move,
    and tactical positioning relative to the player and terrain.
    """

    def __init__(self, enemy_entity: Any) -> None:
        """Initialize the AI controller for a specific enemy entity.
        
        Args:
            enemy_entity: The enemy entity this AI will control
        """
        self.enemy: Any = enemy_entity
        self.aggression: float = 0.7  # How likely to attack vs move (0.0 to 1.0)
        self.last_player_position: Optional[Tuple[int, int]] = None

    def take_turn(
        self, 
        player: Any, 
        game_map: Any, 
        combat_system: Any
    ) -> Tuple[str, Any, str]:
        """Decide what the enemy should do this turn.
        
        Evaluates the current tactical situation and decides between shooting,
        moving, or waiting based on distance, line of sight, and AI personality.
        
        Args:
            player: Player entity to target/track
            game_map: GameMap instance for terrain and line of sight
            combat_system: CombatSystem for handling shooting attempts
            
        Returns:
            Tuple containing:
                - action_type: String describing action taken ("shoot", "move", "wait", "dead")
                - action_data: Data related to the action (shot result, movement, etc.)
                - message: String message describing what happened
        """
        if not self.enemy.alive:
            return "dead", None, ""

        distance = self.enemy.distance_to(player)
        has_line_of_sight = game_map.line_of_sight(
            self.enemy.x, self.enemy.y, player.x, player.y
        )

        # Remember where we last saw the player for tactical tracking
        if has_line_of_sight:
            self.last_player_position = (player.x, player.y)

        # Decide between shooting and moving based on tactical situation
        if self._should_shoot(distance, has_line_of_sight):
            return self._attempt_shoot(player, game_map, combat_system)
        else:
            return self._attempt_move(player, game_map)

    def _should_shoot(self, distance: float, has_line_of_sight: bool) -> bool:
        """Decide if enemy should shoot this turn based on tactical factors.
        
        Args:
            distance: Distance to player in tiles
            has_line_of_sight: Whether enemy can see the player
            
        Returns:
            True if enemy should attempt to shoot, False otherwise
        """
        if distance > MAX_SHOOTING_RANGE:
            return False
        if not has_line_of_sight:
            return False

        # Add some randomness to AI behavior based on aggression level
        shoot_chance = self.aggression

        # More likely to shoot at close range (tactical pressure)
        if distance < MAX_SHOOTING_RANGE * 0.5:
            shoot_chance += 0.2

        return random.random() < shoot_chance

    def _attempt_shoot(
        self, 
        player: Any, 
        game_map: Any, 
        combat_system: Any
    ) -> Tuple[str, Any, str]:
        """Attempt to shoot at the player.
        
        Args:
            player: Player entity to shoot at
            game_map: GameMap instance for terrain collision
            combat_system: CombatSystem for handling the shot
            
        Returns:
            Tuple of ("shoot", shot_result_dict, message_string)
        """
        shot_result = combat_system.attempt_shot(self.enemy, player, game_map)
        return "shoot", shot_result, shot_result["message"]

    def _attempt_move(self, player: Any, game_map: Any) -> Tuple[str, Any, str]:
        """Attempt to move towards the player or last known position.
        
        Uses tactical movement including trying alternative paths when
        the direct route is blocked by terrain.
        
        Args:
            player: Player entity to move towards
            game_map: GameMap instance for collision detection
            
        Returns:
            Tuple of ("move"/"wait", movement_data, message_string)
        """
        target_x, target_y = self._get_movement_target(player, game_map)
        dx, dy = self._calculate_movement_direction(target_x, target_y)

        # Try to move in the calculated direction
        if self.enemy.move(dx, dy, game_map):
            return "move", (dx, dy), f"{self.enemy.name} moves closer..."
        else:
            # If direct path is blocked, try alternative moves
            alternative_moves = self._get_alternative_moves(dx, dy)
            for alt_dx, alt_dy in alternative_moves:
                if self.enemy.move(alt_dx, alt_dy, game_map):
                    return (
                        "move",
                        (alt_dx, alt_dy),
                        f"{self.enemy.name} moves around cover...",
                    )

            # If no movement possible, just wait/taunt
            taunts = [
                f"{self.enemy.name} looks for an opening...",
                f"{self.enemy.name} takes cover!",
                f"{self.enemy.name} reloads...",
                f"{self.enemy.name} waits...",
            ]
            return "wait", None, random.choice(taunts)

    def _get_movement_target(self, player: Any, game_map: Any) -> Tuple[int, int]:
        """Get the position the enemy should move towards.
        
        Uses last known player position if line of sight is lost,
        providing more intelligent tracking behavior.
        
        Args:
            player: Player entity to target
            game_map: GameMap instance for line of sight calculation
            
        Returns:
            Tuple of (target_x, target_y) coordinates to move towards
        """
        # If we can see the player, move towards them
        has_line_of_sight = game_map.line_of_sight(
            self.enemy.x, self.enemy.y, player.x, player.y
        )

        if has_line_of_sight:
            return player.x, player.y
        elif self.last_player_position:
            return self.last_player_position
        else:
            # No idea where player is, move towards current player position as fallback
            return player.x, player.y

    def _calculate_movement_direction(self, target_x: int, target_y: int) -> Tuple[int, int]:
        """Calculate the best movement direction towards target.
        
        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            
        Returns:
            Tuple of (dx, dy) movement direction (-1, 0, or 1 for each axis)
        """
        dx = 0
        dy = 0

        if target_x > self.enemy.x:
            dx = 1
        elif target_x < self.enemy.x:
            dx = -1

        if target_y > self.enemy.y:
            dy = 1
        elif target_y < self.enemy.y:
            dy = -1

        return dx, dy

    def _get_alternative_moves(self, preferred_dx: int, preferred_dy: int) -> List[Tuple[int, int]]:
        """Get alternative movement options if preferred direction is blocked.
        
        Provides tactical movement alternatives when the direct path is blocked,
        including diagonal alternatives and random fallback moves.
        
        Args:
            preferred_dx: Preferred X direction (-1, 0, or 1)
            preferred_dy: Preferred Y direction (-1, 0, or 1)
            
        Returns:
            List of (dx, dy) tuples representing alternative movement options
        """
        alternatives = []

        # Try diagonal moves if moving straight
        if preferred_dx == 0:  # Moving vertically
            alternatives = [(-1, preferred_dy), (1, preferred_dy)]
        elif preferred_dy == 0:  # Moving horizontally
            alternatives = [(preferred_dx, -1), (preferred_dx, 1)]
        else:  # Moving diagonally, try straight moves
            alternatives = [(preferred_dx, 0), (0, preferred_dy)]

        # Add some random movement as last resort
        all_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1),
        ]
        random.shuffle(all_moves)
        alternatives.extend(all_moves)

        return alternatives

    def set_aggression(self, aggression_level: float) -> None:
        """Set how aggressive this enemy is in combat.
        
        Args:
            aggression_level: Aggression value from 0.0 (defensive) to 1.0 (very aggressive)
        """
        self.aggression = max(0.0, min(1.0, aggression_level))