"""
Combat system and shooting mechanics
"""
import math
import random

from constants import (DAMAGE_MAX, DAMAGE_MIN, MAP_HEIGHT, MAP_WIDTH,
                       MAX_SHOOTING_RANGE, MIN_ACCURACY)


class CombatSystem:
    """Handles all combat-related mechanics"""

    @staticmethod
    def calculate_distance(x1, y1, x2, y2):
        """Calculate distance between two points"""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    @staticmethod
    def calculate_accuracy(
        distance, max_range=MAX_SHOOTING_RANGE, min_acc=MIN_ACCURACY
    ):
        """Calculate shooting accuracy based on distance"""
        if distance > max_range:
            return 0.0
        return max(min_acc, 1.0 - (distance / max_range) * 0.7)

    @staticmethod
    def calculate_damage():
        """Calculate random damage for a successful hit"""
        return random.randint(DAMAGE_MIN, DAMAGE_MAX)

    @staticmethod
    def get_bullet_path(game_map, start_x, start_y, target_x, target_y):
        """Get the path a bullet would travel and where it stops"""
        bullet_path = game_map.get_line_path(start_x, start_y, target_x, target_y)
        bullet_end_x, bullet_end_y = target_x, target_y

        # Find where bullet actually stops (wall or target)
        for x, y in bullet_path[1:]:  # Skip shooter's position
            if game_map.blocks_bullets(x, y):
                bullet_end_x, bullet_end_y = x, y
                break

        return bullet_path, bullet_end_x, bullet_end_y

    @classmethod
    def attempt_shot_with_weapon_and_bonus(
        cls, shooter, target, game_map, weapon_stats, bonus_manager=None
    ):
        """
        Attempt a shot from shooter to target using weapon stats and bonus effects
        """
        distance = cls.calculate_distance(shooter.x, shooter.y, target.x, target.y)
        bullet_path, bullet_end_x, bullet_end_y = cls.get_bullet_path(
            game_map, shooter.x, shooter.y, target.x, target.y
        )

        # Apply bonus modifications to weapon stats
        max_range = weapon_stats["max_range"]
        min_accuracy = weapon_stats["min_accuracy"]
        damage_min = weapon_stats["damage_min"]
        damage_max = weapon_stats["damage_max"]

        if bonus_manager:
            max_range = bonus_manager.modify_weapon_range(max_range)

        # Check if shot is out of range
        if distance > max_range:
            # Bullet falls short
            short_distance = int(max_range * 0.8)
            path_to_short = bullet_path[: min(short_distance, len(bullet_path))]
            if path_to_short:
                bullet_end_x, bullet_end_y = path_to_short[-1]

            return {
                "hit": False,
                "bullet_path": bullet_path,
                "bullet_end": (bullet_end_x, bullet_end_y),
                "damage": 0,
                "message": f"{shooter.name}'s {weapon_stats['name']} shot falls short!",
                "hit_target": False,
            }

        # Calculate if shot hits using weapon accuracy and bonus modifications
        base_accuracy = max(
            min_accuracy, 1.0 - (distance / max_range) * (1.0 - min_accuracy)
        )

        if bonus_manager:
            accuracy = bonus_manager.modify_accuracy(base_accuracy, distance, max_range)
        else:
            accuracy = base_accuracy

        hit_roll = random.random() < accuracy

        # Check if target position is blocked by walls
        target_blocked = game_map.blocks_bullets(bullet_end_x, bullet_end_y)

        if hit_roll and not target_blocked:
            # Calculate damage with bonus modifications
            base_damage = random.randint(damage_min, damage_max)

            # Check for critical hit
            is_critical = bonus_manager and bonus_manager.check_critical_hit()
            if is_critical:
                base_damage *= 2

            if bonus_manager:
                damage = bonus_manager.modify_damage(base_damage)
            else:
                damage = base_damage

            # Apply damage (with defensive bonuses for target)
            if hasattr(target, "bonus_manager") and target.bonus_manager:
                damage = target.bonus_manager.modify_damage_taken(damage)

            target_died = target.take_damage(damage)

            # Construct message
            crit_text = "CRITICAL HIT!" if is_critical else ""
            message = f"{shooter.name}'s {weapon_stats['name']} hits {target.name} for {damage} damage!{crit_text}"
            if target_died:
                message += f" {target.name} is dead!"

            return {
                "hit": True,
                "bullet_path": bullet_path,
                "bullet_end": (target.x, target.y),
                "damage": damage,
                "message": message,
                "hit_target": True,
                "target_died": target_died,
                "critical_hit": is_critical,
            }

        elif hit_roll and target_blocked:
            # Would have hit but blocked by terrain
            return {
                "hit": False,
                "bullet_path": bullet_path,
                "bullet_end": (bullet_end_x, bullet_end_y),
                "damage": 0,
                "message": f"{shooter.name}'s {weapon_stats['name']} shot hits cover!",
                "hit_target": False,
            }

        else:
            # Complete miss - bullet goes past target
            miss_end_x, miss_end_y = cls._calculate_miss_endpoint(
                bullet_path, bullet_end_x, bullet_end_y
            )

            return {
                "hit": False,
                "bullet_path": bullet_path,
                "bullet_end": (miss_end_x, miss_end_y),
                "damage": 0,
                "message": f"{shooter.name}'s {weapon_stats['name']} misses {target.name}!",
                "hit_target": False,
            }

    @classmethod
    def attempt_shot(cls, shooter, target, game_map):
        """
        Attempt a shot from shooter to target (uses default weapon stats)
        Returns: (hit_result, bullet_path, bullet_end, damage, message)
        """
        # Use default pistol stats for backwards compatibility
        default_weapon = WeaponStats.PISTOL
        return cls.attempt_shot_with_weapon_and_bonus(shooter, target, game_map, default_weapon)

    @staticmethod
    def _calculate_miss_endpoint(bullet_path, bullet_end_x, bullet_end_y):
        """Calculate where a missed bullet ends up"""
        if len(bullet_path) > 1:
            # Extend path a bit past target for miss effect
            dx = bullet_path[-1][0] - bullet_path[-2][0] if len(bullet_path) > 1 else 0
            dy = bullet_path[-1][1] - bullet_path[-2][1] if len(bullet_path) > 1 else 0
            extended_x = bullet_path[-1][0] + dx * 2
            extended_y = bullet_path[-1][1] + dy * 2

            # Make sure extended position is valid
            if 0 <= extended_x < MAP_WIDTH and 0 <= extended_y < MAP_HEIGHT:
                return extended_x, extended_y

        return bullet_end_x, bullet_end_y


class WeaponStats:
    """Define different weapon types and their stats"""

    PISTOL = {
        "name": "Pistol",
        "max_range": 12,
        "min_accuracy": 0.4,
        "damage_min": 20,
        "damage_max": 35,
    }

    RIFLE = {
        "name": "Rifle",
        "max_range": 20,
        "min_accuracy": 0.6,
        "damage_min": 35,
        "damage_max": 50,
    }

    SHOTGUN = {
        "name": "Shotgun",
        "max_range": 8,
        "min_accuracy": 0.8,
        "damage_min": 40,
        "damage_max": 60,
    }