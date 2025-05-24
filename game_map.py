"""
Game map generation and utilities

This module handles procedural map generation with Old West themed terrain,
collision detection, line of sight calculations, and pathfinding utilities.
"""
import random
from typing import List, Tuple, Optional, Set

import tcod

from constants import (BUILDING_RUINS, CACTUS_PATCHES, MAX_CLUSTER_SIZE,
                       MAX_WALL_CLUSTERS, MIN_CLUSTER_SIZE, MIN_WALL_CLUSTERS,
                       ROCK_FORMATIONS, TREE_CLUSTER_SIZE, TREE_CLUSTERS,
                       WATER_FEATURES, WATER_SIZE)


class TerrainType:
    """Enum-like class for different terrain types.
    
    Defines integer constants for all terrain types used in the game map.
    Each terrain type has different properties for movement and bullet blocking.
    """

    FLOOR: int = 0
    WALL: int = 1
    TREE: int = 2
    WATER: int = 3
    ROCK: int = 4
    CACTUS: int = 5
    BUILDING: int = 6


class GameMap:
    """Handles map generation, collision detection, and line of sight.
    
    Generates procedural Old West themed maps with various terrain features
    including natural elements (trees, water, rocks) and man-made structures.
    Provides utilities for collision detection, pathfinding, and line of sight.
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize a new game map with specified dimensions.
        
        Args:
            width: Map width in tiles
            height: Map height in tiles
        """
        self.width: int = width
        self.height: int = height
        # Use terrain types instead of just True/False
        self.tiles: List[List[int]] = [[TerrainType.FLOOR for _ in range(height)] for _ in range(width)]
        self.generate_old_west_map()

    def generate_old_west_map(self) -> None:
        """Generate an old west themed map with various terrain features.
        
        Creates a complete map with border walls, natural terrain features,
        and man-made structures in a thematic Old West style.
        """
        # Start with basic border walls
        self._create_border_walls()

        # Add natural terrain features
        self._add_water_features()
        self._add_tree_clusters()
        self._add_rock_formations()
        self._add_cactus_patches()

        # Add man-made structures
        self._add_building_ruins()
        self._add_cover_walls()

    def _create_border_walls(self) -> None:
        """Create walls around the map border to prevent entities from leaving."""
        for x in range(self.width):
            self.tiles[x][0] = TerrainType.WALL
            self.tiles[x][self.height - 1] = TerrainType.WALL
        for y in range(self.height):
            self.tiles[0][y] = TerrainType.WALL
            self.tiles[self.width - 1][y] = TerrainType.WALL

    def _add_water_features(self) -> None:
        """Add rivers, ponds, or streams to the map for natural obstacles."""
        num_features = random.randint(*WATER_FEATURES)

        for _ in range(num_features):
            if random.choice([True, False]):  # 50% chance river vs pond
                self._create_river()
            else:
                self._create_pond()

    def _create_river(self) -> None:
        """Create a winding river across the map.
        
        Rivers can be horizontal or vertical with some meandering for natural look.
        They block movement but not bullets (unlike walls).
        """
        # Choose river direction (horizontal or vertical)
        if random.choice([True, False]):
            # Horizontal river
            y_center = random.randint(self.height // 4, 3 * self.height // 4)
            for x in range(2, self.width - 2):
                # Add some meandering
                y_offset = random.randint(-2, 2)
                river_y = max(2, min(self.height - 3, y_center + y_offset))

                # Make river 1-3 tiles wide
                width = random.randint(1, 2)
                for dy in range(-width, width + 1):
                    wy = river_y + dy
                    if self.is_valid_position(x, wy):
                        self.tiles[x][wy] = TerrainType.WATER
        else:
            # Vertical river
            x_center = random.randint(self.width // 4, 3 * self.width // 4)
            for y in range(2, self.height - 2):
                x_offset = random.randint(-2, 2)
                river_x = max(2, min(self.width - 3, x_center + x_offset))

                width = random.randint(1, 2)
                for dx in range(-width, width + 1):
                    wx = river_x + dx
                    if self.is_valid_position(wx, y):
                        self.tiles[wx][y] = TerrainType.WATER

    def _create_pond(self) -> None:
        """Create a small pond or lake with roughly circular shape."""
        center_x = random.randint(5, self.width - 6)
        center_y = random.randint(5, self.height - 6)
        size = random.randint(*WATER_SIZE)

        # Create roughly circular pond
        for x in range(center_x - size // 2, center_x + size // 2 + 1):
            for y in range(center_y - size // 2, center_y + size // 2 + 1):
                if self.is_valid_position(x, y):
                    distance = abs(x - center_x) + abs(y - center_y)
                    if distance <= size // 2 + random.randint(-1, 1):
                        self.tiles[x][y] = TerrainType.WATER

    def _add_tree_clusters(self) -> None:
        """Add clusters of trees for cover and atmosphere.
        
        Trees provide both visual interest and tactical cover options.
        They block both movement and bullets.
        """
        num_clusters = random.randint(*TREE_CLUSTERS)

        for _ in range(num_clusters):
            cluster_x = random.randint(3, self.width - 4)
            cluster_y = random.randint(3, self.height - 4)
            cluster_size = random.randint(*TREE_CLUSTER_SIZE)

            for _ in range(cluster_size):
                # Place trees in a rough cluster pattern
                offset_x = random.randint(-3, 3)
                offset_y = random.randint(-3, 3)
                tree_x = cluster_x + offset_x
                tree_y = cluster_y + offset_y

                if (
                    self.is_valid_position(tree_x, tree_y)
                    and self.tiles[tree_x][tree_y] == TerrainType.FLOOR
                ):
                    self.tiles[tree_x][tree_y] = TerrainType.TREE

    def _add_rock_formations(self) -> None:
        """Add rocky outcroppings for cover.
        
        Rock formations provide solid cover that blocks both movement and bullets,
        similar to walls but more natural looking.
        """
        num_formations = random.randint(*ROCK_FORMATIONS)

        for _ in range(num_formations):
            center_x = random.randint(3, self.width - 4)
            center_y = random.randint(3, self.height - 4)
            formation_size = random.randint(2, 5)

            for _ in range(formation_size):
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
                rock_x = center_x + offset_x
                rock_y = center_y + offset_y

                if (
                    self.is_valid_position(rock_x, rock_y)
                    and self.tiles[rock_x][rock_y] == TerrainType.FLOOR
                ):
                    self.tiles[rock_x][rock_y] = TerrainType.ROCK

    def _add_cactus_patches(self) -> None:
        """Add desert cacti scattered around for atmosphere.
        
        Cacti block movement but not bullets, providing visual interest
        without significantly impacting combat dynamics.
        """
        num_patches = random.randint(*CACTUS_PATCHES)

        for _ in range(num_patches):
            patch_x = random.randint(2, self.width - 3)
            patch_y = random.randint(2, self.height - 3)
            patch_size = random.randint(1, 4)

            for _ in range(patch_size):
                offset_x = random.randint(-4, 4)
                offset_y = random.randint(-4, 4)
                cactus_x = patch_x + offset_x
                cactus_y = patch_y + offset_y

                if (
                    self.is_valid_position(cactus_x, cactus_y)
                    and self.tiles[cactus_x][cactus_y] == TerrainType.FLOOR
                ):
                    self.tiles[cactus_x][cactus_y] = TerrainType.CACTUS

    def _add_building_ruins(self) -> None:
        """Add ruins of old buildings for cover and atmosphere.
        
        Building ruins are partial structures that provide cover while
        maintaining the Old West theme of abandoned settlements.
        """
        num_ruins = random.randint(*BUILDING_RUINS)

        for _ in range(num_ruins):
            # Create small rectangular ruins
            ruin_x = random.randint(4, self.width - 8)
            ruin_y = random.randint(4, self.height - 8)
            width = random.randint(3, 6)
            height = random.randint(3, 5)

            # Create partial walls (ruins are broken)
            for x in range(ruin_x, ruin_x + width):
                for y in range(ruin_y, ruin_y + height):
                    if self.is_valid_position(x, y):
                        # Only place walls on the edges, and not all of them
                        is_edge = (
                            x == ruin_x
                            or x == ruin_x + width - 1
                            or y == ruin_y
                            or y == ruin_y + height - 1
                        )
                        if is_edge and random.random() < 0.7:  # 70% chance for wall
                            if self.tiles[x][y] == TerrainType.FLOOR:
                                self.tiles[x][y] = TerrainType.BUILDING

    def _add_cover_walls(self) -> None:
        """Add some traditional cover walls for tactical gameplay.
        
        Creates small clusters of wall tiles that provide reliable cover
        options for tactical combat positioning.
        """
        num_walls = random.randint(MIN_WALL_CLUSTERS, MAX_WALL_CLUSTERS)
        for _ in range(num_walls):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)

            # Create small wall clusters
            cluster_size = random.randint(MIN_CLUSTER_SIZE, MAX_CLUSTER_SIZE)
            for _ in range(cluster_size):
                if (
                    self.is_valid_position(x, y)
                    and self.tiles[x][y] == TerrainType.FLOOR
                ):
                    self.tiles[x][y] = TerrainType.WALL
                x += random.randint(-1, 1)
                y += random.randint(-1, 1)

    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is within map bounds.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            True if position is within map bounds, False otherwise
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def is_blocked(self, x: int, y: int) -> bool:
        """Check if a position is blocked for movement.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            True if position blocks movement, False otherwise
        """
        if not self.is_valid_position(x, y):
            return True

        # All solid terrain types block movement
        blocking_terrain: Set[int] = {
            TerrainType.WALL,
            TerrainType.TREE,
            TerrainType.WATER,
            TerrainType.ROCK,
            TerrainType.BUILDING,
        }
        return self.tiles[x][y] in blocking_terrain

    def blocks_bullets(self, x: int, y: int) -> bool:
        """Check if a position blocks bullets (different from movement blocking).
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            True if position blocks bullets, False otherwise
        """
        if not self.is_valid_position(x, y):
            return True

        # Cacti don't block bullets, but other terrain does
        bullet_blocking: Set[int] = {
            TerrainType.WALL,
            TerrainType.TREE,
            TerrainType.ROCK,
            TerrainType.BUILDING,
        }
        return self.tiles[x][y] in bullet_blocking

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a position is walkable (opposite of blocked).
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            True if position is walkable, False otherwise
        """
        return not self.is_blocked(x, y)

    def line_of_sight(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        """Check if there's a clear line of sight between two points.
        
        Uses Bresenham's line algorithm to trace a path and check for
        bullet-blocking terrain along the way.
        
        Args:
            x1: Starting X coordinate
            y1: Starting Y coordinate
            x2: Ending X coordinate  
            y2: Ending Y coordinate
            
        Returns:
            True if line of sight is clear, False if blocked
        """
        line_points = tcod.los.bresenham((x1, y1), (x2, y2)).tolist()

        # Check each point in the line (except start and end)
        for x, y in line_points[1:-1]:
            if self.blocks_bullets(x, y):
                return False
        return True

    def get_terrain_type(self, x: int, y: int) -> int:
        """Get the terrain type at a position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            TerrainType constant for the terrain at that position,
            or TerrainType.WALL if position is invalid
        """
        if not self.is_valid_position(x, y):
            return TerrainType.WALL
        return self.tiles[x][y]

    def find_valid_positions(self, border_margin: int = 2) -> List[Tuple[int, int]]:
        """Find all valid (non-blocked) positions on the map.
        
        Args:
            border_margin: Distance from map edges to exclude from results
            
        Returns:
            List of (x, y) tuples representing walkable positions
        """
        valid_positions = []
        for x in range(border_margin, self.width - border_margin):
            for y in range(border_margin, self.height - border_margin):
                if self.is_walkable(x, y):
                    valid_positions.append((x, y))
        return valid_positions

    def get_terrain_positions_by_type(self, terrain_type: int) -> List[Tuple[int, int]]:
        """Get all positions of a specific terrain type.
        
        Args:
            terrain_type: TerrainType constant to search for
            
        Returns:            
            List of (x, y) tuples where the specified terrain type exists
        """
        positions = []
        for x in range(self.width):
            for y in range(self.height):
                if self.tiles[x][y] == terrain_type:
                    positions.append((x, y))
        return positions

    def get_line_path(self, x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        """Get the path of points between two coordinates using Bresenham's algorithm.
        
        Args:
            x1: Starting X coordinate
            y1: Starting Y coordinate
            x2: Ending X coordinate
            y2: Ending Y coordinate
            
        Returns:
            List of (x, y) coordinate tuples representing the line path
        """
        return tcod.los.bresenham((x1, y1), (x2, y2)).tolist()

    def find_spawn_positions(self, min_distance: int = 20) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
        """Find two spawn positions that are far apart for balanced gameplay.
        
        Args:
            min_distance: Minimum Manhattan distance between spawn points
            
        Returns:
            Tuple of two (x, y) position tuples, or (None, None) if suitable
            positions cannot be found
        """
        valid_positions = self.find_valid_positions()

        if len(valid_positions) < 2:
            return None, None

        # Pick first position randomly
        pos1 = random.choice(valid_positions)

        # Find positions far from the first one
        distant_positions = [
            pos
            for pos in valid_positions
            if abs(pos[0] - pos1[0]) + abs(pos[1] - pos1[1]) > min_distance
        ]

        if distant_positions:
            pos2 = random.choice(distant_positions)
        else:
            # If no distant positions, just pick any other position
            pos2 = random.choice([pos for pos in valid_positions if pos != pos1])

        return pos1, pos2