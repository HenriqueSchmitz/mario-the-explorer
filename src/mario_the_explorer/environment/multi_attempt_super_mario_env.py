from logging import Logger
from typing import Any, Optional

from mario_the_explorer.environment.rewards import RewardModel
from mario_the_explorer.environment.super_mario_env import SuperMarioWorldEmulator
from mario_the_explorer.environment.visualization import ScreenOverlay


class MultiAttemptSuperMarioWorldEmulator(SuperMarioWorldEmulator):
    def __init__(self,
                 level: str,
                 render_mode: str,
                 reward_model: RewardModel,
                 attempts: int,
                 screen_overlay: Optional[ScreenOverlay] = None,
                 max_episode_length: Optional[int] = None,
                 render_debug: bool = False,
                 render_grid: bool = False,
                 logger: Optional[Logger] = None):
        super().__init__(
            level=level,
            render_mode=render_mode,
            reward_model=reward_model,
            screen_overlay=screen_overlay,
            max_episode_length=max_episode_length,
            render_debug=render_debug,
            render_grid=render_grid,
            logger=logger
        )
        self.attempts = attempts
        self._current_attempt = 0

    def reset(self, *args, **kwargs):
        self._current_attempt = 0       
        return super().reset(*args, **kwargs)
    
    def step(self, action: list[int]) -> tuple[Any, float, bool, bool, dict]:
        observation, reward, terminated, truncated, info = super().step(action)
        if not terminated and not truncated:
            return observation, reward, terminated, truncated, info
        self._current_attempt += 1
        if self._current_attempt < self.attempts:
            observation, info = super().reset(reset_reward_model=False, reset_overlay=False)
            terminated = False
            truncated = False
        return observation, reward, terminated, truncated, info
    
