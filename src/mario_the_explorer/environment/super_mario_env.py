from logging import Logger
from typing import Any, Optional

import gymnasium as gym
import numpy as np
from mario_the_explorer.environment.env_setup import setup_emulator_memory
from mario_the_explorer.environment.rewards import RewardModel
import stable_retro as retro # type: ignore

from mario_the_explorer.environment.visualization import DebugVisualizer
from mario_the_explorer.environment.world_parser import SCREEN_COLUMNS, SCREEN_ROWS, WorldParser
from mario_the_explorer.logging.dummy_logger import DummyLogger

EMULATOR_NAME = "SuperMarioWorld-Snes-v0"



class SuperMarioWorldEmulator(gym.Env):
    is_emulator_memory_initialized = False

    def __init__(self,
                 level: str,
                 render_mode: str,
                 reward_model: RewardModel,
                 max_episode_length: Optional[int] = None,
                 render_debug: bool = False,
                 render_grid: bool = False,
                 logger: Optional[Logger] = None):
        super().__init__()
        self.logger: Logger = logger if logger is not None else DummyLogger()
        if not self.is_emulator_memory_initialized:
            setup_emulator_memory()
            self.is_emulator_memory_initialized = True
        self.env = retro.make(game=EMULATOR_NAME, state=level, render_mode=render_mode)
        self.reward_model = reward_model
        self._max_episode_length = max_episode_length
        self._world_parser = WorldParser(self.env, logger=logger)
        self._debug_visualizer = DebugVisualizer(render_grid=render_grid)
        self.action_space = self.env.action_space
        self.observation_space = gym.spaces.Box(
            low=0, high=65535, shape=(SCREEN_ROWS, SCREEN_COLUMNS), dtype=np.int32
        )
        self._current_step = 0
        self.render_debug = render_debug
        self.render_grid = render_grid
        self.observation = None

    def reset(self, **kwargs):
        self._current_step = 0
        _, info = self.env.reset(**kwargs)
        matrix_obs = self._world_parser.get_screen_matrix(info)
        self._has_found_ram_offset = False
        return matrix_obs, info

    def render(self):
        original_frame = self.env.render()
        if not self.render_debug:
            return original_frame
        debug_frame = self._debug_visualizer.overlay(original_frame, self.observation)
        return debug_frame

    def step(self, action: list[int]) -> tuple[Any, float, bool, bool, dict]:
        _, _, _, _, info = self.env.step(action)
        self._current_step += 1
        self.observation = self._world_parser.get_screen_matrix(info)
        simplified_observation = self._world_parser.get_screen_matrix_simplified(info)
        terminated = self._has_died(info)
        truncated = self._has_reached_max_steps()
        reward = self.reward_model.get_reward(action, self.observation, terminated, truncated, info)
        new_info = self._reformat_info(info)
        return simplified_observation, reward, terminated, truncated, new_info

    def _has_died(self, info) -> bool:
        return info["lives"] < 4

    def _has_reached_max_steps(self) -> bool:
        if self._max_episode_length is None:
            return False
        return self._current_step >= self._max_episode_length

    def _reformat_info(self, info) -> dict:
        return {
            "score": info["score"],
            "lives": info["lives"]
        }