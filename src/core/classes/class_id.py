"""ClassId enum — identificador unico de cada classe do jogo."""

from enum import Enum


class ClassId(Enum):
    """13 classes jogaveis. Valor = string usada em JSONs e lookups."""

    FIGHTER = "fighter"
    BARBARIAN = "barbarian"
    MAGE = "mage"
    CLERIC = "cleric"
    PALADIN = "paladin"
    RANGER = "ranger"
    MONK = "monk"
    SORCERER = "sorcerer"
    WARLOCK = "warlock"
    DRUID = "druid"
    ROGUE = "rogue"
    BARD = "bard"
    ARTIFICER = "artificer"
