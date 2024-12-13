"""
Builds a graph of a risk gameboard given a JSON file
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

class Graph():
    """
    Class defines a graph in terms of territory locations as a vector of units and ownerships
    with an associated adjacency matrix
    """
    def __init__(self, board):
        """
        constructor
        """
        self.board = json.load(open(board))
        self.graph = nx.Graph()
        self.plt, self.ax = plt.subplots()
        self.territories = np.zeros((len(self.board["Territories"]), 2))
        self.territories[:,1] = 1 # set all territories to have 1 unit

        idx = 0
        territory_dict = {}
        continent_dict = {}
        for continent,contents in self.board['Continents'].items():
            continent_dict[continent] = (idx, idx + len(contents['territories']), contents['bonus'])
            for territory in contents['territories']:
                territory_dict[territory] = idx
                idx += 1
                pos = self.board['Territories'][territory].get('position', (np.random.rand(), np.random.rand())) 
                self.graph.add_node(territory, position=pos)
        adjacencies = np.zeros((idx, idx))
        for territory, contents in self.board['Territories'].items():
            for neighbor in contents['neighbors']:
                adjacencies[territory_dict[territory], territory_dict[neighbor]] = 1
                self.graph.add_edge(territory, neighbor)

        self.adjacencies = adjacencies
        self.continents = continent_dict
        self.territory_ids = territory_dict
        self.pos = nx.spring_layout(self.graph)

    def get_territory_by_id(self, territory_id):
        """
        Get the territory by its ID
        """
        return self.territories[territory_id]
    
    def set_owner(self, territory_id, owner):
        """
        Set the owner of a territory
        """
        self.territories[territory_id][0] = owner
    
    def get_territory_by_name(self, territory_name):
        """
        Get the territory by its name
        """
        return self.territories[self.territory_ids[territory_name]]
    
    def get_owner(self, territory_id):
        """
        Get the owner of a territory
        """
        return self.territories[territory_id][0]
    
    def get_units(self, territory_id):
        """
        Get the number of units in a territory
        """
        return self.territories[territory_id][1]
    
    def get_adjacencies(self, territory_id):
        """
        Get the adjacencies of a territory
        """
        return np.where(self.adjacencies[territory_id] == 1)[0]
    
    def get_continent(self, territory_id):
        """
        Get the continent of a territory
        """
        for continent, (start, end, _) in self.continents.items():
            if start <= territory_id < end:
                return continent
        return None
    
    def get_continent_bonus(self, continent):
        """
        Get the bonus for a continent
        """
        return self.continents[continent][2]
    
    def display(self):
        """
        Display the gameboard: territories, owners, and units
        """
        for territory, idx in self.territory_ids.items():
            owner = int(self.get_owner(idx))
            units = int(self.get_units(idx))
            print(f"Territory: {territory}, Owner: {owner}, Units: {units}")