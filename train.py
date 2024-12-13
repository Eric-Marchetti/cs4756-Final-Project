from risk_env import RiskEnv, Player
from risk_env_wrapper import RiskEnvWrapper
from trinet import TriNet
import json
import argparse

def main(args):
    players = [Player(i) for i in range(2)]
    risk_env = RiskEnv(args.board, players)
    env = RiskEnvWrapper(risk_env)
    # Initialize and train TriNet
    if args.load:
        trinet = TriNet(env, model_path=args.load, visualize=False)
    else:
        trinet = TriNet(env,model_path="models/trinet")
    
    trinet.train(100000)
    import matplotlib.pyplot as plt

    # Assuming trinet.train() returns a list of training losses
    losses = trinet.train(100000)

    # Plot the training loss over time
    plt.plot(losses)
    plt.xlabel('Training Steps')
    plt.ylabel('Loss')
    plt.title('Training Loss Over Time')
    plt.show()
    trinet.save_model("models/trinet")

if __name__ == "__main__": # Initialize environment and players 
    parser = argparse.ArgumentParser()
    parser.add_argument("--board", type=str, help="Path to board configuration JSON")
    parser.add_argument("--players", type=str, help="Path to players configuration JSON")
    parser.add_argument("--load", type=str, help="Path to model to load")

    args = parser.parse_args()
    main(args)