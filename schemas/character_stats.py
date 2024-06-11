from __future__ import annotations

from random import randint
from pydantic import BaseModel


class CharacterStats(BaseModel):
    strength: int = 0
    strength: int = 0
    dexterity: int = 0
    constitution: int = 0
    intelligence: int = 0
    wisdom: int = 0
    charisma: int = 0

    def generate_stats(self):
        self.strength = randint(a=1, b=21)
        self.dexterity = randint(a=1, b=21)
        self.constitution = randint(a=1, b=21)
        self.intelligence = randint(a=1, b=21)
        self.wisdom = randint(a=1, b=21)
        self.charisma = randint(a=1, b=21)
