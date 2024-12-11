from game import Game, Player
import argparse
from random import randint
def main(args):
    playerA = Player("Player A", color = "red", ishuman = True)
    playerB = Player("Player B", color = "blue", ishuman = False) 
    game = Game([playerA, playerB], args.map, vis = args.vis)
    game.initialize_map()
    game.update_visualization()
    while not game.check_win():
        print("current player: " + game.players[game.current_player_id]['name'])
        if game.players[game.current_player_id]['ishuman']:
            #place troops
            game.move_to_reinforce_phase()
            print("Reinforce phase")
            stop_reinforcing = False
            while game.get_reinforcements() > 0 and not stop_reinforcing:
                print("You have " + str(game.get_reinforcements()) + " units to place.")
                print("You have the following territories: ")
                for territory in game.get_territories():
                    print(territory)
                print("Which territory would you like to place units on?")
                territory = input()
                if territory not in game.get_territories():
                    print("Invalid territory")
                    continue
                print("How many units would you like to place?")
                units = input()
                game.reinforce(territory, int(units))
                print("Would you like to place more units? (y/n)")
                stop_reinforcing = input().lower() == "n"
            
            game.move_to_attack_phase()
            print("Attack phase")
            stop_attacking = False
            while not stop_attacking and game.can_attack():
                print("You have the following territories: ")
                for territory in game.get_territories():
                    print(territory)
                print("Would you like to attack? (y/n)")
                attack = input().lower()
                if attack == "y":
                    print("Which territory would you like to attack from?")
                    attacking_territory = input()
                    print("You can attack the following territories: ")
                    for neighbor in game.get_neighbors(attacking_territory):
                        if neighbor not in game.get_territories():
                            print(neighbor)
                    print("Which territory would you like to attack?")
                    defending_territory = input()
                    game.attack(attacking_territory, defending_territory)
                    game.check_elimination()
                    print("Would you like to attack again? (y/n)")
                    stop_attacking = input().lower() == "n"
                else:
                    stop_attacking = True
                game.update_visualization()

            game.move_to_fortify_phase()
            print("Fortify phase")
            print("You have the following territories: ")
            for territory in game.get_territories():
                print(territory)
            print("Would you like to fortify? (y/n)")
            fortify = input()
            if fortify.lower() == "y":
                print("Which territory would you like to move units from?")
                origin_territory = input()
                print("You have " + str(game.risk_map['Territories'][origin_territory]['units']) + " units in this territory.")
                print("How many units would you like to move?")
                units = max(int(input()), game.risk_map['Territories'][origin_territory]['units'] - 1)
                print("Which territory would you like to move units to?")
                destination_territory = input()
                game.fortify(origin_territory, destination_territory, units)

            game.update_visualization()
            game.next_player()
        else:
            # implement AI
            # sample AI: random moves
            game.move_to_reinforce_phase()
            print("listing territories")
            print(game.get_territories())
            print("Reinforce phase")
            stop_reinforcing = False #not using this for now
            while game.get_reinforcements() > 0 and not stop_reinforcing:
                territory = game.get_territories()[randint(0, len(game.get_territories()) - 1)]
                units = randint(0, game.get_reinforcements())
                game.reinforce(territory, units)
                game.update_visualization()
                print(territory + " has been reinforced with " + str(units) + " units.")
            
            game.move_to_attack_phase()
            print("Attack phase")
            stop_attacking = False
            while not stop_attacking and game.can_attack():
                attacking_territory = game.get_territories()[randint(0, len(game.get_territories()) - 1)]
                neighbors = game.get_neighbors(attacking_territory)
                defending_territory = neighbors[randint(0, len(neighbors) - 1)]
                if defending_territory not in game.get_territories():
                    game.attack(attacking_territory, defending_territory)
                    game.check_elimination()
                    game.update_visualization()
                    print(attacking_territory + " attacked " + defending_territory + ".")
                stop_attacking = randint(0, 1) == 1
            game.update_visualization()
            game.next_player()


    print(game.get_winner().name + " wins!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Game Initialization.")
    parser.add_argument("--map", type=str, default="world.json", help="The map file to use for the game.")
    parser.add_argument("--vis", type=bool, default=True, help="Whether to visualize the game.")
    args = parser.parse_args()
    main(args)