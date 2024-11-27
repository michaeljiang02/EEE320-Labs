"""
A medium momentum and poison based bug. Uses three phases.
Phase one - move away from parent and eat until an energy threshold nmor turn threshold is reached. Then move to phase 2
Phase two - grow photo-glands and propagate until an enemy is seen. Then move to phase 3
Phase three - stop propagating to conserve energy, attack enemy if it has less strength, otherwise create poison and stay still

version 1
2024-11-27
"""

from shared import Creature, Cilia, CreatureTypeSensor, EnergySensor, Propagator, Direction, Soil, PhotoGland, Plant, PoisonGland

class KoublaiKhan(Creature):
    __instance_count = 0

    def __init__(self):
        super().__init__()
        KoublaiKhan.__instance_count+=1
        self.cilia = None
        self.type_sensor = None
        self.energy_sensor= None
        self.womb = None
        self.poison_gland=None
        self.phase=1
        self.spread_direction=Direction.random()
        self.conserve_count=0
        self.early_game_count=0
        self.photo_gland_count=0

    @classmethod
    def instance_count(cls):
        return KoublaiKhan.__instance_count

    @classmethod
    def destroyed(cls):
        KoublaiKhan.__instance_count -= 1

    def do_turn(self):
        if self.phase==1:
            self.phase_1()
        if self.phase==2:
            self.phase_2()
        if self.phase==3:
            self.phase_3()

    def phase_1(self): #rapid expansion based on quick movement and growing photo glands
        self.early_game_count+=1
        if not self.cilia and not self.type_sensor:
            self.grow_initial_organs()
        if self.cilia and self.type_sensor:
            self.eat_plants()
        if  self.early_game_count>5:
            self.phase=2

    def phase_2(self): #stay still and propagate
        if not self.womb and self.strength() > Propagator.CREATION_COST+100:
            self.womb = KoublaiKhanPropagator(self)
        self.reproduce_if_able()
        if self.look_for_enemies(): #if an enemy is spotted, move to phase 3.
            self.conserve_count=0
            self.phase=3

    def phase_3(self): #stay still and avoid reproducing to save energy. If an enemy has less energy, attack. Else, make poison.
        self.conserve_count+=1
        if not self.energy_sensor:
            self.energy_sensor=EnergySensor(self)
        if (self.maneuver_warfare()):
            self.conserve_count = 0
        if self.conserve_count>=4:
            self.phase = 2

    def reproduce_if_able(self):
        if self.strength() >= 0.95 * Creature.MAX_STRENGTH:
            self.womb.give_birth(self.strength()/2, self.spread_direction)

    def grow_initial_organs(self):
        if not self.cilia and self.strength() > Cilia.CREATION_COST+100:
            self.cilia = Cilia(self)
        if not self.type_sensor and self.strength() > CreatureTypeSensor.CREATION_COST+100:
            self.type_sensor = CreatureTypeSensor(self)
        while (self.photo_gland_count < 5) and self.strength() > PhotoGland.CREATION_COST+100:
            PhotoGland(self)

    def look_for_enemies(self):
        for d in Direction:
            threat = self.type_sensor.sense(d)
            if threat!= Soil and threat != KoublaiKhan and threat!=Plant:
                return True
        return False

    def maneuver_warfare(self):
        for d in Direction:
            threat = self.type_sensor.sense(d)
            if threat!= Soil and threat != KoublaiKhan and threat!=Plant:
                threat_strength=self.energy_sensor.sense(d)
                if threat_strength<self.strength():
                    self.cilia.move_in_direction(d)
                else:
                    if self.strength() > PoisonGland.CREATION_COST:
                        self.poison_gland=PoisonGland(self)
                        self.poison_gland.add_poison(self.strength()*0.8)
            return True
        return False

    def eat_plants(self):
        for d in Direction:
            potential_plant = self.type_sensor.sense(d)
            if potential_plant==Plant:
                self.cilia.move_in_direction(d)
        self.cilia.move_in_direction(self.spread_direction)

class KoublaiKhanPropagator(Propagator):
    def make_child(self):
        return KoublaiKhan()
