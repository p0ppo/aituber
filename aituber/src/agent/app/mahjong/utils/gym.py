from typing import Dict, List, Optional

import gym
import mjx


class GymEnv(gym.Env):
    def __init__(
        self, opponent_agents: List[mjx.Agent], reward_type: str, done_type: str, feature_type: str
    ) -> None:
        super().__init__()
        self.opponen_agents = {}
        assert len(opponent_agents) == 3
        for i in range(3):
            self.opponen_agents[f"player_{i+1}"] = opponent_agents[i]
        self.reward_type = reward_type
        self.done_type = done_type
        self.feature_type = feature_type

        self.target_player = "player_0"
        self.mjx_env = mjx.MjxEnv()
        self.curr_obs_dict: Dict[str, mjx.Observation] = self.mjx_env.reset()

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        return_info: bool = True,
        options: Optional[dict] = None,
    ):
        assert return_info
        if self.mjx_env.done("game"):
            self.curr_obs_dict = self.mjx_env.reset()

        # skip other players' turns
        while self.target_player not in self.curr_obs_dict:
            action_dict = {
                player_id: self.opponen_agents[player_id].act(obs)
                for player_id, obs in self.curr_obs_dict.items()
            }
            self.curr_obs_dict = self.mjx_env.step(action_dict)
            # game ends without player_0's turn
            if self.mjx_env.done("game"):
                self.curr_obs_dict = self.mjx_env.reset()

        assert self.target_player in self.curr_obs_dict
        obs = self.curr_obs_dict[self.target_player]
        feat = obs.to_features(self.feature_type)
        mask = obs.action_mask()
        return feat, {"action_mask": mask}, obs.legal_actions(), obs

    def step(self, action):
        # prepare action_dict
        action_dict = {}
        legal_actions = self.curr_obs_dict[self.target_player].legal_actions()
        action_dict[self.target_player] = mjx.Action.select_from(action, legal_actions)
        for player_id, obs in self.curr_obs_dict.items():
            if player_id == self.target_player:
                continue
            action_dict[player_id] = self.opponen_agents[player_id].act(obs)

        # update curr_obs_dict
        self.curr_obs_dict = self.mjx_env.step(action_dict)

        # skip other players' turns
        while self.target_player not in self.curr_obs_dict:
            action_dict = {
                player_id: self.opponen_agents[player_id].act(obs)
                for player_id, obs in self.curr_obs_dict.items()
            }
            self.curr_obs_dict = self.mjx_env.step(action_dict)

        # parepare return
        assert self.target_player in self.curr_obs_dict, self.curr_obs_dict.items()
        obs = self.curr_obs_dict[self.target_player]
        done = self.mjx_env.done(self.done_type)
        r = self.mjx_env.rewards(self.reward_type)[self.target_player]
        feat = obs.to_features(self.feature_type)
        mask = obs.action_mask()

        return feat, r, done, {"action_mask": mask}
