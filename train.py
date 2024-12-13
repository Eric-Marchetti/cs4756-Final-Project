from risk_env import RiskEnv, Player, RiskEnvWrapper
from trinet import TriNet
import json
import argparse

def main(args):
    players = [Player(player["name"], player["model_path"]) for player in json.load(open(args.players))["players"]]
    board = json.load(open(args.board))
    risk_env = RiskEnv(board, players)
    env = RiskEnvWrapper(risk_env)
    # Initialize and train TriNet
    if args.load:
        trinet = TriNet(env, model_path=args.load, visualize=True)
    else:
        trinet = TriNet(env)
    
    trinet.train(100000)
    trinet.save_model("models/trinet")

if __name__ == "__main__": # Initialize environment and players 
    parser = argparse.ArgumentParser()
    parser.add_argument("--board", type=str, help="Path to board configuration JSON")
    parser.add_argument("--players", type=str, help="Path to players configuration JSON")
    parser.add_argument("--load", type=str, help="Path to model to load")

    args = parser.parse_args()
    main(args)