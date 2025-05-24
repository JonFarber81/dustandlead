"""
Player bonus system for character customization
"""
from constants import (BONUS_DESPERADO_DAMAGE_DEALT_MULTIPLIER,
                       BONUS_DESPERADO_DAMAGE_TAKEN_MULTIPLIER,
                       BONUS_EAGLE_EYE_ACCURACY_BONUS,
                       BONUS_GUNSLINGER_CRIT_CHANCE,
                       BONUS_LONGSHOT_ACCURACY_PENALTY,
                       BONUS_LONGSHOT_RANGE_MULTIPLIER,
                       BONUS_QUICKDRAW_DAMAGE_BONUS, BONUS_TOUGH_HP)


class PlayerBonus:
    """Defines different player bonuses and their effects"""

    TOUGH = {
        "id": "tough",
        "name": "TOUGH",
        "description": "Years of hard living have made you resilient",
        "effects": [
            f"+{BONUS_TOUGH_HP} Health Points",
            "Better survival in prolonged fights",
        ],
        "stats": {"bonus_hp": BONUS_TOUGH_HP},
    }

    LONGSHOT = {
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

    QUICKDRAW = {
        "id": "quickdraw",
        "name": "QUICKDRAW",
        "description": "Lightning fast on the draw, your shots hit harder",
        "effects": [
            f"+{BONUS_QUICKDRAW_DAMAGE_BONUS} damage to all shots",
            "Devastating opening moves",
        ],
        "stats": {"damage_bonus": BONUS_QUICKDRAW_DAMAGE_BONUS},
    }

    EAGLE_EYE = {
        "id": "eagle_eye",
        "name": "EAGLE EYE",
        "description": "Your aim is legendary across the frontier",
        "effects": [
            f"+{int(BONUS_EAGLE_EYE_ACCURACY_BONUS * 100)}% accuracy at all ranges",
            "More reliable shots",
        ],
        "stats": {"accuracy_bonus": BONUS_EAGLE_EYE_ACCURACY_BONUS},
    }

    GUNSLINGER = {
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

    DESPERADO = {
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
    def get_all_bonuses():
        """Get list of all available bonuses"""
        return [
            PlayerBonus.TOUGH,
            PlayerBonus.LONGSHOT,
            PlayerBonus.QUICKDRAW,
            PlayerBonus.EAGLE_EYE,
            PlayerBonus.GUNSLINGER,
            PlayerBonus.DESPERADO,
        ]

    @staticmethod
    def get_bonus_by_id(bonus_id):
        """Get bonus data by ID"""
        all_bonuses = PlayerBonus.get_all_bonuses()
        for bonus in all_bonuses:
            if bonus["id"] == bonus_id:
                return bonus
        return None


class BonusManager:
    """Manages bonus effects during gameplay"""

    def __init__(self, bonus_data=None):
        self.bonus = bonus_data
        self.stats = bonus_data["stats"] if bonus_data else {}

    def apply_bonus_to_player(self, player):
        """Apply bonus effects to player entity"""
        if not self.bonus:
            return

        # Apply health bonus
        if "bonus_hp" in self.stats:
            bonus_hp = self.stats["bonus_hp"]
            player.max_hp += bonus_hp
            player.hp += bonus_hp

    def modify_weapon_range(self, base_range):
        """Modify weapon range based on bonus"""
        if "range_multiplier" in self.stats:
            return int(base_range * self.stats["range_multiplier"])
        return base_range

    def modify_accuracy(self, base_accuracy, distance, max_range):
        """Modify accuracy based on bonus"""
        accuracy = base_accuracy

        # Eagle Eye bonus
        if "accuracy_bonus" in self.stats:
            accuracy += self.stats["accuracy_bonus"]

        # Long Shot penalty at extended range
        if "long_range_accuracy_penalty" in self.stats:
            original_max_range = max_range / self.stats.get("range_multiplier", 1.0)
            if distance > original_max_range:
                accuracy -= self.stats["long_range_accuracy_penalty"]

        return max(0.05, min(0.95, accuracy))  # Cap between 5% and 95%

    def modify_damage(self, base_damage):
        """Modify damage based on bonus"""
        damage = base_damage

        # Quickdraw damage bonus
        if "damage_bonus" in self.stats:
            damage += self.stats["damage_bonus"]

        # Desperado damage multiplier
        if "damage_dealt_multiplier" in self.stats:
            damage = int(damage * self.stats["damage_dealt_multiplier"])

        return damage

    def modify_damage_taken(self, base_damage):
        """Modify damage taken based on bonus"""
        damage = base_damage

        # Desperado takes more damage
        if "damage_taken_multiplier" in self.stats:
            damage = int(damage * self.stats["damage_taken_multiplier"])

        return damage

    def check_critical_hit(self):
        """Check if attack is a critical hit"""
        if "crit_chance" in self.stats:
            import random

            return random.random() < self.stats["crit_chance"]
        return False

    def get_bonus_description(self):
        """Get description of current bonus for UI"""
        if not self.bonus:
            return "No bonus selected"
        return f"{self.bonus['name']}: {self.bonus['description']}"
