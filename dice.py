import random

class Dice:
    def __init__(self, sides=6):
        self.sides = sides

    def roll(self):
        self.value = random.randint(1,6)
        return self.value

class RollSet:
    def __init__(self, count = 6):
        self.dice = [Dice() for _ in range(count)]
        self.remaining = count

    def roll_all(self):
        self.remaining = len(self.dice)
        return self.roll_remaining()

    def roll_selected(self, indices):
        for i in indices:
            self.dice[i].roll()
        return self.get_values()

    def roll_remaining(self): # This method rolls the remaining dice in the set and returns their values.
        values = []
        for i in range(self.remaining):
            values.append(self.dice[i].roll())
        return values

    def get_values(self):
        return [die.value for die in self.dice] # This method returns the current values of all dice in the set.