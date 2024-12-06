from game import Game
from player import Player

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
                for neighbor in game.risk_map[attacking_territory]:
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

if __name__ == "__main__":
    main()