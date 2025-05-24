#!/usr/bin/env python3
"""
Old West Gunfight - Main game file with enhanced font support

This module contains the main Game class that coordinates all game systems
including player input, entity management, combat resolution, and game state.
Enhanced with better font loading options for improved visual appearance.
"""

import random
import os
from typing import Optional, Tuple, Dict, Any, Union

import tcod

from ai import EnemyAI
from bonus_system import BonusManager, PlayerBonus
from combat import CombatSystem, WeaponStats
# Import our custom modules
from constants import (COLOR_ENEMY, COLOR_PLAYER, MAP_HEIGHT, MAP_WIDTH,
                       SCREEN_HEIGHT, SCREEN_WIDTH)
from entity import Enemy, Player
from game_map import GameMap
from renderer import Renderer


def load_font() -> tcod.tileset.Tileset:
    """Load the font
    
    Returns:
        A TCOD Tileset object with the loaded font
    """
    # Option 2: Try high-quality bitmap fonts
    bitmap_fonts = [
        ("dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD),  # Original fallback
        ("fonts/Hack-Regular.png", 32, 8, tcod.tileset.CHARMAP_CP437),
        ("fonts/dejavu12x12_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD),
        ("fonts/dejavu16x16_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD),
    ]
    
    for font_path, cols, rows, charmap in bitmap_fonts:
        if os.path.exists(font_path):
            try:
                print(f"Loading bitmap font: {font_path}")
                return tcod.tileset.load_tilesheet(font_path, cols, rows, charmap)
            except Exception as e:
                print(f"Failed to load {font_path}: {e}")
                continue
    

class Game:
    """Main game class that coordinates all systems.
    
    Manages game state, player input, AI turns, combat resolution,
    and coordinates between all game subsystems.
    """

    def __init__(self) -> None:
        """Initialize a new game instance with default state."""
        self.game_map: GameMap = GameMap(MAP_WIDTH, MAP_HEIGHT)
        self.player: Optional[Player] = None
        self.enemy: Optional[Enemy] = None
        self.enemy_ai: Optional[EnemyAI] = None
        self.combat_system: CombatSystem = CombatSystem()
        self.renderer: Optional[Renderer] = None
        self.game_over: bool = False
        self.winner: Optional[str] = None
        self.message: str = ""
        self.game_started: bool = False
        self.bonus_selected: bool = False
        self.weapon_selected: bool = False
        self.player_weapon: Optional[Dict[str, Union[str, int, float]]] = None
        self.player_bonus: Optional[Dict[str, Any]] = None
        self.bonus_manager: Optional[BonusManager] = None
        self.spawn_entities()

    def spawn_entities(self) -> None:
        """Spawn player and enemy entities at valid positions on the map.
        
        Attempts to find optimal spawn positions with good separation,
        falls back to any valid positions if needed.
        """
        player_pos, enemy_pos = self.game_map.find_spawn_positions()

        if player_pos and enemy_pos:
            # Create player
            self.player = Player(player_pos[0], player_pos[1])
            self.player.color = COLOR_PLAYER

            # Create enemy
            self.enemy = Enemy(enemy_pos[0], enemy_pos[1])
            self.enemy.color = COLOR_ENEMY

            # Create AI for enemy
            self.enemy_ai = EnemyAI(self.enemy)
        else:
            # Fallback if spawn finding fails
            valid_positions = self.game_map.find_valid_positions()
            if len(valid_positions) >= 2:
                player_pos = valid_positions[0]
                enemy_pos = valid_positions[-1]

                self.player = Player(player_pos[0], player_pos[1])
                self.player.color = COLOR_PLAYER

                self.enemy = Enemy(enemy_pos[0], enemy_pos[1])
                self.enemy.color = COLOR_ENEMY

                self.enemy_ai = EnemyAI(self.enemy)

    def set_renderer(self, renderer: Renderer) -> None:
        """Set the renderer for this game instance.
        
        Args:
            renderer: Renderer instance to use for drawing the game
        """
        self.renderer = renderer

    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state for rendering and external access.
        
        Returns:
            Dictionary containing all relevant game state information
        """
        return {
            "game_map": self.game_map,
            "entities": [self.player, self.enemy],
            "player": self.player,
            "enemy": self.enemy,
            "message": self.message,
            "game_over": self.game_over,
            "winner": self.winner,
            "game_started": self.game_started,
            "bonus_selected": self.bonus_selected,
            "weapon_selected": self.weapon_selected,
            "player_weapon": self.player_weapon,
            "player_bonus": self.player_bonus,
            "bonus_manager": self.bonus_manager,
        }

    def select_bonus(self, bonus_choice: str) -> bool:
        """Select a bonus for the player based on input choice.
        
        Args:
            bonus_choice: String representing the bonus choice ("1"-"6")
            
        Returns:
            True if bonus was successfully selected, False otherwise
        """
        bonus_map = {
            "1": "tough",
            "2": "longshot",
            "3": "quickdraw",
            "4": "eagle_eye",
            "5": "gunslinger",
            "6": "desperado",
        }

        if bonus_choice in bonus_map:
            bonus_id = bonus_map[bonus_choice]
            self.player_bonus = PlayerBonus.get_bonus_by_id(bonus_id)
            self.bonus_manager = BonusManager(self.player_bonus)

            # Apply bonus to player immediately
            if self.player:
                self.bonus_manager.apply_bonus_to_player(self.player)

            self.bonus_selected = True
            self.message = (
                f"You selected {self.player_bonus['name']}. Choose your weapon!"
            )
            return True
        return False

    def select_weapon(self, weapon_choice: str) -> bool:
        """Select a weapon for the player based on input choice.
        
        Args:
            weapon_choice: String representing the weapon choice ("1"-"3")
            
        Returns:
            True if weapon was successfully selected, False otherwise
        """
        weapons = {
            "1": WeaponStats.PISTOL,
            "2": WeaponStats.RIFLE,
            "3": WeaponStats.SHOTGUN,
        }

        if weapon_choice in weapons:
            self.player_weapon = weapons[weapon_choice]
            self.weapon_selected = True
            self.game_started = True
            self.message = (
                f"You selected the {self.player_weapon['name']}. The duel begins!"
            )
            return True
        return False

    def handle_input(self, key: tcod.event.KeyDown) -> Optional[str]:
        """Handle player keyboard input for all game phases.
        
        Args:
            key: TCOD KeyDown event containing the pressed key
            
        Returns:
            "exit" if player wants to quit, None otherwise
        """
        # Bonus selection phase
        if not self.bonus_selected:
            if key.sym == tcod.event.KeySym.ESCAPE:
                return "exit"
            elif key.sym == tcod.event.KeySym.N1:
                self.select_bonus("1")
            elif key.sym == tcod.event.KeySym.N2:
                self.select_bonus("2")
            elif key.sym == tcod.event.KeySym.N3:
                self.select_bonus("3")
            elif key.sym == tcod.event.KeySym.N4:
                self.select_bonus("4")
            elif key.sym == tcod.event.KeySym.N5:
                self.select_bonus("5")
            elif key.sym == tcod.event.KeySym.N6:
                self.select_bonus("6")
            return None

        # Weapon selection phase
        if not self.weapon_selected:
            if key.sym == tcod.event.KeySym.ESCAPE:
                return "exit"
            elif key.sym == tcod.event.KeySym.N1:
                self.select_weapon("1")
            elif key.sym == tcod.event.KeySym.N2:
                self.select_weapon("2")
            elif key.sym == tcod.event.KeySym.N3:
                self.select_weapon("3")
            return None

        # Game over phase
        if self.game_over:
            if key.sym == tcod.event.KeySym.ESCAPE:
                return "exit"
            elif key.sym == tcod.event.KeySym.r:
                self.restart_game()
            return None

        # Main game phase
        if key.sym == tcod.event.KeySym.ESCAPE:
            return "exit"

        player_moved = False

        # Movement
        if key.sym == tcod.event.KeySym.UP:
            if self.player.move(0, -1, self.game_map):
                player_moved = True
        elif key.sym == tcod.event.KeySym.DOWN:
            if self.player.move(0, 1, self.game_map):
                player_moved = True
        elif key.sym == tcod.event.KeySym.LEFT:
            if self.player.move(-1, 0, self.game_map):
                player_moved = True
        elif key.sym == tcod.event.KeySym.RIGHT:
            if self.player.move(1, 0, self.game_map):
                player_moved = True
        elif key.sym == tcod.event.KeySym.f:
            # Fire at enemy
            if self.enemy.alive:
                self.handle_player_shoot()
                player_moved = True

        # Enemy turn
        if player_moved and not self.game_over:
            self.handle_enemy_turn()

        return None

    def handle_player_shoot(self) -> None:
        """Handle player shooting action with selected weapon and bonus effects."""
        shot_result = self.combat_system.attempt_shot_with_weapon_and_bonus(
            self.player,
            self.enemy,
            self.game_map,
            self.player_weapon,
            self.bonus_manager,
        )

        # Animate the bullet
        if self.renderer:
            self.renderer.animate_bullet(
                self.player.x,
                self.player.y,
                shot_result["bullet_end"][0],
                shot_result["bullet_end"][1],
                self.game_map,
                self.get_game_state(),
                hit_target=shot_result["hit_target"],
            )

        self.message = shot_result["message"]

        # Check if enemy died
        if shot_result.get("target_died", False):
            self.game_over = True
            self.winner = self.player.name

    def handle_enemy_turn(self) -> None:
        """Handle enemy AI turn including movement and shooting decisions."""
        if not self.enemy.alive:
            return

        action_type, action_data, ai_message = self.enemy_ai.take_turn(
            self.player, self.game_map, self.combat_system
        )

        if action_type == "shoot":
            shot_result = action_data

            # Animate enemy bullet
            if self.renderer:
                self.renderer.animate_bullet(
                    self.enemy.x,
                    self.enemy.y,
                    shot_result["bullet_end"][0],
                    shot_result["bullet_end"][1],
                    self.game_map,
                    self.get_game_state(),
                    hit_target=shot_result["hit_target"],
                )

            # Check if player died
            if shot_result.get("target_died", False):
                self.game_over = True
                self.winner = self.enemy.name

        self.message = ai_message

    def restart_game(self) -> None:
        """Restart the game by reinitializing all components."""
        self.__init__()


def main() -> None:
    """Main function to run the game.
    
    Initializes TCOD context with enhanced font loading, creates game and 
    renderer instances, and runs the main game loop handling events and rendering.
    """
    # Load the best available font
    tileset = load_font()
    
    # Initialize tcod context with enhanced settings
    with tcod.context.new(
        columns=SCREEN_WIDTH,
        rows=SCREEN_HEIGHT + 12,  # Extra space for UI
        tileset=tileset,
        title="Old West Gunfight - Enhanced Edition",
        vsync=True,
        # Enable integer scaling for crisp pixel fonts
        renderer=tcod.context.RENDERER_SDL2,  # SDL2 renderer for better performance
    ) as context:
        # Create console and game
        console = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT + 12)
        game = Game()
        # Create renderer and link it to the game
        renderer = Renderer(console, context)
        game.set_renderer(renderer)
        
        print("Game started! Controls:")
        print("- Arrow keys: Move")
        print("- F: Fire weapon")
        print("- ESC: Quit")
        print("- R: Restart (when game over)")
        
        # Main game loop
        while True:
            # Render the current frame
            game_state = game.get_game_state()
            renderer.render_game(game_state)
            renderer.present()
            # Handle events
            for event in tcod.event.wait():
                if event.type == "QUIT":
                    return
                elif event.type == "KEYDOWN":
                    result = game.handle_input(event)
                    if result == "exit":
                        return


if __name__ == "__main__":
    main()