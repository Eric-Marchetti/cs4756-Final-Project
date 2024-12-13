import numpy as np
from risk_graph import Graph

class Game():
    def __init__(self, board, num_players):
        self.graph = Graph(board)
        self.num_players = num_players
        self.players = [Player(i) for i in range(num_players)]

    def random_init(self):
        indices = np.arange(len(self.graph.territories))
        np.random.shuffle(indices)
        for i, idx in enumerate(indices):
            self.graph.set_owner(idx, i % self.num_players)

    def display(self):
        self.graph.display()




if __name__ == "__main__":
    game = Game("two.json", 2)
    game.random_init()
    game.display()