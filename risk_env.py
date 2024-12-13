import numpy as np
import json

class Player():
    def __init__(self, player_id, name=None, policy=None):
        self.player_id = player_id
        self.alive = True

class HumanPlayer(Player):
    def __init__(self, player_id, name=None):
        super().__init__(player_id, name)
        self.policy = None

class Actor(Player):
    def __init__(self, player_id, name=None, policy=None):
        super().__init__(player_id, name)
        self.policy = policy
                

def parse_board_layout(board):
    """
    Parse the board layout into the territories, adjacencies, and continents
    Parameters:
    board: a JSON object representing the board
    
    Returns:
    territories: a dictionary of territories and their corresponding indices
    adjacencies: a T x T numpy array representing the adjacency matrix of the territories
    continents: a dictionary of continents and their corresponding indices in territories (start and end index)
    """
    idx = 0
    territory_dict = {}
    continent_dict = {}
    for continent,contents in board['Continents'].items():
        continent_dict[continent] = (idx, idx + len(contents['territories']), contents['bonus'])
        for territory in contents['territories']:
            territory_dict[territory] = idx
            idx += 1
    adjacencies = np.zeros((idx, idx))
    for territory, contents in board['Territories'].items():
        for neighbor in contents['neighbors']:
            adjacencies[territory_dict[territory], territory_dict[neighbor]] = 1
    
    return territory_dict, adjacencies, continent_dict

def game_state_from_board(board):
    """
    Generate the initial game state from the board
    Parameters:
    board: a JSON object representing the board
    
    Returns:
    game_state: a T x 2 numpy array representing the game state (owner id, number of units)
    """
    game_state = []
    for _ in board['Territories']:
        game_state.append((0, 1))
    return game_state

class RiskEnv():
    def __init__(self, board, players):
        """
        Initialize the Risk environment
        Parameters:
        board: a JSON object representing the board
        players: a list of player objects

        Class variables:
        board: a JSON object representing the board
        game_state: a T x 2 numpy array representing the game state (owner id, number of units)
        adjacencies: a T x T numpy array representing the adjacency matrix of the territories
        territories: a dictionary of territories and their corresponding indices
        continents: a dictionary of continents and their corresponding territories
        winner: the winner of the game (player name)
        players: a dictionary of player objects referenced by their name
        
        Note: for efficiency, territories should be grouped by continent for faster ownership checks

        """
        board = json.load(open(board))
        self.players = players
        self.board = board # keep a copy for reset
        self.game_state = np.array(game_state_from_board(board))
        self.start_player_id = self.init_game_state()
        self.territories, self.adjacencies, self.continents = parse_board_layout(board)
        self.winner = None
        self.turn = 0
        self.current_player_id = self.start_player_id

    def init_game_state(self):
        """
        Initialize the game state, set all territories to random owners with one unit each.
        Each player will have an equal number of territories.
        """
        last_player_id = 0
        num_players = len(self.players)
        num_territories = len(self.game_state)
        indices = np.arange(num_territories)
        np.random.shuffle(indices)
        for i in range(num_territories):
            self.game_state[indices[i]] = (i % num_players, 1)
            last_player_id = i % num_players

        return (last_player_id + 1) % num_players 

    def reset(self):
        """
        Reset the game state to the initial state
        """
        self.game_state = np.array(game_state_from_board(self.board))
        self.start_player_id = self.init_game_state()
        self.winner = None
        self.turn = 0
        self.current_player_id = 0

    def check_winner(self):
        """
        Check if there is a winner and update the winner variable

        Returns:
        winner: boolean indicating whether there is a winner
        """
        if len(np.unique(self.game_state[:,0])) == 1:
            self.winner = np.unique(self.game_state[:,0])[0]
            return (True, self.winner)
        return (False, None)

    def get_winnning_player(self):
        """
        Get the winner of the game
        """
        return self.players[self.winner] if self.winner is not None else None
    
    def get_turn(self):
        """
        Get the current turn
        """
        return self.turn
    
    def state(self):
        """
        Get the current game state
        """
        return self.game_state
    
    def board_state(self):
        """
        Get the current board state in an easily visualizable format
        
        Returns:
        board_state: a list of tuples representing the territories and their owner and number of units
        in the format (territory, owner, units)
        """
        board_state = []
        for territory, id in self.territories.items():
            board_state.append((territory, self.game_state[id][0], self.game_state[id][1])) 
        return board_state
    
    def get_reinforcements(self, player_id):
        """
        Get the number of reinforcements for a player
        
        Parameters:
        player_id: the id of the player
        
        Returns:
        reinforcements: the number of reinforcements
        """
        reinforcements = 0
        for continent, (start, end, bonus) in self.continents.items():
            if np.all(self.game_state[start:end, 0] == player_id):
                reinforcements += bonus
        
        reinforcements += max(3, np.sum(self.game_state[self.game_state[:,0] == player_id, 1]) // 3)
        return reinforcements
    
    def reinforce(self, player_id, reinforce_action):
        """
        Reinforce a territory
        
        Parameters:
        player_id: the id of the player
        reinforce_action: a numpy array of shape (T,2) where the first column is the number
        of units to reinforce and the second column is ignored
        """
        # check if the player has enough reinforcements
        reinforcements = self.get_reinforcements(player_id)
        if np.sum(reinforce_action) > reinforcements:
            # print("Not enough reinforcements")
            return
        
        # check if the player is reinforcing territories they own
        if not np.all(reinforce_action[self.game_state[:,0] == player_id] >= 0):
            # print("Cannot reinforce territories you do not own")
            return

        # reinforce the territories
        self.game_state[:,1] += reinforce_action[:]

    def attack(self, player_id, attack_action):
        """
        Attack a territory
        
        Parameters:
        player_id: the id of the player
        attack_action: a numpy array of shape (T,2) where the first column is the number
        of units to attack with and the second column is the index of the territory to attack
        
        Returns:
        winner: boolean indicating whether there is a winner
        """
        # check if the player is attacking from territories they do not own
        # (if the first column has a value > 0, that column should be owned
        # by the player in the corresponding row of the game state)
        if not np.all(np.where(attack_action[:,0] > 0, self.game_state[:,0] == player_id, True)):
            # print("Cannot attack from territories you do not own")
            return False
        # check if the player is attacking territories they own
        # (all the indices in the second column should not be owned by the player)
        if not np.all(np.where(attack_action[:,0] > 0, self.game_state[attack_action[:,1] - 1,0] != player_id, True)):
            # print("Cannot attack territories you own")
            return False
        
        # check if the player is attacking adjacent territories
        # (if the first column has a value > 0, the index in the second column
        # should be adjacent to the corresponding row in the game state)
        for i in range(len(attack_action)):
            if attack_action[i,0] > 0 and not np.any(self.adjacencies[attack_action[i,1]] == 1):
                # print("Cannot attack non-adjacent territories")
                return False
        # if not np.all(np.where(attack_action[:,0] > 0, self.adjacencies[attack_action[:,1], self.game_state[:,0] == player_id], True)):
        #     print("Cannot attack non-adjacent territories")
        #     return False
        # check has enough units to attack in each territory
        if not np.all(attack_action[:,0] > 1):
            # print("Must have at least 2 units to attack")
            return False
        # check if the player is attacking with more or as many units than they have
        if not np.all(attack_action[:,0] < self.game_state[:, 1]):
            # print("Cannot attack with more or as many units than you have")
            return False
        # check if the player is attacking a territory that does not exist
        if not np.all(attack_action[:,1] < len(self.game_state)):
            # print("Cannot attack a territory that does not exist")
            return False
        # attack the territories, for each attack roll the maximum number of dice
        # for the attacker and defender and compare the results, subtract eliminated
        # units from the game state, the number of attacks from the attack action,
        # and repeat until the attacker has reached their attack target at each
        # territory in the attack action or the defender has no units left

        # loop while there are still attacks to be made
        while np.any(attack_action[:,0] > 0):
            # get the maximum number of attackers we can at each index
            attack_units = np.minimum(attack_action[:,0], 3)
            # get the maximum number of defenders we can at each index
            defend_units = np.minimum(self.game_state[attack_action[:,1],1], 2)
            # engage the attacking and defending units
            # we have to go in order, since multiple attacks can be made on the same territory
            for i in range(len(attack_action)):
                if attack_units[i] > 0 and self.game_state[i,0] != player_id:
                    # roll the dice
                    attack_dice = np.random.randint(1, 7, attack_units[i])
                    defend_dice = np.random.randint(1, 7, defend_units[i])
                    # sort the dice rolls
                    attack_dice = np.sort(attack_dice)
                    defend_dice = np.sort(defend_dice)
                    # compare the dice rolls
                    for j in range(min(attack_units[i], defend_units[i])):
                        if attack_dice[j] > defend_dice[j]:
                            # defender loses a unit
                            self.game_state[attack_action[i,1],1] -= 1
                        else:
                            # attacker loses a unit
                            attack_action[i,0] -= 1
                            self.game_state[i,1] -= 1
                    # if the defender has no units left, the attacker has conquered the territory
                    if self.game_state[attack_action[i,1],1] == 0:
                        self.game_state[attack_action[i,1],0] = player_id
                        # shift all remaining declared attack to the conquered territory
                        self.game_state[attack_action[i,1],1] = attack_action[i,0]
                        attack_action[i,0] = 0
                # if we are attacking our own territory, just move the units since we
                # must have already conquered the territory
                if self.game_state[i,0] == player_id:
                    self.game_state[i,1] += attack_action[i,0]
                    attack_action[i,0] = 0
        
        # check if the player has conquered all territories
        return self.check_winner()[0]
    
    def fortify(self, player_id, fortify_action):
        """
        Fortify a territory
        
        Parameters:
        player_id: the id of the player
        fortify_action: a numpy array of shape (T,2) where the first column is the number
        of units to fortify with and the second column is the index of the territory to fortify
        """
        src = fortify_action[1]
        dest = fortify_action[2]
        quantity = fortify_action[0]
        # check that the player is fortifying from a territory they own
        if self.game_state[src - 1,0] != player_id:
            raise ValueError("Cannot fortify from a territory you do not own")
            
        # check that the player is fortifying to a territory they own
        if self.game_state[dest - 1,0] != player_id:
            raise ValueError("Cannot fortify to a territory you do not own")
            
        # check that the player is fortifying connected territories
        if not self.is_link(player_id, self.adjacencies, src, dest):
            raise ValueError("Cannot fortify unconnected territories")
        
        fortify_quantity = min(quantity, self.game_state[src,1] - 1)
        self.game_state[src,1] -= fortify_quantity
        self.game_state[dest,1] += fortify_quantity
             
    def is_link(self, player_id, adjacencies, src, dest):
        """
        Check if two territories are connected by a single player in the graph

        Parameters:
        adjacencies: a T x T numpy array representing the adjacency matrix of the territories
        src: the index of the source territory
        dest: the index of the destination territory

        Returns:
        is_link: boolean indicating whether the territories are connected
        """
        visited = np.zeros(len(adjacencies))
        stack = [src]
        while stack:
            current = stack.pop()
            if current == dest:
                return True
            if visited[current] == 0:
                visited[current] = 1
                neighbors = np.where(adjacencies[current] == 1)[0]
                stack.extend([n for n in neighbors if self.game_state[n,0] == player_id])    
            return False
    
    def is_alive(self, player):
        """
        Check if a player is still alive
        
        Parameters:
        player: the name of the player
        
        Returns:
        is_alive: boolean indicating whether the player is alive
        """
        return np.any(self.game_state[:,0] == player)
    
    def get_player_id(self, player):
        """
        Get the player id from the player name
        
        Parameters:
        player: the name of the player
        
        Returns:
        player_id: the id of the player
        """
        return [p.name for p in self.players].index(player)

    def get_fortify_paths(self, player_id):
        """
        Get the fortify paths for a player
        
        Parameters:
        player_id: the id of the player
        
        Returns:
        fortify_paths: a T x T numpy array representing the fortify paths
        """
        fortify_paths = np.zeros((len(self.game_state), len(self.game_state)))
        # each entry should be the number of units on the source - 1
        for i in range(len(self.game_state)):
            if self.game_state[i,0] == player_id:
                # only add the entry if the destination is owned and connected
                for j in range(len(self.game_state)):
                    if self.game_state[j,0] == player_id and self.is_link(player_id, self.adjacencies, i, j):
                        fortify_paths[i,j] = self.game_state[i,1] - 1

        return fortify_paths