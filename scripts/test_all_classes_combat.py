"""Testa combate com todas as 13 classes em 3 batalhas.

Batalha 1: Fighter, Barbarian, Mage, Cleric, Paladin  (5 vs 5)
Batalha 2: Ranger, Monk, Sorcerer, Warlock            (4 vs 4)
Batalha 3: Druid, Rogue, Bard, Artificer              (4 vs 4)

Uso:
    python -m scripts.test_all_classes_combat
"""

from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.artificer.artificer import Artificer
from src.core.classes.barbarian.barbarian import Barbarian
from src.core.classes.bard.bard import Bard
from src.core.classes.cleric.cleric import Cleric
from src.core.classes.druid.druid import Druid
from src.core.classes.fighter.fighter import Fighter
from src.core.classes.mage.mage import Mage
from src.core.classes.monk.monk import Monk
from src.core.classes.paladin.paladin import Paladin
from src.core.classes.ranger.ranger import Ranger
from src.core.classes.rogue.rogue import Rogue
from src.core.classes.sorcerer.sorcerer import Sorcerer
from src.core.classes.warlock.warlock import Warlock
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import CombatEngine, CombatResult
from src.core.combat.combat_log import CombatLog
from src.core.combat.composite_handler import CompositeHandler
from src.core.combat.dispatch_handler import DispatchTurnHandler
from src.core.combat.log_formatter import LogFormatter
from src.core.combat.skill_handler import SkillHandler
from src.core.items.armor_loader import load_armors
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_loader import load_skills
from src.core.skills.spell_slot import SpellSlot

EMPTY_THRESHOLDS = ThresholdCalculator({})
ENEMY_MODS = ClassModifiers(
    hit_dice=10, mod_hp_flat=0, mod_hp_mult=8, mana_multiplier=5,
    mod_atk_physical=7, mod_atk_magical=5, mod_def_physical=3,
    mod_def_magical=3, regen_hp_mod=3, regen_mana_mod=2,
)


def _attrs(s: int, d: int, c: int, i: int, w: int, ch: int, m: int) -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: s, AttributeType.DEXTERITY: d,
        AttributeType.CONSTITUTION: c, AttributeType.INTELLIGENCE: i,
        AttributeType.WISDOM: w, AttributeType.CHARISMA: ch,
        AttributeType.MIND: m,
    })


def _load_mods(class_name: str) -> ClassModifiers:
    return ClassModifiers.from_json(f"data/classes/{class_name}.json")


def _make_skill_bar(skill_ids: list[str]) -> SkillBar:
    all_skills = load_skills()
    skills = tuple(all_skills[sid] for sid in skill_ids if sid in all_skills)
    if not skills:
        return SkillBar(slots=())
    total_cost = sum(s.slot_cost for s in skills)
    slot = SpellSlot(max_cost=total_cost + 50, skills=skills)
    return SkillBar(slots=(slot,))


def _make_enemies(count: int, weapons: dict, armors: dict) -> list[Character]:
    """Cria inimigos genericos para testar contra."""
    enemy_configs = [
        ("Orc_Berserker", _attrs(8, 5, 8, 3, 4, 3, 3),
         weapons["greatsword"], armors["chain_mail"], Position.FRONT),
        ("Orc_Archer", _attrs(5, 8, 6, 3, 5, 3, 4),
         weapons["longbow"], armors["studded_leather"], Position.BACK),
        ("Dark_Shaman", _attrs(3, 5, 5, 8, 7, 5, 8),
         weapons["quarterstaff"], armors["mage_robes"], Position.BACK),
        ("Orc_Brute", _attrs(9, 4, 9, 2, 3, 2, 2),
         weapons["warhammer"], armors["plate_armor"], Position.FRONT),
        ("Orc_Scout", _attrs(6, 7, 6, 4, 5, 3, 3),
         weapons["short_sword"], armors["leather_armor"], Position.FRONT),
    ]
    enemies = []
    for idx in range(count):
        name, attrs, weapon, armor, pos = enemy_configs[idx % len(enemy_configs)]
        suffix = f"_{idx}" if count > len(enemy_configs) else ""
        enemies.append(Character(
            name=f"{name}{suffix}",
            attributes=attrs,
            config=CharacterConfig(
                class_modifiers=ENEMY_MODS,
                threshold_calculator=EMPTY_THRESHOLDS,
                position=pos,
                weapon=weapon,
                armor=armor,
                skill_bar=_make_skill_bar(["weaken"]),
            ),
        ))
    return enemies


def _make_handler(names: list[str]) -> DispatchTurnHandler:
    """Handler generico: tenta skill -> basic attack para todos."""
    skill_h = SkillHandler()
    basic_h = BasicAttackHandler()
    combo = CompositeHandler((skill_h, basic_h))
    return DispatchTurnHandler(
        {name: combo for name in names},
        basic_h,
    )


def _print_party_status(label: str, chars: list[Character]) -> None:
    print(f"\n  {label}:")
    for c in chars:
        alive = "ALIVE" if c.is_alive else "DEAD"
        hp_pct = int(c.current_hp / c.max_hp * 100) if c.max_hp > 0 else 0
        mp_pct = int(c.current_mana / c.max_mana * 100) if c.max_mana > 0 else 0
        print(f"    {c.name:20s} [{alive:5s}] HP: {c.current_hp:4d}/{c.max_hp:4d} ({hp_pct:3d}%)  MP: {c.current_mana:4d}/{c.max_mana:4d} ({mp_pct:3d}%)")


def _run_battle(
    battle_name: str,
    party: list[Character],
    enemies: list[Character],
) -> CombatResult:
    """Executa uma batalha e imprime o resultado."""
    all_names = [c.name for c in party] + [c.name for c in enemies]
    handler = _make_handler(all_names)
    engine = CombatEngine(party, enemies, handler)

    print(f"\n{'='*70}")
    print(f"  {battle_name}")
    print(f"{'='*70}")
    print(f"\n  Party: {', '.join(c.name for c in party)}")
    print(f"  Enemies: {', '.join(c.name for c in enemies)}")

    _print_party_status("Party (antes)", party)
    _print_party_status("Enemies (antes)", enemies)

    result = engine.run_combat()

    # Combat log
    log = CombatLog()
    for event in engine.events:
        log.add_from_combat_event(event)

    print(f"\n  --- Combat Log ({engine.round_number} rounds) ---")
    text = LogFormatter.to_text(log)
    if text:
        for line in text.split("\n"):
            print(f"  {line}")

    _print_party_status("Party (depois)", party)
    _print_party_status("Enemies (depois)", enemies)

    result_label = {
        CombatResult.PARTY_VICTORY: "VITORIA DA PARTY",
        CombatResult.PARTY_DEFEAT: "DERROTA DA PARTY",
        CombatResult.DRAW: "EMPATE (100 rounds)",
    }
    print(f"\n  >> RESULTADO: {result_label[result]} <<")
    print(f"  >> Rounds: {engine.round_number}")
    return result


def battle_1(weapons: dict, armors: dict) -> CombatResult:
    """Fighter, Barbarian, Mage, Cleric, Paladin vs 5 Orcs."""
    fighter = Fighter(
        name="Gareth",
        attributes=_attrs(9, 6, 8, 3, 4, 3, 3),
        config=CharacterConfig(
            class_modifiers=_load_mods("fighter"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.FRONT,
            weapon=weapons["longsword"],
            armor=armors["chain_mail"],
            skill_bar=_make_skill_bar(["power_strike"]),
        ),
    )
    barbarian = Barbarian(
        name="Throk",
        attributes=_attrs(10, 5, 9, 2, 4, 2, 3),
        config=CharacterConfig(
            class_modifiers=_load_mods("barbarian"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.FRONT,
            weapon=weapons["greatsword"],
            armor=armors["leather_armor"],
        ),
    )
    mage = Mage(
        name="Lyra",
        attributes=_attrs(3, 5, 4, 10, 8, 6, 10),
        config=CharacterConfig(
            class_modifiers=_load_mods("mage"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            weapon=weapons["arcane_staff"],
            armor=armors["mage_robes"],
            skill_bar=_make_skill_bar(["fireball", "ice_bolt"]),
        ),
    )
    cleric = Cleric(
        name="Aurelia",
        attributes=_attrs(4, 5, 6, 7, 10, 8, 8),
        config=CharacterConfig(
            class_modifiers=_load_mods("cleric"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            weapon=weapons["holy_mace"],
            armor=armors["scale_mail"],
            skill_bar=_make_skill_bar(["minor_heal"]),
        ),
    )
    paladin = Paladin(
        name="Roland",
        attributes=_attrs(8, 5, 8, 4, 7, 8, 5),
        config=CharacterConfig(
            class_modifiers=_load_mods("paladin"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.FRONT,
            weapon=weapons["longsword"],
            armor=armors["plate_armor"],
        ),
    )
    party = [fighter, barbarian, mage, cleric, paladin]
    enemies = _make_enemies(5, weapons, armors)
    return _run_battle("BATALHA 1: Fighter, Barbarian, Mage, Cleric, Paladin", party, enemies)


def battle_2(weapons: dict, armors: dict) -> CombatResult:
    """Ranger, Monk, Sorcerer, Warlock vs 4 Orcs."""
    ranger = Ranger(
        name="Kael",
        attributes=_attrs(6, 9, 6, 5, 7, 4, 5),
        config=CharacterConfig(
            class_modifiers=_load_mods("ranger"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            weapon=weapons["longbow"],
            armor=armors["studded_leather"],
            skill_bar=_make_skill_bar(["poison_strike"]),
        ),
    )
    monk = Monk(
        name="Zhen",
        attributes=_attrs(6, 9, 7, 4, 8, 3, 6),
        config=CharacterConfig(
            class_modifiers=_load_mods("monk"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.FRONT,
            weapon=weapons["quarterstaff"],
            armor=armors["leather_armor"],
        ),
    )
    sorcerer = Sorcerer(
        name="Nyx",
        attributes=_attrs(3, 6, 4, 10, 7, 8, 10),
        config=CharacterConfig(
            class_modifiers=_load_mods("sorcerer"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            weapon=weapons["arcane_staff"],
            armor=armors["mage_robes"],
            skill_bar=_make_skill_bar(["fireball", "ice_bolt"]),
        ),
    )
    warlock = Warlock(
        name="Vex",
        attributes=_attrs(3, 5, 5, 9, 6, 8, 9),
        config=CharacterConfig(
            class_modifiers=_load_mods("warlock"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            weapon=weapons["dagger"],
            armor=armors["leather_armor"],
            skill_bar=_make_skill_bar(["fireball"]),
        ),
    )
    party = [ranger, monk, sorcerer, warlock]
    enemies = _make_enemies(4, weapons, armors)
    return _run_battle("BATALHA 2: Ranger, Monk, Sorcerer, Warlock", party, enemies)


def battle_3(weapons: dict, armors: dict) -> CombatResult:
    """Druid, Rogue, Bard, Artificer vs 4 Orcs."""
    druid = Druid(
        name="Fern",
        attributes=_attrs(4, 5, 6, 8, 10, 7, 9),
        config=CharacterConfig(
            class_modifiers=_load_mods("druid"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            weapon=weapons["quarterstaff"],
            armor=armors["leather_armor"],
            skill_bar=_make_skill_bar(["minor_heal"]),
        ),
    )
    rogue = Rogue(
        name="Shadow",
        attributes=_attrs(6, 10, 5, 6, 5, 6, 4),
        config=CharacterConfig(
            class_modifiers=_load_mods("rogue"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.FRONT,
            weapon=weapons["dagger"],
            armor=armors["studded_leather"],
            skill_bar=_make_skill_bar(["poison_strike"]),
        ),
    )
    bard = Bard(
        name="Melody",
        attributes=_attrs(4, 6, 5, 6, 7, 10, 8),
        config=CharacterConfig(
            class_modifiers=_load_mods("bard"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            weapon=weapons["short_sword"],
            armor=armors["leather_armor"],
            skill_bar=_make_skill_bar(["minor_heal"]),
        ),
    )
    artificer = Artificer(
        name="Cogsworth",
        attributes=_attrs(5, 7, 6, 10, 6, 5, 8),
        config=CharacterConfig(
            class_modifiers=_load_mods("artificer"),
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            weapon=weapons["shortbow"],
            armor=armors["studded_leather"],
        ),
    )
    party = [druid, rogue, bard, artificer]
    enemies = _make_enemies(4, weapons, armors)
    return _run_battle("BATALHA 3: Druid, Rogue, Bard, Artificer", party, enemies)


def main() -> None:
    weapons = load_weapons()
    armors = load_armors()

    results = []
    results.append(("Batalha 1", battle_1(weapons, armors)))
    results.append(("Batalha 2", battle_2(weapons, armors)))
    results.append(("Batalha 3", battle_3(weapons, armors)))

    print(f"\n{'='*70}")
    print("  RESUMO FINAL")
    print(f"{'='*70}")
    for name, result in results:
        label = {
            CombatResult.PARTY_VICTORY: "VITORIA",
            CombatResult.PARTY_DEFEAT: "DERROTA",
            CombatResult.DRAW: "EMPATE",
        }
        print(f"  {name}: {label[result]}")


if __name__ == "__main__":
    main()
