import numpy as np
import gymnasium as gym
from gymnasium import spaces
import networkx as nx
import matplotlib.pyplot as plt
import time

class RiskEnvWrapper(gym.Env): 
    def __init__(self, risk_env, visualize=False, max_episode_steps = 200): 
        super(RiskEnvWrapper, self).__init__()
        self.risk_env = risk_env
        self.T = risk_env.game_state.shape[0]
        self.visualize = visualize
        self.max_episode_steps = max_episode_steps
        self.current_step = 0

        # self.action_space = spaces.Dict({
        #     'reinforce': spaces.Box(low=0, high=1, shape=(self.T,), dtype=np.float32),
        #     'attack_units': spaces.Box(low=0, high=self.T, shape=(self.T,self.T), dtype=np.int32),
        #     'fortify_units': spaces.Box(low=0, high=self.T, shape=(self.T,self.T), dtype=np.int32)
        # })
        self.action_space = spaces.Box( low=0, high=1, shape=(self.T + self.T * self.T + self.T * self.T,), dtype=np.float32 )
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
        self.current_step = 0
        return self._get_obs(), {}
    
    def step(self, action):
        if self.visualize:
            self.print_game_state()
        # reinforce_action = action['reinforce']
        # attack_units = action['attack_units']
        # fortify_units = action['fortify_units']
        reinforce_action = action[:self.T] 
        attack_units = (action[self.T:self.T + self.T * self.T].reshape((self.T, self.T)) * (self.T + 1)).astype(np.int32)
        fortify_units = (action[self.T + self.T * self.T:].reshape((self.T, self.T)) * (self.T + 1)).astype(np.int32)

        # Convert reinforce_action from distribution to number of units
        # print(self.risk_env.get_reinforcements(self.risk_env.current_player_id))
        # print(reinforce_action)
        # Do the same for attack_units and fortify_units
            
        # reinforce_action, attack_units, fortify_units = self.filter_actions(reinforce_action, attack_units, fortify_units)
        reinforce_action, attack_units, fortify_units = self.filter_actions(reinforce_action, attack_units, fortify_units)

        self.risk_env.reinforce(self.risk_env.current_player_id, reinforce_action)
        # self.print_game_state()
        # print(attack_units)
        self.risk_env.winner = self.risk_env.attack(self.risk_env.current_player_id, attack_units)
        # print(fortify_units)
        self.risk_env.fortify(self.risk_env.current_player_id, fortify_units)
        

        # next player
        self.risk_env.current_player_id = (self.risk_env.current_player_id + 1) % len(self.risk_env.players)

        self.current_step += 1
        done = self.risk_env.check_winner()[0]
        if not done and self.current_step >= self.max_episode_steps:
            done = True

        return self._get_obs(), self.calculate_reward(), done, False, {}
    
    def _get_obs(self):
        obs = {
            'owners': self.risk_env.game_state[:,0],
            'units': self.risk_env.game_state[:,1],
            'reinforcement_max': self.risk_env.get_reinforcements(self.risk_env.current_player_id),
            'adjacencies': self.risk_env.adjacencies,
            'fortify_paths': self.risk_env.get_fortify_paths(self.risk_env.current_player_id)
        }

        # Example normalization: Assume max_units = 50 as a heuristic
        max_units = 50.0
        obs['units'] = np.clip(obs['units'], 0, max_units) / max_units
        # Similarly, normalize reinforcement_max by some scale, say max 20
        obs['reinforcement_max'] = np.clip(obs['reinforcement_max'], 0, 20) / 20.0

        return obs
    
    def filter_actions(self, reinforce_action, attack_units, fortify_units):
        # cannot reinforce, attack, or fortify on rows that are not owned
        reinforce_action = reinforce_action * (self.risk_env.game_state[:,0] == self.risk_env.current_player_id) 
        reinforce_action = reinforce_action / np.where(np.sum(reinforce_action) > 0, np.sum(reinforce_action), 1) 
        reinforce_action = np.nan_to_num(reinforce_action) 
        reinforce_action = (reinforce_action * (self.risk_env.get_reinforcements(self.risk_env.current_player_id))).astype(np.int32)
        # also cannot attack or fortify from rows that have under 2 units
        # also cannot attack TO columns that are owned, or fortify TO columns that aren't owned

        # set all values >= 0
        # reinforce_action = np.maximum(reinforce_action, 0)
        # attack_units = np.maximum(attack_units, 0)
        # fortify_units = np.maximum(fortify_units, 0)

        # for i in range(self.T): 
        #     for j in range(self.T): 
        #         if self.risk_env.adjacencies[i,j] == 0 or self.risk_env.game_state[i,1] < 2: 
        #             attack_units[i,j] = 0 
        #             fortify_units[i,j] = 0 
        #         elif self.risk_env.game_state[i,0] != self.risk_env.current_player_id: 
        #             attack_units[i,j] = 0 
        #             fortify_units[i,j] = 0
        #         elif self.risk_env.game_state[j,0] == self.risk_env.current_player_id:
        #             attack_units[i,j] = 0
        #         if self.risk_env.game_state[j,0] != self.risk_env.current_player_id or not self.risk_env.is_link(self.risk_env.current_player_id, self.risk_env.adjacencies, i, j): 
        #             fortify_units[i,j] = 0 
        for i in range(self.T): 
            for j in range(self.T): 
                if self.risk_env.adjacencies[i, j] == 0 or self.risk_env.game_state[i, 1] < 2: 
                    attack_units[i, j] = 0
                    fortify_units[i, j] = 0 
                if self.risk_env.game_state[i, 0] != self.risk_env.current_player_id or self.risk_env.game_state[j, 0] == self.risk_env.current_player_id: 
                    attack_units[i, j] = 0 
                if (self.risk_env.game_state[i, 0] != self.risk_env.current_player_id 
                    or self.risk_env.game_state[j, 0] != self.risk_env.current_player_id
                    or not self.risk_env.is_link(self.risk_env.current_player_id, self.risk_env.adjacencies, i, j)):
                    fortify_units[i, j] = 0

        # print('attack_units: ', attack_units)
    
        # for i in range(self.T): 
        #     attack_units[i] = np.minimum(attack_units[i], self.risk_env.game_state[i,1] - 1) 
        #     if np.sum(attack_units[i]) > self.risk_env.game_state[i,1] - 1: 
        #         attack_units[i] = (attack_units[i] / np.sum(attack_units[i]) * (self.risk_env.game_state[i,1] - 1)).astype(np.int32) 
        #         fortify_units[i] = np.minimum(fortify_units[i], self.risk_env.game_state[i,1] - 1) 
        #         if np.sum(fortify_units[i]) > self.risk_env.game_state[i,1] - 1: 
        #             fortify_units[i] = (fortify_units[i] / np.sum(fortify_units[i]) * (self.risk_env.game_state[i,1] - 1)).astype(np.int32) 
        for i in range(self.T):
            # For attacks, cannot use more than (current units - 1)
            max_units_available = self.risk_env.game_state[i, 1] - 1
            if max_units_available < 0:
                max_units_available = 0
            if np.sum(attack_units[i]) > max_units_available:
                total = np.sum(attack_units[i])
                if total > 0:
                    attack_units[i] = (attack_units[i] / total * max_units_available).astype(np.int32)

            # Similarly for fortify, cannot move more units than (current units - 1)
            if np.sum(fortify_units[i]) > max_units_available:
                total = np.sum(fortify_units[i])
                if total > 0:
                    fortify_units[i] = (fortify_units[i] / total * max_units_available).astype(np.int32)

        return reinforce_action, attack_units, fortify_units
    
    def calculate_reward(self):
        current_player_id = self.risk_env.current_player_id
        reward = np.sum(self.risk_env.game_state[:,0] == current_player_id) / self.T
        if self.risk_env.winner:
            reward += 1.0
        return reward

    def print_game_state(self):
        print("Current player: ", self.risk_env.current_player_id)
        for i in range(self.T):
            print(f"Territory {i}: Owner {self.risk_env.game_state[i,0]}, Units {self.risk_env.game_state[i,1]}", end=" | ")
            if (i + 1) % 5 == 0:  # Adjust the number 5 to change the grid width
                print()
        print()
        # print('adjacencies: ', self.risk_env.adjacencies)
        # print(self.risk_env.get_fortify_paths(self.risk_env.current_player_id))

if __name__ == "__main__":
    from risk_env import RiskEnv, Player
    risk_env = RiskEnv("small.json",[Player(0), Player(1)])
    env = RiskEnvWrapper(risk_env, visualize=True)
    env.reset()
    done = False
    while not done:
        action = env.action_space.sample()
        obs, reward, done, _, _ = env.step(action)
        print(reward)
        time.sleep(0.5)
    print(obs)