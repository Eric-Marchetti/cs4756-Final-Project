from random import random, shuffle
import json
import networkx as nx
import matplotlib.pyplot as plt

class Game:
    def __init__(self, players, risk_map):
        self.players = players
        self.current_player_id = 0
        self.turn = 0
        #self.turn_phase = "reinforce"
        self.num_trade_ins = 0
        self.risk_map = json.load(open(risk_map))

    def initialize_map(self):
        shuffled_territories = list(self.risk_map["Territories"].keys())
        shuffle(shuffled_territories)
        for territory in shuffled_territories:
            self.risk_map["Territories"][territory]["owner"] = self.players[self.current_player_id]
            self.risk_map["Territories"][territory]["units"] = 1
            self.players[self.current_player_id].add_territory(territory, 1)
            self.players[self.current_player_id].units += 1
            self.current_player_id = (self.current_player_id + 1) % len(self.players)

    def next_player(self):
        self.current_player_id = (self.current_player_id + 1) % len(self.players)
        if self.current_player_id == 0:
            self.turn += 1

    def current_player(self):
        return self.players[self.current_player_id]

    def reinforce(self, territory, units):
        self.current_player().add_units(territory, units)
        self.reinforcements -= units

    def attack(self, attacking_player, attacking_territory, defending_player, defending_territory):
        attacker_rolls = min(attacking_player.get_units_in_territory(attacking_territory), 3)
        defender_rolls = min(defending_player.get_units_in_territory(defending_territory), 2)

        attacker_dice = [random.randint(1, 6) for i in range(attacker_rolls)].sort(reverse=True)
        defender_dice = [random.randint(1, 6) for i in range(defender_rolls)].sort(reverse=True)

        for i in range(min(attacker_rolls, defender_rolls)):
            if attacker_dice[i] > defender_dice[i]:
                defending_player.remove_units(defending_territory, 1)
                self.risk_map["Territories"][defending_territory]["units"] -= 1
            else:
                attacking_player.remove_units(attacking_territory, 1)
                self.risk_map["Territories"][attacking_territory]["units"] -= 1

            if self.risk_map["Territories"][defending_territory]["units"] <= 0:
                self.risk_map["Territories"][defending_territory]["owner"] = attacking_player
                self.risk_map["Territories"][defending_territory]["units"] = attacker_rolls - i - 1
                attacking_player.add_territory(defending_territory, attacker_rolls - i - 1)
                defending_player.remove_territory(defending_territory)
                break

        # add logic for territory takeover here

    def fortify(self, player, origin_territory, destination_territory, units):
        player.remove_units(origin_territory, units)
        self.risk_map["Territories"][origin_territory]["units"] -= units
        player.add_units(destination_territory, units)
        self.risk_map["Territories"][destination_territory]["units"] += units

    def turn_in_cards(self, player, cards):
        if len(cards) != 3:
            print("Invalid trade: must trade exactly 3 cards.")
            return 0

        if not all(card in player.getCards for card in cards):
            print("Invalid trade: player does not own all these cards.")
            return 0
        
        if len(set(cards)) == 1 or len(set(cards)) == 3:
            for card in cards:
                player.cards.remove(card)
            
        if self.num_trade_ins < 5:
            num_troops = 4 + 2 * self.num_trade_ins
        elif self.num_trade_ins == 6:
            num_troops = 15
        else:
            num_troops = 5 * self.num_trade_ins - 15

        self.num_trade_ins += 1
        return num_troops


    def check_win(self):
        if len(self.players) == 1:
            return True
    
    def get_winner(self):
        return self.players[0]

    def check_elimination(self):
        for player in self.players:
            if len(player.territories) == 0:
                print(player.name + " has been eliminated.")
                self.players.remove(player)
                
    def check_continent(self, continent):
        for player in self.players:
            if all(territory in player.territories for territory in self.risk_map['Continents'][continent]["territories"]):
                return player
    
    def get_continent_bonus(self, continent):
        return self.risk_map["Continents"][continent]["bonus"]

    def check_elimination_bonus(self, killing_player, eliminated_player):
        if eliminated_player.territories: # if they still have land they not eliminated
            return
        eliminated_player_cards = eliminated_player.getCards()
        if len(eliminated_player_cards) > 0:
            killing_player.cards += eliminated_player_cards

    def calculate_reinforcements(self, player):
        reinforcements = max(3, len(player.territories) // 3)
        for continent in self.risk_map['Continents']:
            if self.check_continent(continent) == player:
                reinforcements += self.get_continent_bonus(continent)
        return reinforcements
    
    def get_neighbors(self, territory):
        return self.risk_map['Territories'][territory]['neighbors']
    
    def visualize(self):
        G = nx.Graph()
        pos = {}
        labels = {}
        colors = []

        for territory,data in self.risk_map["Territories"].items():
            G.add_node(territory)
            pos[territory] = data['position']
            labels[territory] = f"{territory}\n{data['units']} troops"
            if "owner" in data:
                colors.append(data['owner'].color)
            else:
                colors.append("gray")
            for neighbor in data['neighbors']:
                G.add_edge(territory, neighbor)
        plt.figure(figsize=(10,10))
        nx.draw(G, pos, labels=labels, node_color=colors, with_labels=True)
        plt.show()
    
class Card:
    def __init__(self, territory, unit_type):
        self.territory = territory
        self.unit_type = unit_type
