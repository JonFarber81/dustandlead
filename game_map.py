"""
Game map generation and utilities
"""
import random
import tcod
from constants import (
    MIN_WALL_CLUSTERS, MAX_WALL_CLUSTERS, 
    MIN_CLUSTER_SIZE, MAX_CLUSTER_SIZE,
    TREE_CLUSTERS, TREE_CLUSTER_SIZE,
    WATER_FEATURES, WATER_SIZE,
    ROCK_FORMATIONS, CACTUS_PATCHES,
    BUILDING_RUINS
)


class TerrainType:
    """Enum-like class for different terrain types"""
    FLOOR = 0
    WALL = 1
    TREE = 2
    WATER = 3
    ROCK = 4
    CACTUS = 5
    BUILDING = 6


class GameMap:
    """Handles map generation, collision detection, and line of sight"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Use terrain types instead of just True/False
        self.tiles = [[TerrainType.FLOOR for _ in range(height)] for _ in range(width)]
        self.generate_old_west_map()

    def generate_old_west_map(self):
        """Generate an old west themed map with various terrain features"""
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
        
    def _create_border_walls(self):
        """Create walls around the map border"""
        for x in range(self.width):
            self.tiles[x][0] = TerrainType.WALL
            self.tiles[x][self.height - 1] = TerrainType.WALL
        for y in range(self.height):
            self.tiles[0][y] = TerrainType.WALL
            self.tiles[self.width - 1][y] = TerrainType.WALL

    def _add_water_features(self):
        """Add rivers, ponds, or streams"""
        num_features = random.randint(*WATER_FEATURES)
        
        for _ in range(num_features):
            if random.choice([True, False]):  # 50% chance river vs pond
                self._create_river()
            else:
                self._create_pond()
    
    def _create_river(self):
        """Create a winding river across the map"""
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
    
    def _create_pond(self):
        """Create a small pond or lake"""
        center_x = random.randint(5, self.width - 6)
        center_y = random.randint(5, self.height - 6)
        size = random.randint(*WATER_SIZE)
        
        # Create roughly circular pond
        for x in range(center_x - size//2, center_x + size//2 + 1):
            for y in range(center_y - size//2, center_y + size//2 + 1):
                if self.is_valid_position(x, y):
                    distance = abs(x - center_x) + abs(y - center_y)
                    if distance <= size//2 + random.randint(-1, 1):
                        self.tiles[x][y] = TerrainType.WATER

    def _add_tree_clusters(self):
        """Add clusters of trees for cover and atmosphere"""
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
                
                if (self.is_valid_position(tree_x, tree_y) and 
                    self.tiles[tree_x][tree_y] == TerrainType.FLOOR):
                    self.tiles[tree_x][tree_y] = TerrainType.TREE

    def _add_rock_formations(self):
        """Add rocky outcroppings for cover"""
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
                
                if (self.is_valid_position(rock_x, rock_y) and 
                    self.tiles[rock_x][rock_y] == TerrainType.FLOOR):
                    self.tiles[rock_x][rock_y] = TerrainType.ROCK

    def _add_cactus_patches(self):
        """Add desert cacti scattered around"""
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
                
                if (self.is_valid_position(cactus_x, cactus_y) and 
                    self.tiles[cactus_x][cactus_y] == TerrainType.FLOOR):
                    self.tiles[cactus_x][cactus_y] = TerrainType.CACTUS

    def _add_building_ruins(self):
        """Add ruins of old buildings"""
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
                        is_edge = (x == ruin_x or x == ruin_x + width - 1 or 
                                 y == ruin_y or y == ruin_y + height - 1)
                        if is_edge and random.random() < 0.7:  # 70% chance for wall
                            if self.tiles[x][y] == TerrainType.FLOOR:
                                self.tiles[x][y] = TerrainType.BUILDING

    def _add_cover_walls(self):
        """Add some traditional cover walls like the original"""
        num_walls = random.randint(MIN_WALL_CLUSTERS, MAX_WALL_CLUSTERS)
        for _ in range(num_walls):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            
            # Create small wall clusters
            cluster_size = random.randint(MIN_CLUSTER_SIZE, MAX_CLUSTER_SIZE)
            for _ in range(cluster_size):
                if (self.is_valid_position(x, y) and 
                    self.tiles[x][y] == TerrainType.FLOOR):
                    self.tiles[x][y] = TerrainType.WALL
                x += random.randint(-1, 1)
                y += random.randint(-1, 1)

    def is_valid_position(self, x, y):
        """Check if position is within map bounds"""
        return 0 <= x < self.width and 0 <= y < self.height

    def is_blocked(self, x, y):
        """Check if a position is blocked (wall or out of bounds)"""
        if not self.is_valid_position(x, y):
            return True
        
        # All solid terrain types block movement
        blocking_terrain = {
            TerrainType.WALL, TerrainType.TREE, TerrainType.WATER, 
            TerrainType.ROCK, TerrainType.BUILDING
        }
        return self.tiles[x][y] in blocking_terrain

    def blocks_bullets(self, x, y):
        """Check if a position blocks bullets (different from movement)"""
        if not self.is_valid_position(x, y):
            return True
        
        # Cacti don't block bullets, but other terrain does
        bullet_blocking = {
            TerrainType.WALL, TerrainType.TREE, TerrainType.ROCK, 
            TerrainType.BUILDING
        }
        return self.tiles[x][y] in bullet_blocking

    def is_walkable(self, x, y):
        """Check if a position is walkable (opposite of blocked)"""
        return not self.is_blocked(x, y)

    def line_of_sight(self, x1, y1, x2, y2):
        """Check if there's a clear line of sight between two points"""
        line_points = tcod.los.bresenham((x1, y1), (x2, y2)).tolist()

        # Check each point in the line (except start and end)
        for x, y in line_points[1:-1]:
            if self.blocks_bullets(x, y):
                return False
        return True

    def get_terrain_type(self, x, y):
        """Get the terrain type at a position"""
        if not self.is_valid_position(x, y):
            return TerrainType.WALL
        return self.tiles[x][y]

    def find_valid_positions(self, border_margin=2):
        """Find all valid (non-blocked) positions on the map"""
        valid_positions = []
        for x in range(border_margin, self.width - border_margin):
            for y in range(border_margin, self.height - border_margin):
                if self.is_walkable(x, y):
                    valid_positions.append((x, y))
        return valid_positions

    def get_terrain_positions_by_type(self, terrain_type):
        """Get all positions of a specific terrain type"""
        positions = []
        for x in range(self.width):
            for y in range(self.height):
                if self.tiles[x][y] == terrain_type:
                    positions.append((x, y))
        return positions

    def get_line_path(self, x1, y1, x2, y2):
        """Get the path of points between two coordinates"""
        return tcod.los.bresenham((x1, y1), (x2, y2)).tolist()

    def find_spawn_positions(self, min_distance=20):
        """Find two spawn positions that are far apart"""
        valid_positions = self.find_valid_positions()
        
        if len(valid_positions) < 2:
            return None, None

        # Pick first position randomly
        pos1 = random.choice(valid_positions)
        
        # Find positions far from the first one
        distant_positions = [
            pos for pos in valid_positions 
            if abs(pos[0] - pos1[0]) + abs(pos[1] - pos1[1]) > min_distance
        ]
        
        if distant_positions:
            pos2 = random.choice(distant_positions)
        else:
            # If no distant positions, just pick any other position
            pos2 = random.choice([pos for pos in valid_positions if pos != pos1])
            
        return pos1, pos2