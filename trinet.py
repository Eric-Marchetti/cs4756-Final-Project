import os
import torch
import numpy as np
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
class TriNet(nn.Module):
    """
    A neural network model that uses the PPO algorithm to learn reinforcement attack and fortify strategies for the game of Risk.
    This network operates under the assumption that reinforcement, attacking, and fortification must be declared at the start of
    the turn, and that the player must follow through with their declared actions (with fortification continuing to the greatest
    extent possible). The network is trained using the PPO algorithm from the stable_baselines3 library.
    """
    def __init__(self, env, model_path=None):
        super(TriNet, self).__init__()
        self.env = DummyVecEnv([lambda: env])
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        learning_rate = 0.0001 
        clip_range = 0.1 
        entropy_coef = 0.01
        
        self.agent = PPO("MultiInputPolicy", self.env, verbose=1, learning_rate=learning_rate, clip_range=clip_range, ent_coef=entropy_coef)
        self.agent.policy.to(self.device)
        if model_path and model_path != "random" and os.path.exists(model_path):
            self.load_model(model_path)
        self.random = model_path == "random"

    def train(self, num_steps):
        if self.random:
            return
        self.agent.learn(total_timesteps=num_steps)
        
    def predict(self, obs):
        return self.agent.predict(obs)
    
    def get_action(self, obs):
        if self.random: 
            return self.env.action_space.sample() 
        action, _ = self.predict(obs) 
        T = obs["owners"].shape[0] 
        # reinforce = action['reinforce'] 
        # attack_units = action['attack_units'] 
        # fortify_units = action['fortify_units']
        reinforce = action[:T]
        attack_units = (action[T:T + T * T].reshape((T, T)) * (T + 1)).astype(np.int32)
        fortify_units = (action[T + T * T:].reshape((T, T)) * (T + 1)).astype(np.int32) 
        # return { 'reinforce': reinforce, 'attack_units': attack_units, 'fortify_units': fortify_units }
        return np.concatenate((reinforce, attack_units.flatten(), fortify_units.flatten()))

    def save_model(self, path):
        if self.random:
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.agent.save(path)

    def load_model(self, path):
        if self.random:
            return
        self.agent = PPO.load(path, self.env)
        self.agent.policy.to(self.device)