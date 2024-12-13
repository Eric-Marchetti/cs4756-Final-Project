import networkx as nx
import matplotlib.pyplot as plt

def visualize_game_state(env, title="Risk Game State"):
    """
    Visualize the current game state of the Risk environment using predefined coordinates.
    """
    owners = env.risk_env.game_state[:, 0]
    units = env.risk_env.game_state[:, 1]
    adj = env.risk_env.adjacencies
    territories = env.risk_env.territories  # dict {territory_name: index}
    pos = env.risk_env.positions           # dict {territory_index: (x, y)}

    # Create a graph from the adjacency matrix
    G = nx.from_numpy_array(adj)

    # Reverse territory dictionary for labeling
    idx_to_name = {v: k for k, v in territories.items()}

    # Assign colors based on owner
    player_colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
    node_colors = [player_colors[owner % len(player_colors)] for owner in owners]

    # Labels with territory name and unit count
    node_labels = {i: f"{idx_to_name[i]}\nUnits: {units[i]}" for i in range(len(owners))}

    plt.figure(figsize=(15, 10))
    # Draw the graph using the predefined positions
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200)
    nx.draw_networkx_edges(G, pos, alpha=0.7)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, font_color='white')

    plt.title(title)
    plt.axis('off')
    plt.show()