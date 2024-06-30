from typing import Annotated
from pydantic import BaseModel, Field
from schemas.character_stats import CharacterStats


class Character(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    race: Annotated[str, Field(min_length=1)]
    gender: Annotated[str, Field(min_length=1)]
    classe: Annotated[str, Field(min_length=1)]
    background: Annotated[str, Field(min_length=1)]
    hp: Annotated[int, Field(gt=1)]
    ca: int
    stats: CharacterStats
