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