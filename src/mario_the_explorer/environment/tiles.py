import enum
from typing import TypedDict, Optional

import numpy as np



class TileType(enum.Enum):
    EMPTY = 0
    MARIO = 1
    SPRITE = 2
    EXTENDED_SPRITE = 3
    BLOCK = 4

class Tile(TypedDict):
    type: TileType
    id: int

def tile_absolute_id(tile: Tile) -> int:
    if tile["type"] == TileType.EMPTY:
        return 0
    if tile["type"] == TileType.MARIO:
        return 1
    offset_level = 0
    offset_multiplier = 256
    if tile["type"] == TileType.SPRITE:
        offset_level = 1
    if tile["type"] == TileType.EXTENDED_SPRITE:
        offset_level = 2
    if tile["type"] == TileType.BLOCK:
        offset_level = 3
    offset = offset_level * offset_multiplier
    return int(tile["id"]) + offset

class LayeredTile():
    def __init__(self, type: TileType, id: int, layer: int):
        self.type = type
        self.id = id
        self.layer = layer

    def get_tile(self) -> Tile:
        return Tile(type=self.type, id=self.id)

class UngriddedTile(LayeredTile):
    def __init__(self, type: TileType, id: int, layer: int, x: int, y: int):
        super().__init__(type, id, layer)
        self.x = x
        self.y = y

class TileStack():
    def __init__(self):
        self.stack: list[LayeredTile] = []

    def add(self, tile: LayeredTile):
        self.stack.append(tile)

    def resolve(self) -> Tile:
        if len(self.stack) == 0:
            return Tile(type=TileType.EMPTY, id=0)
        front_tile = self.stack[0]
        for tile in self.stack:
            if tile.layer < front_tile.layer:
                front_tile = tile
        return front_tile.get_tile()

class DenseTileMatrix():
    def __init__(self, rows: int = 14, columns: int = 16):
        self.rows = rows
        self.columns = columns
        self.tile_matrix: list[list[TileStack]] = []
        for row in range(rows):
            row_stack = []
            for col in range(columns):
                row_stack.append(TileStack())
            self.tile_matrix.append(row_stack)

    def add(self, tile: Optional[UngriddedTile]):
        if tile is None:
            return
        if not self._are_grid_coords_in_cam_view(tile.x, tile.y):
            return
        self.tile_matrix[tile.y][tile.x].add(tile)

    def _are_grid_coords_in_cam_view(self, grid_x: int, grid_y: int) -> bool:
        return 0 <= grid_x < self.columns and 0 <= grid_y < self.rows

    def resolve(self) -> list[list[Tile]]:
        resolved_matrix: list[list[Tile]] = []
        for row in self.tile_matrix:
            resolved_row: list[Tile] = []
            for col in row:
                resolved_row.append(col.resolve())
            resolved_matrix.append(resolved_row)
        return resolved_matrix

    def resolveSimplified(self):
        resolved_matrix = []
        for row in self.tile_matrix:
            resolved_row = []
            for col in row:
                resolved_row.append(tile_absolute_id(col.resolve()))
            resolved_matrix.append(resolved_row)
        return np.array(resolved_matrix)