import argparse
import time
import numpy as np
import matplotlib.pyplot as plt

from risk_env import RiskEnv, Player
from risk_env_wrapper import RiskEnvWrapper
from trinet import TriNet
from risk_graph_2 import visualize_game_state  # Assume you saved visualize_game_state in visualization.py

def simulate(args):
    # Create players and environment
    players = [Player(i) for i in range(2)]
    risk_env = RiskEnv(args.board, players)
    env = RiskEnvWrapper(risk_env, visualize=False, max_episode_steps=50)  # Adjust max steps if needed
    plt.ion()
    # Load model if provided, else use random actions
    if args.model:
        trinet = TriNet(env, model_path=args.model)
        model = trinet.agent
        print("Model loaded from:", args.model)
    else:
        model = None
        print("No model provided, using random actions.")

    obs, info = env.reset(seed=args.seed)
    visualize_game_state(env, title="Initial Game State")

    step_count = 0
    done = False

    while not done and step_count < args.max_steps:
        step_count += 1
        if model is not None:
            # Use the trained model to predict actions
            action, _ = model.predict(obs, deterministic=True)
        else:
            # Random action
            action = env.action_space.sample()

        obs, reward, done, truncated, info = env.step(action)
        
        # Visualize the new state
        plt.close('all')  # Close previous plots if needed
        visualize_game_state(env, title=f"Step {step_count}, Reward: {reward}")
        
        if args.delay > 0:
            plt.pause(args.delay)

    print("Simulation ended.")
    if done:
        print("Episode finished because 'done' = True.")
    else:
        print("Max steps reached without episode termination.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--board", type=str, default="very_small_board.json", help="Path to board configuration JSON")
    parser.add_argument("--model", type=str, default=None, help="Path to a trained model to load. If not provided, random actions will be used.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for environment reset.")
    parser.add_argument("--max_steps", type=int, default=100, help="Maximum number of steps to simulate.")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay in seconds between steps for visualization.")
    args = parser.parse_args()

    simulate(args)