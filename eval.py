from risk_env import RiskEnv, Player, RiskEnvWrapper
import argparse
import json

def main(args):
    board = json.load(open(args.board))
    players = [Player(player["name"], player["model_path"]) for player in json.load(open(args.players))["players"]]
    risk_env = RiskEnv(board, players)
    env = RiskEnvWrapper(risk_env, visualize=True)
    env.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--board", type=str, help="Path to board configuration JSON")
    parser.add_argument("--players", type=str, help="Path to players configuration JSON")

    args = parser.parse_args()
    main(args)    