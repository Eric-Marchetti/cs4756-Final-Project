import numpy as np
import gymnasium as gym
from gymnasium import spaces
import networkx as nx
import matplotlib.pyplot as plt
import time

class RiskEnvWrapper(gym.Env): 
    def __init__(self, risk_env, visualize=False): 
        super(RiskEnvWrapper, self).__init__()
        self.risk_env = risk_env
        self.T = risk_env.game_state.shape[0]

        self.action_space = spaces.Dict({
            'reinforce': spaces.Box(low=0, high=1, shape=(self.T,), dtype=np.float32),
            'attack_units': spaces.Box(low=0, high=1, shape=(self.T,), dtype=np.float32),
            'attack_dest': spaces.Box(low=0, high=self.T, shape=(self.T,), dtype=np.int32),
            'fortify_src_dest': spaces.Box(low=0, high=self.T, shape=(2,), dtype=np.int32),
            'fortify_units': spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
        })
        self.observation_space = spaces.Dict({
            'owners': spaces.Box(low=0, high=len(self.risk_env.players), shape=(self.T,), dtype=np.int32),
            'units': spaces.Box(low=0, high=np.inf, shape=(self.T,), dtype=np.int32),
            'reinforcement_max': spaces.Box(low=0, high=np.inf, shape=(1,), dtype=np.int32),
            'adjacencies': spaces.Box(low=0, high=1, shape=(self.T,self.T), dtype=np.int32),
            'fortify_paths': spaces.Box(low=0, high=np.inf, shape=(self.T,self.T), dtype=np.int32)
        })

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.risk_env.reset()
        return self._get_obs(), {}
    
    def step(self, action):
        reinforce_action = action['reinforce']
        attack_units = action['attack_units']
        attack_dest = action['attack_dest']
        fortify_units = action['fortify_units']
        fortify_src_dest = action['fortify_src_dest']

        # Convert reinforce_action from distribution to number of units
        reinforce_action = (reinforce_action / np.sum(reinforce_action) * self.risk_env.get_reinforcements(self.risk_env.current_player_id)).astype(np.int32)
        
        # Do the same for attack_units and fortify_units
        attack_units_shape = attack_units.shape 
        attack_indices = np.where(attack_units > 0) 
        attack_units_flat = attack_units.flatten() 
        attack_units = np.zeros_like(attack_units_flat, dtype=np.int32) 
        if attack_indices[0].size > 0: 
            attack_units[attack_indices] = np.minimum((attack_units_flat[attack_indices] * self.risk_env.game_state.flatten()[attack_indices]).astype(np.int32), self.risk_env.game_state.flatten()[attack_indices] - 1) 
        attack_units = attack_units.reshape(attack_units_shape)
        
        if fortify_units > 0: 
            fortify_units = np.minimum((fortify_units * self.risk_env.game_state[fortify_src_dest[0] - 1, 1]).astype(np.int32), self.risk_env.game_state[fortify_src_dest[0] - 1, 1] - 1) 
        else: 
            fortify_units = np.zeros_like(fortify_units, dtype=np.int32)

        self.risk_env.reinforce(self.risk_env.current_player_id, reinforce_action)
        self.risk_env.winner = self.risk_env.attack(self.risk_env.current_player_id, np.array([attack_units, attack_dest]))
        self.risk_env.fortify(self.risk_env.current_player_id, np.concatenate([fortify_units, fortify_src_dest]))

        return self._get_obs(), self.risk_env.get_reward(), self.risk_env.is_game_over(), {}
    
    def _get_obs(self):
        return {
            'owners': self.risk_env.game_state[:,0],
            'units': self.risk_env.game_state[:,1],
            'reinforcement_max': self.risk_env.get_reinforcements(self.risk_env.current_player_id),
            'adjacencies': self.risk_env.adjacencies,
            'fortify_paths': self.risk_env.get_fortify_paths(self.risk_env.current_player_id)
        }
    
    def filter_fortify(self, fortify_action):
        """
        Replaces invalid fortify actions with valid ones
        """
        if self.risk_env.game_state[fortify_action[0],0] != self.risk_env.current_player_id:
            return 
        
    def calculate_reward(self):
        current_player_id = self.risk_env.current_player_id
        reward = np.sum(self.risk_env.game_state[self.risk_env.game_state[:,0] == current_player_id, 1])
        if self.risk_env.winner:
            reward += 1000
        return reward

    def print_game_state(self):
        print(self.risk_env.game_state)
        print(self.risk_env.adjacencies)
        print(self.risk_env.get_fortify_paths(self.risk_env.current_player_id))

if __name__ == "__main__":
    from risk_env import RiskEnv, Player
    risk_env = RiskEnv("two.json",[Player(0), Player(1)])
    env = RiskEnvWrapper(risk_env)
    env.reset()
    done = False
    while not done:
        action = env.action_space.sample()
        obs, reward, done, _, _ = env.step(action)
        print(reward)
        time.sleep(0.1)
    print(obs)