"""Mixin para gerenciamento de equipamento (armor e accessories)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.effects.modifiable_stat import ModifiableStat
from src.core.items.accessory_slots import calculate_accessory_slots

if TYPE_CHECKING:
    from src.core.items.accessory import Accessory
    from src.core.items.armor import Armor


class EquipmentMixin:
    """Gerencia armor e accessories equipados."""

    _armor: Armor | None
    _accessories: list[Accessory]

    @property
    def armor(self) -> Armor | None:
        return self._armor

    @property
    def accessories(self) -> tuple[Accessory, ...]:
        return tuple(self._accessories)

    @property
    def max_accessory_slots(self) -> int:
        bonuses = self.get_threshold_bonuses()  # type: ignore[attr-defined]
        return calculate_accessory_slots(bonuses)

    def equip_armor(self, armor: Armor) -> None:
        self._armor = armor

    def unequip_armor(self) -> Armor | None:
        old = self._armor
        self._armor = None
        return old

    def equip_accessory(self, accessory: Accessory) -> bool:
        """Equipa acessorio. Retorna False se nao ha slots."""
        if len(self._accessories) >= self.max_accessory_slots:
            return False
        self._accessories.append(accessory)
        return True

    def unequip_accessory(self, accessory: Accessory) -> bool:
        """Remove acessorio. Retorna False se nao encontrado."""
        try:
            self._accessories.remove(accessory)
        except ValueError:
            return False
        return True

    def _armor_bonus(self, field: str) -> int:
        """Retorna bonus flat da armadura para o campo dado."""
        if self._armor is None:
            return 0
        return getattr(self._armor, field, 0)

    def _total_accessory_flat(self, stat: ModifiableStat) -> int:
        """Soma bonus flat de todos os acessorios para o stat."""
        total = 0
        for acc in self._accessories:
            for bonus in acc.stat_bonuses:
                if bonus.stat == stat:
                    total += bonus.flat
        return total
