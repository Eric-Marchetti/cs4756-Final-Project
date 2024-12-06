from random import random
risk_map = {
    "North America": {
        "Alaska": {"neighbors": ["Northwest Territory", "Alberta", "Kamchatka"], "continent": "North America"},
        "Northwest Territory": {"neighbors": ["Alaska", "Greenland", "Alberta", "Ontario"], "continent": "North America"},
        "Greenland": {"neighbors": ["Northwest Territory", "Ontario", "Quebec", "Iceland"], "continent": "North America"},
        "Alberta": {"neighbors": ["Alaska", "Northwest Territory", "Ontario", "Western United States"], "continent": "North America"},
        "Ontario": {"neighbors": ["Northwest Territory", "Alberta", "Western United States", "Eastern United States", "Quebec", "Greenland"], "continent": "North America"},
        "Quebec": {"neighbors": ["Ontario", "Eastern United States", "Greenland"], "continent": "North America"},
        "Western United States": {"neighbors": ["Alberta", "Ontario", "Eastern United States", "Central America"], "continent": "North America"},
        "Eastern United States": {"neighbors": ["Ontario", "Quebec", "Western United States", "Central America"], "continent": "North America"},
        "Central America": {"neighbors": ["Western United States", "Eastern United States", "Venezuela"], "continent": "North America"},
    },
    "South America": {
        "Venezuela": {"neighbors": ["Central America", "Brazil", "Peru"], "continent": "South America"},
        "Brazil": {"neighbors": ["Venezuela", "Peru", "Argentina", "North Africa"], "continent": "South America"},
        "Peru": {"neighbors": ["Venezuela", "Brazil", "Argentina"], "continent": "South America"},
        "Argentina": {"neighbors": ["Peru", "Brazil"], "continent": "South America"},
    },
    "Europe": {
        "Iceland": {"neighbors": ["Greenland", "Great Britain", "Scandinavia"], "continent": "Europe"},
        "Great Britain": {"neighbors": ["Iceland", "Scandinavia", "Northern Europe", "Western Europe"], "continent": "Europe"},
        "Scandinavia": {"neighbors": ["Iceland", "Great Britain", "Northern Europe", "Ukraine"], "continent": "Europe"},
        "Northern Europe": {"neighbors": ["Scandinavia", "Great Britain", "Western Europe", "Southern Europe", "Ukraine"], "continent": "Europe"},
        "Western Europe": {"neighbors": ["Great Britain", "Northern Europe", "Southern Europe", "North Africa"], "continent": "Europe"},
        "Southern Europe": {"neighbors": ["Western Europe", "Northern Europe", "Ukraine", "Middle East", "North Africa", "Egypt"], "continent": "Europe"},
        "Ukraine": {"neighbors": ["Scandinavia", "Northern Europe", "Southern Europe", "Ural", "Afghanistan", "Middle East"], "continent": "Europe"},
    },
    "Africa": {
        "North Africa": {"neighbors": ["Western Europe", "Brazil", "Egypt", "East Africa", "Congo", "Southern Europe"], "continent": "Africa"},
        "Egypt": {"neighbors": ["North Africa", "Southern Europe", "Middle East", "East Africa"], "continent": "Africa"},
        "East Africa": {"neighbors": ["Egypt", "North Africa", "Congo", "South Africa", "Madagascar", "Middle East"], "continent": "Africa"},
        "Congo": {"neighbors": ["North Africa", "East Africa", "South Africa"], "continent": "Africa"},
        "South Africa": {"neighbors": ["Congo", "East Africa", "Madagascar"], "continent": "Africa"},
        "Madagascar": {"neighbors": ["East Africa", "South Africa"], "continent": "Africa"},
    },
    "Asia": {
        "Ural": {"neighbors": ["Ukraine", "Siberia", "China", "Afghanistan"], "continent": "Asia"},
        "Siberia": {"neighbors": ["Ural", "Yakutsk", "Irkutsk", "Mongolia", "China"], "continent": "Asia"},
        "Yakutsk": {"neighbors": ["Siberia", "Kamchatka", "Irkutsk"], "continent": "Asia"},
        "Kamchatka": {"neighbors": ["Yakutsk", "Irkutsk", "Mongolia", "Japan", "Alaska"], "continent": "Asia"},
        "Irkutsk": {"neighbors": ["Siberia", "Yakutsk", "Kamchatka", "Mongolia"], "continent": "Asia"},
        "Mongolia": {"neighbors": ["Irkutsk", "Kamchatka", "Japan", "China", "Siberia"], "continent": "Asia"},
        "Japan": {"neighbors": ["Kamchatka", "Mongolia"], "continent": "Asia"},
        "Afghanistan": {"neighbors": ["Ukraine", "Ural", "China", "India", "Middle East"], "continent": "Asia"},
        "China": {"neighbors": ["Ural", "Siberia", "Mongolia", "India", "Siam", "Afghanistan"], "continent": "Asia"},
        "India": {"neighbors": ["Afghanistan", "China", "Middle East", "Siam"], "continent": "Asia"},
        "Siam": {"neighbors": ["India", "China", "Indonesia"], "continent": "Asia"},
        "Middle East": {"neighbors": ["Ukraine", "Southern Europe", "Egypt", "East Africa", "India", "Afghanistan"], "continent": "Asia"},
    },
    "Australia": {
        "Indonesia": {"neighbors": ["Siam", "New Guinea", "Western Australia"], "continent": "Australia"},
        "New Guinea": {"neighbors": ["Indonesia", "Eastern Australia", "Western Australia"], "continent": "Australia"},
        "Western Australia": {"neighbors": ["Indonesia", "New Guinea", "Eastern Australia"], "continent": "Australia"},
        "Eastern Australia": {"neighbors": ["New Guinea", "Western Australia"], "continent": "Australia"},
    }
}
continent_bonus = {
            "North America": 5,
            "South America": 2,
            "Europe": 5,
            "Africa": 3,
            "Asia": 7,
            "Australia": 2
        }

class Player:
    def __init__(self, name, color, ishuman):
        self.color = color
        self.territories = {} # {territory: units}
        self.cards = []
        self.units = 0
        self.is_human = ishuman

    def add_territory(self, territory, units):
        self.territories[territory] = units

    def remove_territory(self, territory):
        del self.territories[territory]

    def add_units(self, territory, units):
        self.units += units
        self.territories[territory] += units

    def remove_units(self, territory, units):
        self.units -= units
        self.territories[territory] -= units

    def get_units_in_territory(self, territory):
        return self.territories[territory]
    
    def getCards(self):
        return self.cards

class Card:
    def __init__(self, territory, unit_type):
        self.territory = territory
        self.unit_type = unit_type

class Game:
    def __init__(self, players):
        self.players = players
        self.current_player = 0
        self.turn = 0
        #self.turn_phase = "reinforce"
        self.num_trade_ins = 0

    def initialize_map(self):
        for continent in risk_map:
            keys_shuffled = random.shuffle(list(risk_map[continent].keys()))
            for key in keys_shuffled:
                territory = risk_map[continent][key]
                self.players[self.current_player].add_territory(territory, 1)
                self.players[self.current_player].units += 1
                self.current_player = (self.current_player + 1) % len(self.players)

    def next_player(self):
        self.current_player = (self.current_player + 1) % len(self.players)
        if self.current_player == 0:
            self.turn += 1

    def reinforce(self, territory, units):
        self.players[self.current_player].add_units(territory, units)
        self.reinforcements -= units

    def attack(self, attacking_player, attacking_territory, defending_player, defending_territory):
        attacker_rolls = min(attacking_player.get_units_in_territory(attacking_territory), 3)
        defender_rolls = min(defending_player.get_units_in_territory(defending_territory), 2)

        attacker_dice = [random.randint(1, 6) for i in range(attacker_rolls)].sort(reverse=True)
        defender_dice = [random.randint(1, 6) for i in range(defender_rolls)].sort(reverse=True)

        for i in range(min(attacker_rolls, defender_rolls)):
            if attacker_dice[i] > defender_dice[i]:
                defending_player.remove_units(defending_territory, 1)
            else:
                attacking_player.remove_units(attacking_territory, 1)

    def fortify(self, player, origin_territory, destination_territory, units):
        player.remove_units(origin_territory, units)
        player.add_units(destination_territory, units)  

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
            if all(territory in player.territories for territory in risk_map[continent]):
                return player
    
    def get_continent_bonus(self, continent):
        return continent_bonus[continent]

    def check_elimination_bonus(self, killing_player, eliminated_player):
        if eliminated_player.territories: # if they still have land they not eliminated
            return
        eliminated_player_cards = eliminated_player.getCards()
        if len(eliminated_player_cards) > 0:
            killing_player.cards += eliminated_player_cards

    def calculate_reinforcements(self, player):
        reinforcements = max(3, len(player.territories) // 3)
        for continent in risk_map:
            if self.check_continent(continent) == player:
                reinforcements += self.get_continent_bonus(continent)
        return reinforcements

def main():
    playerA = Player("Player A", "red", True)
    playerB = Player("Player B", "blue", True) 
    game = Game([playerA, playerB])
    game.initialize_map()
    while not game.check_win():
        if game.current_player.is_human:
            #place troops
            units_to_place = game.calculate_reinforcements(game.current_player)
            print("Reinforce phase")
            print("You have " + str(units) + " units to place.")
            print("You have the following territories: ")
            for territory in game.current_player.territories:
                print(territory)
            while units_to_place > 0:
                print("Which territory would you like to place units on?")
                territory = input()
                print("How many units would you like to place?")
                units = input()
                game.reinforce(territory, units)
                units_to_place -= units
            
            #attack
            print("Attack phase")
            print("You have the following territories: ")
            print("Would you like to attack? (y/n)")
            attack = input()
            while attack == "y":
                print("You have the following territories: ")
                for territory in game.current_player.territories:
                    print(territory)    
                print("Which territory would you like to attack from?")
                attacking_territory = input()
                print("You can attack the following territories: ")
                for neighbor in risk_map[attacking_territory]["neighbors"]:
                    if neighbor not in game.current_player.territories:
                        print(neighbor)
                print("Which territory would you like to attack?")
                defending_territory = input()
                for player in game.players:
                    if defending_territory in player.territories:
                        defending_player = player
                game.attack(game.current_player, attacking_territory, defending_player, defending_territory)
                game.check_elimination()
                print("Would you like to attack again? (y/n)")
                attack = input()

            #fortify
            print("Fortify phase")
            print("You have the following territories: ")
            for territory in game.current_player.territories:
                print(territory)
            print("Would you like to fortify? (y/n)")
            fortify = input()
            while fortify == "y":
                print("Which territory would you like to move units from?")
                origin_territory = input()
                print("You have " + str(game.current_player.get_units_in_territory(origin_territory)) + " units in this territory.")
                print("How many units would you like to move?")
                units = max(int(input()), game.current_player.get_units_in_territory(origin_territory) - 1)
                print("Which territory would you like to move units to?")
                destination_territory = input()
                game.fortify(game.current_player, origin_territory, destination_territory, units)
                print("Would you like to fortify again? (y/n)")
                fortify = input()
            game.next_player()
        
    print(game.get_winner().name + " wins!")
