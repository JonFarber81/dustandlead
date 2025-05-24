"""
Player bonus system for character customization

This module provides the bonus system that allows players to customize their
character with special abilities that modify combat statistics and behavior.
"""
from typing import Dict, List, Optional, Any, Union
import random

from constants import (BONUS_DESPERADO_DAMAGE_DEALT_MULTIPLIER,
                       BONUS_DESPERADO_DAMAGE_TAKEN_MULTIPLIER,
                       BONUS_EAGLE_EYE_ACCURACY_BONUS,
                       BONUS_GUNSLINGER_CRIT_CHANCE,
                       BONUS_LONGSHOT_ACCURACY_PENALTY,
                       BONUS_LONGSHOT_RANGE_MULTIPLIER,
                       BONUS_QUICKDRAW_DAMAGE_BONUS, BONUS_TOUGH_HP)


class PlayerBonus:
    """Defines different player bonuses and their effects.
    
    Contains static bonus definitions that provide various gameplay modifications
    including health increases, accuracy changes, damage bonuses, and special abilities.
    """

    TOUGH: Dict[str, Union[str, List[str], Dict[str, Union[int, float]]]] = {
        "id": "tough",
        "name": "TOUGH",
        "description": "Years of hard living have made you resilient",
        "effects": [
            f"+{BONUS_TOUGH_HP} Health Points",
            "Better survival in prolonged fights",
        ],
        "stats": {"bonus_hp": BONUS_TOUGH_HP},
    }

    LONGSHOT: Dict[str, Union[str, List[str], Dict[str, Union[int, float]]]] = {
        "id": "longshot",
        "name": "LONG SHOT",
        "description": "You can make shots others wouldn't dare attempt",
        "effects": [
            f"+{int((BONUS_LONGSHOT_RANGE_MULTIPLIER - 1) * 100)}% shooting range",
            f"-{int(BONUS_LONGSHOT_ACCURACY_PENALTY * 100)}% accuracy at long range",
            "Risk vs reward gameplay",
        ],
        "stats": {
            "range_multiplier": BONUS_LONGSHOT_RANGE_MULTIPLIER,
            "long_range_accuracy_penalty": BONUS_LONGSHOT_ACCURACY_PENALTY,
        },
    }

    QUICKDRAW: Dict[str, Union[str, List[str], Dict[str, Union[int, float]]]] = {
        "id": "quickdraw",
        "name": "QUICKDRAW",
        "description": "Lightning fast on the draw, your shots hit harder",
        "effects": [
            f"+{BONUS_QUICKDRAW_DAMAGE_BONUS} damage to all shots",
            "Devastating opening moves",
        ],
        "stats": {"damage_bonus": BONUS_QUICKDRAW_DAMAGE_BONUS},
    }

    EAGLE_EYE: Dict[str, Union[str, List[str], Dict[str, Union[int, float]]]] = {
        "id": "eagle_eye",
        "name": "EAGLE EYE",
        "description": "Your aim is legendary across the frontier",
        "effects": [
            f"+{int(BONUS_EAGLE_EYE_ACCURACY_BONUS * 100)}% accuracy at all ranges",
            "More reliable shots",
        ],
        "stats": {"accuracy_bonus": BONUS_EAGLE_EYE_ACCURACY_BONUS},
    }

    GUNSLINGER: Dict[str, Union[str, List[str], Dict[str, Union[int, float]]]] = {
        "id": "gunslinger",
        "name": "GUNSLINGER",
        "description": "Sometimes luck favors the bold",
        "effects": [
            f"{int(BONUS_GUNSLINGER_CRIT_CHANCE * 100)}% chance for critical hits",
            "Critical hits deal double damage",
            "High risk, high reward",
        ],
        "stats": {"crit_chance": BONUS_GUNSLINGER_CRIT_CHANCE},
    }

    DESPERADO: Dict[str, Union[str, List[str], Dict[str, Union[int, float]]]] = {
        "id": "desperado",
        "name": "DESPERADO",
        "description": "Live fast, die hard - nothing left to lose",
        "effects": [
            f"+{int((BONUS_DESPERADO_DAMAGE_DEALT_MULTIPLIER - 1) * 100)}% damage dealt",
            f"+{int((BONUS_DESPERADO_DAMAGE_TAKEN_MULTIPLIER - 1) * 100)}% damage taken",
            "Glass cannon playstyle",
        ],
        "stats": {
            "damage_dealt_multiplier": BONUS_DESPERADO_DAMAGE_DEALT_MULTIPLIER,
            "damage_taken_multiplier": BONUS_DESPERADO_DAMAGE_TAKEN_MULTIPLIER,
        },
    }

    @staticmethod
    def get_all_bonuses() -> List[Dict[str, Union[str, List[str], Dict[str, Union[int, float]]]]]:
        """Get list of all available bonuses for selection screen.
        
        Returns:
            List of bonus dictionaries containing all available player bonuses
        """
        return [
            PlayerBonus.TOUGH,
            PlayerBonus.LONGSHOT,
            PlayerBonus.QUICKDRAW,
            PlayerBonus.EAGLE_EYE,
            PlayerBonus.GUNSLINGER,
            PlayerBonus.DESPERADO,
        ]

    @staticmethod
    def get_bonus_by_id(bonus_id: str) -> Optional[Dict[str, Union[str, List[str], Dict[str, Union[int, float]]]]]:
        """Get bonus data by its unique identifier.
        
        Args:
            bonus_id: String identifier for the desired bonus
            
        Returns:
            Bonus dictionary if found, None otherwise
        """
        all_bonuses = PlayerBonus.get_all_bonuses()
        for bonus in all_bonuses:
            if bonus["id"] == bonus_id:
                return bonus
        return None


class BonusManager:
    """Manages bonus effects during gameplay.
    
    Handles the application of bonus effects to combat calculations,
    player statistics, and special ability triggers during gameplay.
    """

    def __init__(self, bonus_data: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the bonus manager with optional bonus data.
        
        Args:
            bonus_data: Dictionary containing bonus information and stats
        """
        self.bonus: Optional[Dict[str, Any]] = bonus_data
        self.stats: Dict[str, Union[int, float]] = bonus_data["stats"] if bonus_data else {}

    def apply_bonus_to_player(self, player: Any) -> None:
        """Apply bonus effects to player entity (typically health increases).
        
        Args:
            player: Player entity to apply bonuses to
        """
        if not self.bonus:
            return

        # Apply health bonus
        if "bonus_hp" in self.stats:
            bonus_hp = int(self.stats["bonus_hp"])
            player.max_hp += bonus_hp
            player.hp += bonus_hp

    def modify_weapon_range(self, base_range: int) -> int:
        """Modify weapon range based on active bonus effects.
        
        Args:
            base_range: Base weapon range before bonuses
            
        Returns:
            Modified weapon range after applying bonus effects
        """
        if "range_multiplier" in self.stats:
            return int(base_range * self.stats["range_multiplier"])
        return base_range

    def modify_accuracy(self, base_accuracy: float, distance: float, max_range: int) -> float:
        """Modify shooting accuracy based on bonus effects and distance.
        
        Args:
            base_accuracy: Base accuracy before bonuses (0.0 to 1.0)
            distance: Distance to target
            max_range: Maximum weapon range (possibly modified by bonuses)
            
        Returns:
            Modified accuracy value capped between 0.05 and 0.95
        """
        accuracy = base_accuracy

        # Eagle Eye bonus - flat accuracy increase
        if "accuracy_bonus" in self.stats:
            accuracy += float(self.stats["accuracy_bonus"])

        # Long Shot penalty at extended range beyond original weapon range
        if "long_range_accuracy_penalty" in self.stats:
            original_max_range = max_range / self.stats.get("range_multiplier", 1.0)
            if distance > original_max_range:
                accuracy -= float(self.stats["long_range_accuracy_penalty"])

        return max(0.05, min(0.95, accuracy))  # Cap between 5% and 95%

    def modify_damage(self, base_damage: int) -> int:
        """Modify damage output based on active bonus effects.
        
        Args:
            base_damage: Base damage before bonuses
            
        Returns:
            Modified damage after applying bonus effects
        """
        damage = base_damage

        # Quickdraw damage bonus - flat damage increase
        if "damage_bonus" in self.stats:
            damage += int(self.stats["damage_bonus"])

        # Desperado damage multiplier - percentage increase
        if "damage_dealt_multiplier" in self.stats:
            damage = int(damage * self.stats["damage_dealt_multiplier"])

        return damage

    def modify_damage_taken(self, base_damage: int) -> int:
        """Modify damage taken based on defensive bonus effects.
        
        Args:
            base_damage: Base damage before defensive bonuses
            
        Returns:
            Modified damage after applying defensive bonus effects
        """
        damage = base_damage

        # Desperado takes more damage (glass cannon effect)
        if "damage_taken_multiplier" in self.stats:
            damage = int(damage * self.stats["damage_taken_multiplier"])

        return damage

    def check_critical_hit(self) -> bool:
        """Check if an attack should be a critical hit based on bonus effects.
        
        Returns:
            True if attack should be a critical hit, False otherwise
        """
        if "crit_chance" in self.stats:
            return random.random() < float(self.stats["crit_chance"])
        return False

    def get_bonus_description(self) -> str:
        """Get a formatted description of the current bonus for UI display.
        
        Returns:
            String description of active bonus, or default message if none
        """
        if not self.bonus:
            return "No bonus selected"
        return f"{self.bonus['name']}: {self.bonus['description']}"