from abc import ABC, abstractmethod

from mario_the_explorer.environment.tiles import Tile


class RewardModel(ABC):

    @abstractmethod
    def get_reward(self,
                   action: list[int],
                   observation: list[list[Tile]],
                   terminated: bool,
                   truncated: bool,
                   info: dict) -> float:
        raise NotImplementedError
