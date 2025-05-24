"""
AI system for enemy behavior
"""
import random
from constants import MAX_SHOOTING_RANGE


class EnemyAI:
    """AI controller for enemy entities"""
    
    def __init__(self, enemy_entity):
        self.enemy = enemy_entity
        self.aggression = 0.7  # How likely to attack vs move
        self.last_player_position = None
        
    def take_turn(self, player, game_map, combat_system):
        """
        Decide what the enemy should do this turn
        Returns: (action_type, action_data, message)
        """
        if not self.enemy.alive:
            return "dead", None, ""
            
        distance = self.enemy.distance_to(player)
        has_line_of_sight = game_map.line_of_sight(
            self.enemy.x, self.enemy.y, player.x, player.y
        )
        
        # Remember where we last saw the player
        if has_line_of_sight:
            self.last_player_position = (player.x, player.y)
        
        # Decide between shooting and moving
        if self._should_shoot(distance, has_line_of_sight):
            return self._attempt_shoot(player, game_map, combat_system)
        else:
            return self._attempt_move(player, game_map)
    
    def _should_shoot(self, distance, has_line_of_sight):
        """Decide if enemy should shoot this turn"""
        if distance > MAX_SHOOTING_RANGE:
            return False
        if not has_line_of_sight:
            return False
        
        # Add some randomness to AI behavior
        shoot_chance = self.aggression
        
        # More likely to shoot at close range
        if distance < MAX_SHOOTING_RANGE * 0.5:
            shoot_chance += 0.2
            
        return random.random() < shoot_chance
    
    def _attempt_shoot(self, player, game_map, combat_system):
        """Attempt to shoot at the player"""
        shot_result = combat_system.attempt_shot(self.enemy, player, game_map)
        
        return "shoot", shot_result, shot_result['message']
    
    def _attempt_move(self, player, game_map):
        """Attempt to move towards the player or last known position"""
        target_x, target_y = self._get_movement_target(player, game_map)  # Pass game_map here
        dx, dy = self._calculate_movement_direction(target_x, target_y)
        
        # Try to move in the calculated direction
        if self.enemy.move(dx, dy, game_map):
            return "move", (dx, dy), f"{self.enemy.name} moves closer..."
        else:
            # If direct path is blocked, try alternative moves
            alternative_moves = self._get_alternative_moves(dx, dy)
            for alt_dx, alt_dy in alternative_moves:
                if self.enemy.move(alt_dx, alt_dy, game_map):
                    return "move", (alt_dx, alt_dy), f"{self.enemy.name} moves around cover..."
            
            # If no movement possible, just wait/taunt
            taunts = [
                f"{self.enemy.name} looks for an opening...",
                f"{self.enemy.name} takes cover!",
                f"{self.enemy.name} reloads...",
                f"{self.enemy.name} waits..."
            ]
            return "wait", None, random.choice(taunts)
    
    def _get_movement_target(self, player, game_map):
        """Get the position the enemy should move towards"""
        # If we can see the player, move towards them
        has_line_of_sight = game_map.line_of_sight(
            self.enemy.x, self.enemy.y, player.x, player.y
        )
        
        if has_line_of_sight:
            return player.x, player.y
        elif self.last_player_position:
            return self.last_player_position
        else:
            # No idea where player is, move randomly
            return player.x, player.y  # Default to current player position
    
    def _calculate_movement_direction(self, target_x, target_y):
        """Calculate the best movement direction towards target"""
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
    
    def _get_alternative_moves(self, preferred_dx, preferred_dy):
        """Get alternative movement options if preferred direction is blocked"""
        alternatives = []
        
        # Try diagonal moves if moving straight
        if preferred_dx == 0:  # Moving vertically
            alternatives = [(-1, preferred_dy), (1, preferred_dy)]
        elif preferred_dy == 0:  # Moving horizontally  
            alternatives = [(preferred_dx, -1), (preferred_dx, 1)]
        else:  # Moving diagonally
            alternatives = [(preferred_dx, 0), (0, preferred_dy)]
        
        # Add some random movement as last resort
        all_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        random.shuffle(all_moves)
        alternatives.extend(all_moves)
        
        return alternatives
    
    def set_aggression(self, aggression_level):
        """Set how aggressive this enemy is (0.0 to 1.0)"""
        self.aggression = max(0.0, min(1.0, aggression_level))