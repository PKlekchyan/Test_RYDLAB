class Planet:
    def __init__(self, id_, name, diameter, population, rotation_period, orbital_period):
        self.id = id_
        self.name = name
        self.diameter = diameter
        self.population = population
        self.rotation_period = rotation_period
        self.orbital_period = orbital_period


class Character:
    def __init__(self, id_, name, planet_name, image=None):
        self.id = id_
        self.name = name
        self.planet_name = planet_name
        self.image = image


