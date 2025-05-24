"""
Rendering system for the game
"""

import time

import tcod

from constants import (BULLET_ANIMATION_DELAY, COLOR_BLOOD, COLOR_BUILDING,
                       COLOR_BULLET, COLOR_CACTUS, COLOR_ENEMY, COLOR_FLOOR,
                       COLOR_PLAYER, COLOR_ROCK, COLOR_TREE, COLOR_WALL,
                       COLOR_WATER, HIT_ANIMATION_DELAY,
                       IMPACT_ANIMATION_DELAY, MAP_HEIGHT, MAP_WIDTH,
                       SCREEN_WIDTH)
from game_map import TerrainType


class Renderer:
    """Handles all rendering and animations"""

    def __init__(self, console, context):
        self.console = console
        self.context = context

    def render_game(self, game_state, **kwargs):
        """Main render method for the game"""
        self.console.clear()

        # Show bonus selection screen
        if not game_state.get("bonus_selected", True):
            self._render_bonus_selection()
            return

        # Show weapon selection screen
        if not game_state.get("weapon_selected", True):
            self._render_weapon_selection()
            return

        # Render map
        self._render_map(game_state["game_map"])

        # Render entities
        self._render_entities(game_state["entities"])

        # Render special effects
        if kwargs.get("show_bullet"):
            self._render_bullet(kwargs["bullet_x"], kwargs["bullet_y"])

        if kwargs.get("show_impact"):
            self._render_impact(
                kwargs["impact_x"],
                kwargs["impact_y"],
                kwargs.get("hit_character", False),
            )

        # Render UI
        self._render_ui(game_state)

    def _render_bonus_selection(self):
        """Render the bonus selection screen"""
        from bonus_system import PlayerBonus

        title = "=== CHOOSE YOUR GUNSLINGER BONUS ==="
        self.console.print((SCREEN_WIDTH - len(title)) // 2, 8, title, (255, 255, 0))

        subtitle = "Select your character's special ability:"
        self.console.print(
            (SCREEN_WIDTH - len(subtitle)) // 2, 10, subtitle, (255, 255, 255)
        )

        bonuses = PlayerBonus.get_all_bonuses()
        start_y = 13

        for i, bonus in enumerate(bonuses, 1):
            # Bonus name and number
            bonus_line = f"{i}. {bonus['name']}"
            self.console.print(5, start_y + (i - 1) * 4, bonus_line, (173, 216, 230))

            # Description
            self.console.print(
                8, start_y + (i - 1) * 4 + 1, bonus["description"], (211, 211, 211)
            )

            # Effects
            effects_text = " | ".join(bonus["effects"])
            if len(effects_text) > 70:  # Wrap long text
                effects_text = effects_text[:67] + "..."
            self.console.print(
                8, start_y + (i - 1) * 4 + 2, effects_text, (144, 238, 144)
            )

        # Instructions
        instructions = ["", "Press 1-6 to select your bonus", "Press ESC to quit"]

        for i, instruction in enumerate(instructions):
            color = (
                (255, 255, 0) if instruction.startswith("Press") else (255, 255, 255)
            )
            self.console.print(
                (SCREEN_WIDTH - len(instruction)) // 2,
                start_y + 25 + i,
                instruction,
                color,
            )

    def _render_weapon_selection(self):
        """Render the weapon selection screen"""
        title = "=== CHOOSE YOUR WEAPON ==="
        self.console.print((SCREEN_WIDTH - len(title)) // 2, 10, title, (255, 255, 0))

        weapons_info = [
            "1. PISTOL",
            "   - Range: 12 tiles",
            "   - Accuracy: Good (40% minimum)",
            "   - Damage: 20-35",
            "   - Best for: Balanced combat",
            "",
            "2. RIFLE",
            "   - Range: 20 tiles",
            "   - Accuracy: Excellent (60% minimum)",
            "   - Damage: 35-50",
            "   - Best for: Long range precision",
            "",
            "3. SHOTGUN",
            "   - Range: 8 tiles",
            "   - Accuracy: Outstanding (80% minimum)",
            "   - Damage: 40-60",
            "   - Best for: Close quarters devastation",
            "",
            "Press 1, 2, or 3 to select your weapon",
            "Press ESC to quit",
        ]

        start_y = 15
        for i, line in enumerate(weapons_info):
            color = (255, 255, 255)
            if line.startswith(("1.", "2.", "3.")):
                color = (63, 63, 255)
            elif line.startswith("   - Best for:"):
                color = (63, 255, 63)
            elif line.startswith("Press"):
                color = (255, 255, 0)

            self.console.print(
                (SCREEN_WIDTH - len(line)) // 2, start_y + i, line, color
            )

    def _render_map(self, game_map):
        """Render the game map with different terrain types"""
        terrain_symbols = {
            TerrainType.FLOOR: (".", COLOR_FLOOR),
            TerrainType.WALL: ("#", COLOR_WALL),
            TerrainType.TREE: ("♣", COLOR_TREE),  # Tree symbol
            TerrainType.WATER: ("~", COLOR_WATER),  # Water symbol
            TerrainType.ROCK: ("o", COLOR_ROCK),  # Rock symbol
            TerrainType.CACTUS: ("i", COLOR_CACTUS),  # Cactus symbol
            TerrainType.BUILDING: ("▓", COLOR_BUILDING),  # Building ruins symbol
        }

        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                terrain_type = game_map.get_terrain_type(x, y)
                symbol, color = terrain_symbols.get(terrain_type, (".", COLOR_FLOOR))
                self.console.print(x, y, symbol, color)

    def _render_entities(self, entities):
        """Render all game entities"""
        for entity in entities:
            if entity.alive:
                color = COLOR_PLAYER if entity.name == "Player" else COLOR_ENEMY
                self.console.print(entity.x, entity.y, entity.char, color)
            else:
                self.console.print(entity.x, entity.y, "%", COLOR_BLOOD)

    def _render_bullet(self, x, y):
        """Render a bullet during animation"""
        self.console.print(x, y, "*", COLOR_BULLET)

    def _render_impact(self, x, y, hit_character=False):
        """Render impact effects"""
        if hit_character:
            self.console.print(x, y, "X", (255, 100, 100))  # light red
        else:
            self.console.print(x, y, "*", (255, 165, 0))  # orange

    def _render_ui(self, game_state):
        """Render the user interface"""
        player = game_state["player"]
        enemy = game_state["enemy"]
        message = game_state.get("message", "")
        game_over = game_state.get("game_over", False)
        winner = game_state.get("winner", None)
        player_weapon = game_state.get("player_weapon", None)
        player_bonus = game_state.get("player_bonus", None)
        bonus_manager = game_state.get("bonus_manager", None)

        # Health displays
        self.console.print(
            1, MAP_HEIGHT + 1, f"Player HP: {player.hp}/{player.max_hp}", COLOR_PLAYER
        )
        self.console.print(
            1, MAP_HEIGHT + 2, f"Enemy HP: {enemy.hp}/{enemy.max_hp}", COLOR_ENEMY
        )

        # Bonus info
        if player_bonus:
            bonus_info = f"Bonus: {player_bonus['name']}"
            self.console.print(1, MAP_HEIGHT + 3, bonus_info, (255, 0, 255))  # magenta

        # Weapon info
        if player_weapon:
            # Get modified weapon stats
            base_range = player_weapon["max_range"]
            actual_range = (
                bonus_manager.modify_weapon_range(base_range)
                if bonus_manager
                else base_range
            )

            weapon_info = f"Weapon: {player_weapon['name']} (Range: {actual_range}, Damage: {player_weapon['damage_min']}-{player_weapon['damage_max']})"
            if actual_range != base_range:
                weapon_info += f" [Modified from {base_range}]"

            self.console.print(1, MAP_HEIGHT + 4, weapon_info, (0, 255, 255))  # cyan

        # Controls
        self.console.print(
            1,
            MAP_HEIGHT + 5,
            "Arrow keys: Move | F: Fire | ESC: Quit",
            (255, 255, 255),  # white
        )

        # Game message
        if message:
            # Color critical hits differently
            message_color = (
                (255, 100, 100) if "CRITICAL HIT" in message else (255, 255, 0)
            )  # light red or yellow
            self.console.print(1, MAP_HEIGHT + 7, message, message_color)

        # Game over screen
        if game_over:
            game_over_text = f"GAME OVER - {winner} wins!"
            self.console.print(1, MAP_HEIGHT + 9, game_over_text, (255, 0, 0))  # red
            self.console.print(
                1,
                MAP_HEIGHT + 10,
                "Press R to restart or ESC to quit",
                (255, 255, 255),  # white
            )

    def animate_bullet(
        self, start_x, start_y, end_x, end_y, game_map, game_state, hit_target=False
    ):
        """Animate a bullet traveling from start to end position"""
        # Get the path the bullet travels
        bullet_path = game_map.get_line_path(start_x, start_y, end_x, end_y)

        for i, (x, y) in enumerate(bullet_path[1:], 1):  # Skip starting position
            # Clear and redraw everything with bullet
            self.render_game(game_state, show_bullet=True, bullet_x=x, bullet_y=y)
            self.context.present(self.console)
            time.sleep(BULLET_ANIMATION_DELAY)

            # Check if bullet hits terrain that blocks bullets
            if game_map.blocks_bullets(x, y):
                # Show impact on blocking terrain
                self._show_impact_effect(x, y, game_state, hit_character=False)
                break

        # If we hit the target, show a brief hit effect
        if hit_target:
            self._show_impact_effect(end_x, end_y, game_state, hit_character=True)

    def _show_impact_effect(self, x, y, game_state, hit_character=False):
        """Show impact effect at specified location"""
        self.render_game(
            game_state,
            show_impact=True,
            impact_x=x,
            impact_y=y,
            hit_character=hit_character,
        )
        self.context.present(self.console)

        delay = HIT_ANIMATION_DELAY if hit_character else IMPACT_ANIMATION_DELAY
        time.sleep(delay)

    def present(self):
        """Present the rendered frame to screen"""
        self.context.present(self.console)
