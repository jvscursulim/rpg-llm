from __future__ import annotations

import numpy as np

from pydantic import BaseModel


class CharacterStats(BaseModel):
    strength: int = 0
    dexterity: int = 0
    constitution: int = 0
    intelligence: int = 0
    wisdom: int = 0
    charisma: int = 0
    strength_modifier: int=0
    dexterity_modifier: int=0
    constitution_modifier: int=0
    intelligence_modifier: int=0
    wisdom_modifier: int=0
    charisma_modifier: int=0

    def calculate_stats_modifiers(self):

        self.strength_modifier = np.floor((self.strength - 10)/2)
        self.dexterity_modifier = np.floor((self.dexterity - 10)/2)
        self.constitution_modifier = np.floor((self.constitution - 10)/2)
        self.intelligence_modifier = np.floor((self.intelligence - 10)/2)
        self.wisdom_modifier = np.floor((self.wisdom - 10)/2)
        self.charisma_modifier = np.floor((self.charisma - 10)/2)
