"""
version 1.13
2021-11-23

Python implementation: Greg Phillips
Based on an original design by Scott Knight and a series of
implementations in C++ and Java by Scott Knight and Greg Phillips
"""


from shared import Creature, Cilia, CreatureTypeSensor, Propagator, Direction, Soil, Plant, PhotoGland


class GenghisKhan(Creature):
    """
    Grows one Cilia, one CreatureTypeSensor, one GenghisKhanPropagator, and as many PhotoGlands as it can. On
    each turn, if the organ cap has not been reached, Genghis Khan will continue growing PhotoGlands. It will then reproduce if strength is high enough, then attempts to
    find a creature to attack. If unable to attack, it moves in a random direction.
    """
    __instance_count = 0

    def __init__(self):
        super().__init__()
        GenghisKhan.__instance_count += 1
        self.cilia = None
        self.type_sensor = None
        self.womb = None
        self.organ_count = 0


    def do_turn(self):
        if self.organ_count < Creature.MAX_ORGANS:
            self.create_organs()
        else:
            self.reproduce_if_able()
            did_attack = self.maneuver_warfare()
            if not did_attack:
                self.cilia.move_in_direction(Direction.random())


    @classmethod
    def instance_count(cls):
        return GenghisKhan.__instance_count


    @classmethod
    def destroyed(cls):
        GenghisKhan.__instance_count -= 1


    def create_organs(self):
        if not self.cilia and self.strength() > Cilia.CREATION_COST:
            self.cilia = Cilia(self)
            self.organ_count += 1
        if not self.type_sensor and self.strength() > CreatureTypeSensor.CREATION_COST:
            self.type_sensor = CreatureTypeSensor(self)
            self.organ_count += 1
        if not self.womb and self.strength() > Propagator.CREATION_COST:
            self.womb = GenghisKhanPropagator(self)
            self.organ_count += 1
        while self.organ_count < Creature.MAX_ORGANS and self.strength() > PhotoGland.CREATION_COST:
            PhotoGland(self)
            self.organ_count += 1



    def reproduce_if_able(self):
        if self.strength() >= 0.95 * Creature.MAX_STRENGTH:
            for d in Direction:
                nursery = self.type_sensor.sense(d)
                if nursery == Soil or nursery == Plant:
                    self.womb.give_birth(self.strength() * 0.5, d)
                    break


    def maneuver_warfare(self):
        for d in Direction:
            enemy = self.type_sensor.sense(d)
            if enemy != Soil and enemy != GenghisKhan:
                self.cilia.move_in_direction(d)
                return True
        return False


class GenghisKhanPropagator(Propagator):
    def make_child(self):
            return GenghisKhan()


