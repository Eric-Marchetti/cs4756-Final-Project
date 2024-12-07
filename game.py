from random import random, shuffle, randint
import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from typing import List

class Player:
    def __init__(self, name, color = "blue", ishuman = True):
        self.color = color
        self.ishuman = ishuman
        self.name = name

    def to_dict(self):
        return {"name": self.name, "color": self.color, "ishuman": self.ishuman, "territories": [], "reinforcements": 0, "cards": []}

class Game:
    def __init__(self, players : List[Player], risk_map, vis = False):
        '''
        Initializes the game with a list of players and a risk map.
        The risk map is a JSON file that contains the territories and continents of the game.
        '''
        self.players = {}
        for i in range(len(players)):
            self.players[i] = players[i].to_dict() # stores players by player id (assigned at the beginning of the game)
        self.current_player_id = 0
        self.turn = 0
        self.num_trade_ins = 0
        self.risk_map = json.load(open(risk_map))
        self.vis = vis
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.G = nx.Graph()
        self.pos = {}

        for territory, data in self.risk_map["Territories"].items(): 
            self.G.add_node(territory) 
            self.pos[territory] = data['position'] 
            for neighbor in data['neighbors']: 
                self.G.add_edge(territory, neighbor)

    def initialize_map(self):
        '''
        Initializes the game by assigning territories to players and placing one unit on each territory.

        The territories are shuffled and assigned to players in a round-robin fashion.
        '''
        shuffled_territories = list(self.risk_map["Territories"].keys())
        shuffle(shuffled_territories)
        for territory in shuffled_territories:
            self.risk_map["Territories"][territory]["owner"] = self.current_player_id # territory ownership is assigned by player id 
            self.players[self.current_player_id]["territories"].append(territory) # list for quick length checking
            self.risk_map["Territories"][territory]["units"] = 1
            self.current_player_id = (self.current_player_id + 1) % len(self.players)
        return

    def next_player(self):
        '''
        Advances the turn to the next player in the list of players.
        '''
        self.current_player_id = (self.current_player_id + 1) % len(self.players)
        if self.current_player_id == 0:
            self.turn += 1

    def current_player_name(self):
        '''
        Returns the name of the current player.
        '''
        return self.players[self.current_player_id]['name']

    def reinforce(self, territory, units):
        '''
        Allows a player to place units on a territory they own.
        The player must own the territory and have units to place.

        Updates the number of remaining reinforcements the player has.
        '''
        if territory not in self.risk_map["Territories"]:
            print("Invalid reinforce: territory does not exist.")
            return
        
        if self.risk_map["Territories"][territory]["owner"] != self.current_player_id:
            print("Invalid reinforce: territory must be owned by the player.")
            return
        
        if self.players[self.current_player_id]['reinforcements'] < units:
            print("Invalid reinforce: player does not have enough units.")
            return
        
        self.risk_map["Territories"][territory]["units"] += units
        self.players[self.current_player_id]['reinforcements'] -= units
        return

    def reinforce_batch(self, territories):
        '''
        Allows a player to place units on multiple territories they own using a dictionary.
        The player must own the territories and have units to place.

        Updates the number of remaining reinforcements the player has.
        '''
        total_units = 0
        for units in territories.values():
            total_units += units

        if self.players[self.current_player_id]['reinforcements'] < total_units:
            print("Invalid reinforce: player does not have enough units.")

        for territory, units in territories.items():
            if territory not in self.risk_map["Territories"]:
                print("Invalid reinforce: territory does not exist.")
                return
            
            if self.risk_map["Territories"][territory]["owner"] != self.current_player_id:
                print("Invalid reinforce: territory must be owned by the player.")
                return
            
            self.risk_map["Territories"][territory]["units"] += units

        self.players[self.current_player_id]['reinforcements'] -= total_units

    def get_reinforcements(self):
        '''
        Returns the number of reinforcements the current player has.
        '''
        return self.players[self.current_player_id]['reinforcements']

    def can_attack(self):
        '''
        Returns True if the current player can attack another player, False otherwise.
        '''
        for territory in self.players[self.current_player_id]['territories']:
            for neighbor in self.risk_map["Territories"][territory]["neighbors"]:
                if self.risk_map["Territories"][neighbor]["owner"] != self.current_player_id and self.risk_map["Territories"][territory]["units"] > 1:
                    return True

    def attack(self, attacking_territory, defending_territory):
        '''
        Allows a player to attack a territory owned by another player.
        The attacking player must own the attacking territory and the defending territory must be owned by another player.
        The attacking player can only attack territories that are adjacent to the attacking territory.
        The attacking player can roll up to 3 dice and the defending player can roll up to 2 dice.
        The units in the attacking territory are reduced by the number of units lost in the attack.
        If the defending territory is conquered, the attacking player takes control of the territory and moves the remaining units.
        '''
        if attacking_territory not in self.risk_map["Territories"] or defending_territory not in self.risk_map["Territories"]:
            print("Invalid attack: territories do not exist.")

        if defending_territory not in self.risk_map["Territories"][attacking_territory]["neighbors"]:
            print("Invalid attack: attacking territory must be adjacent to the defending territory.")
            return

        if self.risk_map["Territories"][attacking_territory]["owner"] != self.current_player_id:
            print("Invalid attack: attacking territory must be owned by the player.")
            return
        
        if self.risk_map["Territories"][defending_territory]["owner"] == self.current_player_id:
            print("Invalid attack: defending territory cannot be owned by the player.")
            return

        attacker_rolls = min(self.risk_map["Territories"][attacking_territory]["units"] - 1, 3)
        defender_rolls = min(self.risk_map["Territories"][defending_territory]["units"], 2)
        
        attacker_dice = sorted([randint(1, 6) for _ in range(attacker_rolls)], reverse=True)
        defender_dice = sorted([randint(1, 6) for _ in range(defender_rolls)], reverse=True)

        for i in range(min(attacker_rolls, defender_rolls)):
            if attacker_dice[i] > defender_dice[i]:
                self.risk_map["Territories"][defending_territory]["units"] -= 1
            else:
                self.risk_map["Territories"][attacking_territory]["units"] -= 1

            if self.risk_map["Territories"][defending_territory]["units"] <= 0:
                previous_owner = self.risk_map["Territories"][defending_territory]["owner"]
                self.risk_map["Territories"][defending_territory]["owner"] = self.current_player_id
                self.players[previous_owner]["territories"].remove(defending_territory)
                self.players[self.current_player_id]["territories"].append(defending_territory)
                self.risk_map["Territories"][defending_territory]["units"] = attacker_rolls - i - 1
                self.risk_map["Territories"][attacking_territory]["units"] -= attacker_rolls - i - 1
                break

    def fortify(self, origin_territory, destination_territory, units):
        '''
        Moves units from one territory to another, as long as the origin territory is owned by the player.
        If the origin and destination territories are not owned by the player, the move is invalid.
        If the player tries to move all the units from the origin territory, the move is invalid.
        '''

        if self.risk_map["Territories"][origin_territory]["owner"] != self.current_player_id or self.risk_map["Territories"][destination_territory]["owner"] != self.current_player_id:
            print("Invalid fortify: origin and destination territories must be owned by the player.")
            return
        
        if units >= self.risk_map["Territories"][origin_territory]["units"]:
            print("Invalid fortify: must leave at least one unit in the origin territory.")
            return

        self.risk_map["Territories"][origin_territory]["units"] -= units
        self.risk_map["Territories"][destination_territory]["units"] += units

    def turn_in_cards(self, player, cards):
        '''
        Allows a player to trade exactly 3 cards for units, according to the following rules:
        - The player must own all the cards they are trading in
        - The cards must be either all different or all the same
        - The number of units received is determined by the following formula:
            - 4 + 2 * (number of trade-ins) if the number of trade-ins is less than 5
            - 15 if the number of trade-ins is 6
            - 5 * (number of trade-ins) - 15 if the number of trade-ins is greater than 6
        
        Increments the number of trade-ins by 1 and adds the units to the player's reinforcements.
        '''

        if len(cards) != 3:
            print("Invalid trade: must trade exactly 3 cards.")
            return 0

        if not all(card in self.players[self.current_player_id]['cards'] for card in cards):
            print("Invalid trade: player does not own all these cards.")
            return 0
        
        if len(set(cards)) == 1 or len(set(cards)) == 3:
            for card in cards:
                self.players[self.current_player_id]['cards'].remove(card)
            
        if self.num_trade_ins < 5:
            num_troops = 4 + 2 * self.num_trade_ins
        elif self.num_trade_ins == 6:
            num_troops = 15
        else:
            num_troops = 5 * self.num_trade_ins - 15

        self.num_trade_ins += 1
        self.players[self.current_player_id]['reinforcements'] += num_troops

    def check_win(self):
        '''
        Returns True if there is only one player left in the game, False otherwise.
        '''
        if len(self.players) == 1:
            return True
        return False
    
    def get_winner(self):
        '''
        Returns the name of the first player in the list of players.
        '''
        return next(iter(self.players.values()))['name']

    def check_elimination(self):
        '''
        Checks if any players have been eliminated by losing all their territories.
        Removes any eliminated players from the game.
        '''
        for id, player in self.players.items():
            if len(player['territories']) == 0:
                print(player['name'] + " has been eliminated.")
                del self.players[id]
                
    def check_continent(self, continent):
        '''
        Returns the id of player who controls an entire continent or -1 if no player controls the continent
        '''
        for id, player in self.players.items():
            if all(territory in player['territories'] for territory in self.risk_map['Continents'][continent]["territories"]):
                return id
        return -1
    
    def get_continent_bonus(self, continent):
        '''
        Returns the bonus for controlling a continent
        '''
        return self.risk_map["Continents"][continent]["bonus"]

    def check_elimination_bonus(self, killing_player_id, eliminated_player_id):
        '''
        Sends the cards of an eliminated player to the killing player if they have any.
        '''
        if self.players[eliminated_player_id]['cards'] == []:
           self.players[killing_player_id].cards += self.players[eliminated_player_id].cards
        eliminated_player_cards = self.players[eliminated_player_id]['cards']
        if len(eliminated_player_cards) > 0:
            self.players['killing_player_id']['cards'] += eliminated_player_cards
        return

    def calculate_reinforcements(self):
        '''
        Calculates the reinforcements a player receives at the beginning of their turn
        according to the following rules: a player receives 3 units or the number of territories
        they control divided by 3, whichever is greater. Additionally, a player receives a bonus
        for controlling continents. The bonus for each continent is determined by the Continents
        dictionary in the risk_map. The bonus is added to the player's reinforcements if they control
        the entire continent.
        '''
        reinforcements = max(3, len(self.players[self.current_player_id]['territories']) // 3)
        for continent in self.risk_map['Continents']:
            if self.check_continent(continent) == self.current_player_id:
                reinforcements += self.get_continent_bonus(continent)
        return reinforcements
    
    def get_neighbors(self, territory):
        '''
        Returns a list of the neighbors of a territory
        '''
        return self.risk_map['Territories'][territory]['neighbors']
    
    def get_territories(self):
        '''
        Returns a list of the territories owned by the current player
        '''
        return self.players[self.current_player_id]['territories']

    def update_visualization(self): 
        labels = {} 
        colors = []
        for territory, data in self.risk_map["Territories"].items(): 
            labels[territory] = f"{territory}\n{data['units']} troops" 
            if "owner" in data: 
                colors.append(self.players[data['owner']]['color']) 
            else: 
                colors.append("gray") 
        self.ax.clear() 
        nx.draw(self.G, self.pos, labels=labels, node_color=colors, with_labels=True, ax=self.ax) 
        self.ax.set_title(f"{self.players[self.current_player_id]['name']}'s turn") 
        plt.pause(0.1) # Pause for a short time to update the plot

    def move_to_reinforce_phase(self):
        '''
        Moves the game to the reinforce phase by calculating the reinforcements for the current player.
        '''
        self.players[self.current_player_id]['reinforcements'] = self.calculate_reinforcements()
        if self.vis:
            self.update_visualization()
        return

    def move_to_attack_phase(self):
        '''
        Moves the game to the attack phase.
        '''
        if self.vis:
            self.update_visualization()
        return
    
    def move_to_fortify_phase(self):
        '''
        Moves the game to the fortify phase.
        '''
        if self.vis:
            self.update_visualization()
        return

class Card:
    def __init__(self, territory, unit_type):
        self.territory = territory
        self.unit_type = unit_type
