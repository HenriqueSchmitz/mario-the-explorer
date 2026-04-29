from enum import Enum
from logging import Logger

import torch
import numpy as np
import gymnasium as gym



class SuperMarioAction(Enum):
    B = 0
    Y = 1
    SELECT = 2
    START = 3
    UP = 4
    DOWN = 5
    LEFT = 6
    RIGHT = 7
    A = 8
    X = 9
    L = 10
    R = 11

class SuperMarioCombo(Enum):
    DO_NOTHING = []
    LEFT = [SuperMarioAction.LEFT]
    LEFT_RUN = [SuperMarioAction.LEFT, SuperMarioAction.Y]
    LEFT_JUMP = [SuperMarioAction.LEFT, SuperMarioAction.B]
    LEFT_RUN_JUMP = [SuperMarioAction.LEFT, SuperMarioAction.Y, SuperMarioAction.B]
    RIGHT = [SuperMarioAction.RIGHT]
    RIGHT_RUN = [SuperMarioAction.RIGHT, SuperMarioAction.Y]
    RIGHT_JUMP = [SuperMarioAction.RIGHT, SuperMarioAction.B]
    RIGHT_RUN_JUMP = [SuperMarioAction.RIGHT, SuperMarioAction.Y, SuperMarioAction.B]
    JUMP = [SuperMarioAction.B]
    DOWN = [SuperMarioAction.DOWN]

    @staticmethod
    def get_combo_id(combo: 'SuperMarioCombo') -> int:
        return list(SuperMarioCombo).index(combo)

class SuperMarioDiscretizer(gym.ActionWrapper):

    def __init__(self, env):
        super().__init__(env)
        self._action_map = []
        for combo in SuperMarioCombo:
            self._action_map.append(self._build_action_from_combo(combo))
        self.action_space = gym.spaces.Discrete(len(self._action_map))

    def _build_action_from_combo(self, combo: SuperMarioCombo) -> np.ndarray:
        action_vector = np.zeros(len(SuperMarioAction), dtype=np.uint8)
        for action in combo.value:
            action_vector[action.value] = 1
        return action_vector

    def action(self, action: int):
        return self._action_map[int(action)]
    
def prime_policy_for_combo(model, target_combo: SuperMarioCombo, env, logger: Logger, iterations=1000):
    logger.info(f"Priming policy to prefer '{target_combo.key}'") # type: ignore
    optimizer = model.policy.optimizer
    combo_index = SuperMarioCombo.get_combo_id(target_combo)
    target_action = torch.tensor([combo_index]).to(model.device)
    model.policy.train()
    for _ in range(iterations):
        obs, _ = model.policy.obs_to_tensor(env.observation_space.sample())
        distribution = model.policy.get_distribution(obs)
        logits = distribution.distribution.logits
        loss = torch.nn.functional.cross_entropy(logits, target_action)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    logger.info("Priming complete")