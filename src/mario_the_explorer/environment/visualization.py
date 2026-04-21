import cv2
import numpy as np

from mario_the_explorer.environment.tiles import Tile, TileType
from mario_the_explorer.environment.world_parser import SCREEN_COLUMNS, SCREEN_ROWS, TILE_SIZE

BLACK_RGB = (0, 0, 0)
RED_HSV = (0, 200, 255)
GREN_HSV = (60, 255, 255)

GRID_COLOR_RGB = (80, 80, 80)



class DebugVisualizer():
    def __init__(self, render_grid=False):
        self.render_grid = render_grid
        self.img_width = SCREEN_COLUMNS * TILE_SIZE
        self.img_height = SCREEN_ROWS * TILE_SIZE

    def overlay(self, original_frame, observation):
        game_view = original_frame.copy()
        if self.render_grid:
            game_view = self._draw_grid(game_view)
        matrix_view = self._get_observation_image(observation)
        return np.hstack((game_view, matrix_view))

    def _get_observation_image(self, observation):
        matrix_img = np.zeros((self.img_height, self.img_width, 3), dtype=np.uint8)
        if observation is not None:
            matrix_img = self._populate_objects(matrix_img, observation)
        if self.render_grid:
            matrix_img = self._draw_grid(matrix_img)
        return matrix_img

    def _populate_objects(self, matrix_img, observation):
        for row in range(SCREEN_ROWS):
            for col in range(SCREEN_COLUMNS):
                tile = observation[row][col]
                self._draw_tile(matrix_img, col, row, tile)
        return matrix_img

    def _draw_tile(self, img, x: int, y: int, tile: Tile) -> None:
        if tile["type"] == TileType.EMPTY:
            return
        color = self._choose_tile_color(tile)
        x_start = int(x * TILE_SIZE)
        y_start = int(y * TILE_SIZE)
        x_end = x_start + TILE_SIZE - 1
        y_end = y_start + TILE_SIZE - 1
        cv2.rectangle(img, (x_start, y_start), (x_end, y_end), color, -1) # type: ignore

    def _choose_tile_color(self, tile: Tile) -> tuple[int, int, int]:
        if tile["type"] == TileType.EMPTY:
            return BLACK_RGB
        t_type = tile["type"]
        t_id = int(tile["id"])
        h, s, v = RED_HSV
        if t_type == TileType.MARIO:
            h, s, v = GREN_HSV
        elif t_type == TileType.BLOCK:
            # Blue/Cyan range
            h = 100 + (t_id % 20)
            s = 150 + (t_id % 100)
        elif t_type == TileType.SPRITE:
            # Purple/Magenta range
            h = 140 + (t_id % 20)
            s = 200 + (t_id % 55)
        elif t_type == TileType.EXTENDED_SPRITE:
            # Orange/Yellow range
            h = 20 + (t_id % 15)
            s = 180 + (t_id % 75)
        hsv_pixel = np.array([[[h, s, v]]]).astype(np.uint8)
        rgb_pixel = cv2.cvtColor(hsv_pixel, cv2.COLOR_HSV2RGB)[0][0]
        return rgb_pixel[0], rgb_pixel[1], rgb_pixel[2]

    def _draw_grid(self, img):
        h, w = img.shape[:2]
        for x in range(0, w + 1, TILE_SIZE):
            cv2.line(img, (x, 0), (x, h), GRID_COLOR_RGB, 1)
        for y in range(0, h + 1, TILE_SIZE):
            cv2.line(img, (0, y), (w, y), GRID_COLOR_RGB, 1)
        return img