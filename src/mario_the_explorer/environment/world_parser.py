from logging import Logger
from typing import Optional

import numpy as np

from mario_the_explorer.environment.tiles import DenseTileMatrix, Tile, TileType, UngriddedTile
from mario_the_explorer.logging.dummy_logger import DummyLogger

SCREEN_ROWS = 14
SCREEN_COLUMNS = 16
TILE_SIZE = 16

TILE_BLOCK_COLUMNS = 16
WORLD_HEIGHT_TILES = 27
TILE_BLOCK_TILES = TILE_BLOCK_COLUMNS * WORLD_HEIGHT_TILES
MAX_NUMBER_OF_TILES = 14336

MAP_TILES_BASE_ADDRESS = 0xF000
MAP_TILE_ATTRIBUTES_OFFSET = 0x10000
MAP_TILE_ATTRIBUTES_BASE_ADDRESS = MAP_TILES_BASE_ADDRESS + MAP_TILE_ATTRIBUTES_OFFSET

SKY_TILE_ID = 0x25



class WorldParser:
    def __init__(self, env, logger: Optional[Logger] = None):
        self.logger: Logger = logger if logger is not None else DummyLogger()
        self.env = env

    def get_screen_matrix(self, info) -> list[list[Tile]]:
        screen_matrix = self._build_dense_screen_matrix(info)
        return screen_matrix.resolve()

    def get_screen_matrix_simplified(self, info) -> np.ndarray:
        screen_matrix = self._build_dense_screen_matrix(info)
        return screen_matrix.resolveSimplified()

    def _build_dense_screen_matrix(self, info) -> DenseTileMatrix:
        screen_matrix = DenseTileMatrix()
        for mario_tile in self._get_mario(info):
            screen_matrix.add(mario_tile)
        for sprite in self._get_sprites(info):
            screen_matrix.add(sprite)
        for extended_sprite in self._get_extended_sprites(info):
            screen_matrix.add(extended_sprite)
        for tile in self._get_layer1_tiles(info):
            screen_matrix.add(tile)
        return screen_matrix

    def _get_mario(self, info: dict) -> list[UngriddedTile]:
        mario_tiles = []
        mario_x = info.get("x", 0)
        mario_y = info.get("y", 0)
        grid_x, grid_y = self._coords_absolute_to_cam_grid(mario_x, mario_y, info)
        grid_y += 1 # Fixing shift in mario position
        grid_x += 1
        if not self._are_grid_coords_in_cam_view(grid_x, grid_y):
            return []
        mario_priority = info.get("mario_priority", 2)
        layer = 1 if mario_priority == 3 else 3
        mario_tiles.append(UngriddedTile(type=TileType.MARIO, id=1, layer=layer, x=grid_x, y=grid_y))
        is_big = info.get('mario_powerup', 0) > 0
        if is_big and grid_y > 0:
            mario_tiles.append(UngriddedTile(type=TileType.MARIO, id=2, layer=layer, x=grid_x, y=grid_y - 1))
        return mario_tiles

    def _get_sprites(self, info: dict) -> list[UngriddedTile]:
        sprites = []
        for sprite_index in range(12):
            sprite = self._get_sprite_at_index(sprite_index, info)
            if sprite is not None:
                sprites.append(sprite)
        return sprites

    def _get_sprite_at_index(self, index: int, info: dict) -> Optional[UngriddedTile]:
        if info.get(f"sprite_status_{index}", 0) == 0:
            return None
        sprite_x = self._combine_low_and_high_bits(info.get(f"sprite_x_low_{index}", 0), info.get(f"sprite_x_high_{index}", 0))
        sprite_y = self._combine_low_and_high_bits(info.get(f"sprite_y_low_{index}", 0), info.get(f"sprite_y_high_{index}", 0))
        sprite_type = info.get(f"sprite_type_{index}", 0)
        grid_x, grid_y = self._coords_absolute_to_cam_grid(sprite_x, sprite_y, info)
        grid_x += 1 # Fixing shift in position of all sprites
        if not self._are_grid_coords_in_cam_view(grid_x, grid_y):
            return None
        priority_byte = info.get(f"sprite_priority_{index}", 0)
        sprite_priority = priority_byte & 0x03
        layer_map = {3: 1, 2: 3, 1: 5, 0: 6}
        layer = layer_map.get(sprite_priority, 3)
        return UngriddedTile(type=TileType.SPRITE, id=sprite_type, layer=layer, x=grid_x, y=grid_y)

    def _get_extended_sprites(self, info: dict) -> list[UngriddedTile]:
        extended_sprites = []
        for sprite_index in range(10):
            extended_sprite = self._get_extended_sprite_at_index(sprite_index, info)
            if extended_sprite is not None:
                extended_sprites.append(extended_sprite)
        return extended_sprites

    def _get_extended_sprite_at_index(self, index: int, info: dict) -> Optional[UngriddedTile]:
        sprite_type = info.get(f"ext_sprite_type_{index}", 0)
        if sprite_type == 0:
            return None
        sprite_x = self._combine_low_and_high_bits(info.get(f"ext_sprite_x_low_{index}", 0), info.get(f"ext_sprite_x_high_{index}", 0))
        sprite_y = self._combine_low_and_high_bits(info.get(f"ext_sprite_y_low_{index}", 0), info.get(f"ext_sprite_y_high_{index}", 0))
        grid_x, grid_y = self._coords_absolute_to_cam_grid(sprite_x, sprite_y, info)
        grid_x += 1 # Fixing shift in position of all extended sprites
        if not self._are_grid_coords_in_cam_view(grid_x, grid_y):
            return None
        return UngriddedTile(type=TileType.EXTENDED_SPRITE, id=sprite_type+200, layer=3, x=grid_x, y=grid_y)

    def _get_layer1_tiles(self, info: dict) -> list[UngriddedTile]:
        ram = self.env.unwrapped.get_ram()
        cam_x, cam_y = self._get_camera_coords(info)
        tiles = []
        for row in range(SCREEN_ROWS):
            for col in range(SCREEN_COLUMNS):
                tiles.append(self.get_tile_at_screen_position(col, row, cam_x, cam_y, ram))
        return tiles
    
    def get_tile_at_screen_position(self, x: int, y: int, cam_x: int, cam_y: int, ram) -> Optional[UngriddedTile]:
        tile_index = self.find_index_of_tile_at_screen_position(x, y, cam_x, cam_y)
        if tile_index >= MAX_NUMBER_OF_TILES:
            return None
        tile_id = ram[MAP_TILES_BASE_ADDRESS + tile_index]
        if tile_id == SKY_TILE_ID:
            return None
        attributes_byte = ram[MAP_TILE_ATTRIBUTES_BASE_ADDRESS + tile_index]
        has_priority = (attributes_byte & 0x20) != 0
        layer = 2 if has_priority else 4
        return UngriddedTile(
            type=TileType.BLOCK,
            id=tile_id,
            layer=layer,
            x=x,
            y=y
        )

    def find_index_of_tile_at_screen_position(self, x: int, y: int, cam_x: int, cam_y: int) -> int:
        world_x = cam_x + (x * TILE_SIZE)
        world_y = cam_y + (y * TILE_SIZE)
        world_column = world_x // TILE_SIZE
        world_row = world_y // TILE_SIZE
        screen_num = world_column // TILE_BLOCK_COLUMNS
        local_x = world_column % TILE_BLOCK_COLUMNS
        tile_index = (screen_num * TILE_BLOCK_TILES) + (world_row * TILE_BLOCK_COLUMNS) + local_x
        return tile_index

    def _combine_low_and_high_bits(self, low: int, high: int) -> int:
        return (high << 8) | low

    def _are_grid_coords_in_cam_view(self, grid_x: int, grid_y: int) -> bool:
        return 0 <= grid_x < SCREEN_COLUMNS and 0 <= grid_y < SCREEN_ROWS

    def _coords_absolute_to_cam_grid(self, x: int, y: int, info: dict) -> tuple[int, int]:
        relative_x, relative_y = self._coords_absolute_to_cam_relative(x, y, info)
        grid_x = relative_x // TILE_SIZE
        grid_y = relative_y // TILE_SIZE
        return grid_x, grid_y

    def _coords_absolute_to_cam_relative(self, x: int, y: int, info: dict) -> tuple[int, int]:
        cam_x, cam_y = self._get_camera_coords(info)
        relative_x = int(x) - cam_x
        relative_y = int(y) - cam_y
        return relative_x, relative_y

    def _get_camera_coords(self, info: dict):
        cam_x = info.get('cam_x', None)
        ram = None
        if cam_x is None:
            ram = self.env.unwrapped.get_ram()
            cam_x = self._combine_low_and_high_bits(ram[0x1A], ram[0x1B])
        cam_y = info.get('cam_y', None)
        if cam_y is None:
            if ram is None:
                ram = self.env.unwrapped.get_ram()
            cam_y = self._combine_low_and_high_bits(ram[0x1C], ram[0x1D])
        return int(cam_x), int(cam_y)