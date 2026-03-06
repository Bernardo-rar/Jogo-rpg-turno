from __future__ import annotations


THIRST_TRIGGER_STACKS = 5
HP_THRESHOLD_RATIO = 0.5


class InsatiableThirst:
    """Sede Insaciavel do Warlock.

    Ganha 1 stack por turno abaixo de 50% HP.
    Ao atingir 5 stacks, ativa buff temporario e reseta stacks.
    Buff dura CON turnos.
    """

    def __init__(self) -> None:
        self._stacks = 0
        self._active = False
        self._remaining_turns = 0

    @property
    def stacks(self) -> int:
        return self._stacks

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def remaining_turns(self) -> int:
        return self._remaining_turns

    def check_and_stack(self, hp_ratio: float) -> bool:
        """Checa HP e ganha stack se abaixo de 50%. Retorna True se trigger."""
        if self._active:
            return False
        if hp_ratio >= HP_THRESHOLD_RATIO:
            return False
        self._stacks += 1
        if self._stacks >= THIRST_TRIGGER_STACKS:
            return True
        return False

    def activate(self, duration: int) -> None:
        """Ativa buff de Sede Insaciavel por N turnos."""
        self._active = True
        self._remaining_turns = duration
        self._stacks = 0

    def tick(self) -> None:
        """Decrementa duracao. Desativa quando acaba."""
        if not self._active:
            return
        self._remaining_turns -= 1
        if self._remaining_turns <= 0:
            self._active = False
            self._remaining_turns = 0
