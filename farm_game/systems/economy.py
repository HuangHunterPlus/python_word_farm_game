import math


LEVEL_COEFFICIENT = 100


class EconomySystem:
    def __init__(self, gold: int = 100, exp: int = 0):
        self.gold = gold
        self.exp = exp

    def add_gold(self, amount: int):
        self.gold += amount

    def spend_gold(self, amount: int) -> bool:
        if self.gold < amount:
            return False
        self.gold -= amount
        return True

    def add_exp(self, amount: int):
        self.exp += amount

    @property
    def level(self) -> int:
        return int(math.sqrt(self.exp / LEVEL_COEFFICIENT)) + 1

    def get_exp_to_next_level(self) -> int:
        current = self.level
        needed = LEVEL_COEFFICIENT * (current ** 2)
        return needed - self.exp

    def get_total_exp_for_level(self, level: int) -> int:
        return LEVEL_COEFFICIENT * (level ** 2)
