"""Mock Battle v2 - integracao completa: skills, consumiveis, elementos, equipment."""

from __future__ import annotations

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import (
    CombatEngine,
    CombatResult,
    EventType as EngineEventType,
)
from src.core.combat.combat_log import CombatLog, EventType as LogEventType
from src.core.combat.composite_handler import CompositeHandler
from src.core.combat.consumable_handler import ConsumableHandler
from src.core.combat.dispatch_handler import DispatchTurnHandler
from src.core.combat.log_formatter import LogFormatter
from src.core.combat.skill_handler import SkillHandler
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import load_profiles
from src.core.items.accessory_loader import load_accessories
from src.core.items.armor_loader import load_armors
from src.core.items.consumable_loader import load_consumables
from src.core.items.inventory import Inventory
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_loader import load_skills
from src.core.skills.spell_slot import SpellSlot

EMPTY_THRESHOLDS = ThresholdCalculator({})

# --- ClassModifiers por arquetipo ---

FIGHTER_MODS = ClassModifiers(
    hit_dice=12, mod_hp_flat=0, mod_hp_mult=10, mana_multiplier=6,
    mod_atk_physical=10, mod_atk_magical=6, mod_def_physical=5,
    mod_def_magical=3, regen_hp_mod=5, regen_mana_mod=3,
)
RANGER_MODS = ClassModifiers(
    hit_dice=10, mod_hp_flat=0, mod_hp_mult=8, mana_multiplier=7,
    mod_atk_physical=8, mod_atk_magical=6, mod_def_physical=3,
    mod_def_magical=3, regen_hp_mod=3, regen_mana_mod=3,
)
CLERIC_MODS = ClassModifiers(
    hit_dice=8, mod_hp_flat=0, mod_hp_mult=8, mana_multiplier=8,
    mod_atk_physical=5, mod_atk_magical=8, mod_def_physical=3,
    mod_def_magical=4, regen_hp_mod=3, regen_mana_mod=4,
)
SORCERER_MODS = ClassModifiers(
    hit_dice=6, mod_hp_flat=0, mod_hp_mult=6, mana_multiplier=12,
    mod_atk_physical=4, mod_atk_magical=10, mod_def_physical=2,
    mod_def_magical=5, regen_hp_mod=2, regen_mana_mod=5,
)
ORC_MODS = ClassModifiers(
    hit_dice=10, mod_hp_flat=0, mod_hp_mult=8, mana_multiplier=5,
    mod_atk_physical=8, mod_atk_magical=4, mod_def_physical=4,
    mod_def_magical=3, regen_hp_mod=3, regen_mana_mod=2,
)
SHAMAN_MODS = ClassModifiers(
    hit_dice=6, mod_hp_flat=0, mod_hp_mult=5, mana_multiplier=10,
    mod_atk_physical=4, mod_atk_magical=8, mod_def_physical=2,
    mod_def_magical=4, regen_hp_mod=2, regen_mana_mod=4,
)

# --- Attribute presets ---


def _melee_attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 8, AttributeType.DEXTERITY: 6,
        AttributeType.CONSTITUTION: 7, AttributeType.INTELLIGENCE: 3,
        AttributeType.WISDOM: 4, AttributeType.CHARISMA: 3,
        AttributeType.MIND: 3,
    })


def _ranged_attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 5, AttributeType.DEXTERITY: 8,
        AttributeType.CONSTITUTION: 5, AttributeType.INTELLIGENCE: 5,
        AttributeType.WISDOM: 6, AttributeType.CHARISMA: 4,
        AttributeType.MIND: 5,
    })


def _caster_attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 3, AttributeType.DEXTERITY: 5,
        AttributeType.CONSTITUTION: 5, AttributeType.INTELLIGENCE: 9,
        AttributeType.WISDOM: 8, AttributeType.CHARISMA: 6,
        AttributeType.MIND: 9,
    })


def _orc_attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 7, AttributeType.DEXTERITY: 5,
        AttributeType.CONSTITUTION: 7, AttributeType.INTELLIGENCE: 3,
        AttributeType.WISDOM: 4, AttributeType.CHARISMA: 3,
        AttributeType.MIND: 3,
    })


# --- Helpers ---


def _make_skill_bar(skill_ids: list[str]) -> SkillBar:
    """Cria SkillBar com todas as skills num unico SpellSlot grande."""
    all_skills = load_skills()
    skills = tuple(all_skills[sid] for sid in skill_ids)
    total_cost = sum(s.slot_cost for s in skills)
    slot = SpellSlot(max_cost=total_cost + 10, skills=skills)
    return SkillBar(slots=(slot,))


def _make_inventory(item_quantities: dict[str, int]) -> Inventory:
    """Cria Inventory com consumiveis carregados do JSON."""
    all_consumables = load_consumables()
    inv = Inventory()
    for cid, qty in item_quantities.items():
        inv.add_item(all_consumables[cid], quantity=qty)
    return inv


# --- Fixture principal ---


@pytest.fixture
def battle_v2_setup():
    """Monta party + enemies + engine para Mock Battle v2."""
    weapons = load_weapons()
    armors = load_armors()
    accessories = load_accessories()
    profiles = load_profiles()

    # Party
    gareth = Character(
        name="Gareth", attributes=_melee_attrs(),
        config=CharacterConfig(
            class_modifiers=FIGHTER_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            weapon=weapons["longsword"],
            armor=armors["chain_mail"],
            accessories=(accessories["iron_ring"],),
            inventory=_make_inventory({"health_potion_small": 2}),
        ),
    )
    kael = Character(
        name="Kael", attributes=_ranged_attrs(),
        config=CharacterConfig(
            class_modifiers=RANGER_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            weapon=weapons["longbow"],
            armor=armors["studded_leather"],
            accessories=(accessories["cloak_of_speed"],),
            skill_bar=_make_skill_bar(["poison_strike"]),
        ),
    )
    aurelia = Character(
        name="Aurelia", attributes=_caster_attrs(),
        config=CharacterConfig(
            class_modifiers=CLERIC_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            weapon=weapons["mace"],
            armor=armors["scale_mail"],
            accessories=(accessories["amulet_of_wisdom"],),
            skill_bar=_make_skill_bar(["minor_heal"]),
            inventory=_make_inventory({"antidote": 2}),
        ),
    )
    lyra = Character(
        name="Lyra", attributes=_caster_attrs(),
        config=CharacterConfig(
            class_modifiers=SORCERER_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            armor=armors["mage_robes"],
            skill_bar=_make_skill_bar(["fireball", "ice_bolt"]),
            inventory=_make_inventory({"mana_potion_small": 2}),
        ),
    )

    # Enemies
    orc_0 = Character(
        name="Orc_0", attributes=_orc_attrs(),
        config=CharacterConfig(
            class_modifiers=ORC_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            weapon=weapons["greatsword"],
            inventory=_make_inventory({"health_potion_small": 1}),
        ),
    )
    orc_1 = Character(
        name="Orc_1", attributes=_orc_attrs(),
        config=CharacterConfig(
            class_modifiers=ORC_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            weapon=weapons["longsword"],
            skill_bar=_make_skill_bar(["weaken"]),
        ),
    )
    shaman = Character(
        name="Shaman", attributes=_caster_attrs(),
        config=CharacterConfig(
            class_modifiers=SHAMAN_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            weapon=weapons["dagger"],
            elemental_profile=profiles["fire_creature"],
            skill_bar=_make_skill_bar(["fireball"]),
        ),
    )

    party = [gareth, kael, aurelia, lyra]
    enemies = [orc_0, orc_1, shaman]

    # Handlers via CompositeHandler
    skill_h = SkillHandler()
    consumable_h = ConsumableHandler()
    basic_h = BasicAttackHandler()

    with_all = CompositeHandler((skill_h, consumable_h, basic_h))
    skill_or_attack = CompositeHandler((skill_h, basic_h))

    dispatch = DispatchTurnHandler(
        {
            "Gareth": CompositeHandler((consumable_h, basic_h)),
            "Kael": skill_or_attack,
            "Aurelia": with_all,
            "Lyra": with_all,
            "Orc_0": CompositeHandler((consumable_h, basic_h)),
            "Orc_1": skill_or_attack,
            "Shaman": skill_or_attack,
        },
        basic_h,
    )

    engine = CombatEngine(party, enemies, dispatch)
    return engine, party, enemies


# === Testes ===


class TestMockBattleV2Runs:
    def test_combat_runs_to_completion(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        result = engine.run_combat()
        assert result is not None

    def test_result_is_not_draw(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        result = engine.run_combat()
        assert result != CombatResult.DRAW

    def test_events_were_generated(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        engine.run_combat()
        assert len(engine.events) > 0


class TestMockBattleV2Participants:
    def test_all_party_members_appear(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        engine.run_combat()
        actors = {e.actor_name for e in engine.events}
        for name in ("Gareth", "Kael", "Aurelia", "Lyra"):
            assert name in actors

    def test_enemies_appear_in_events(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        engine.run_combat()
        actors = {e.actor_name for e in engine.events}
        enemy_names = {"Orc_0", "Orc_1", "Shaman"}
        assert actors & enemy_names


class TestMockBattleV2Skills:
    def test_heal_events_generated(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        engine.run_combat()
        heals = [e for e in engine.events if e.event_type == EngineEventType.HEAL]
        assert len(heals) >= 1

    def test_debuff_events_generated(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        engine.run_combat()
        debuffs = [e for e in engine.events if e.event_type == EngineEventType.DEBUFF]
        assert len(debuffs) >= 1

    def test_ailment_events_generated(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        engine.run_combat()
        ailments = [e for e in engine.events if e.event_type == EngineEventType.AILMENT]
        assert len(ailments) >= 1

    def test_multiple_event_types_in_battle(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        engine.run_combat()
        types = {e.event_type for e in engine.events}
        assert len(types) >= 3


class TestMockBattleV2Equipment:
    def test_party_has_weapons(self, battle_v2_setup) -> None:
        _, party, _ = battle_v2_setup
        gareth, kael, aurelia, _ = party
        assert gareth.weapon is not None
        assert kael.weapon is not None
        assert aurelia.weapon is not None

    def test_party_has_armor(self, battle_v2_setup) -> None:
        _, party, _ = battle_v2_setup
        for char in party:
            assert char.armor is not None

    def test_party_has_accessories(self, battle_v2_setup) -> None:
        _, party, _ = battle_v2_setup
        gareth, kael, aurelia, _ = party
        assert len(gareth.accessories) == 1
        assert len(kael.accessories) == 1
        assert len(aurelia.accessories) == 1


class TestMockBattleV2Consumables:
    def test_inventory_decremented(self, battle_v2_setup) -> None:
        engine, party, enemies = battle_v2_setup
        gareth = party[0]
        orc_0 = enemies[0]
        initial_gareth = gareth.inventory.get_quantity("health_potion_small")
        initial_orc = orc_0.inventory.get_quantity("health_potion_small")
        engine.run_combat()
        final_gareth = gareth.inventory.get_quantity("health_potion_small")
        final_orc = orc_0.inventory.get_quantity("health_potion_small")
        assert final_gareth < initial_gareth or final_orc < initial_orc

    def test_heal_from_consumable_or_skill(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        engine.run_combat()
        heals = [
            e for e in engine.events
            if e.event_type in (EngineEventType.HEAL, EngineEventType.MANA_RESTORE)
        ]
        assert len(heals) >= 1


class TestMockBattleV2Elemental:
    def test_shaman_has_elemental_profile(self, battle_v2_setup) -> None:
        _, _, enemies = battle_v2_setup
        shaman = enemies[2]
        assert shaman.elemental_profile is not None
        assert shaman.elemental_profile.is_resistant_to(ElementType.FIRE)

    def test_fire_damage_events_exist(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        engine.run_combat()
        damage_events = [e for e in engine.events if e.damage is not None]
        assert len(damage_events) >= 1


class TestMockBattleV2Log:
    def test_combat_log_has_entries(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        engine.run_combat()
        log = CombatLog()
        for event in engine.events:
            log.add_from_combat_event(event)
        assert len(log.entries) > 0

    def test_log_contains_multiple_event_types(self, battle_v2_setup) -> None:
        engine, _, _ = battle_v2_setup
        engine.run_combat()
        log = CombatLog()
        for event in engine.events:
            log.add_from_combat_event(event)
        types = {e.event_type for e in log.entries}
        assert len(types) >= 2

    def test_formatted_log_is_readable(self, battle_v2_setup, capsys) -> None:
        engine, _, _ = battle_v2_setup
        result = engine.run_combat()
        log = CombatLog()
        for event in engine.events:
            log.add_from_combat_event(event)
        text = LogFormatter.to_text(log)
        print(f"\n=== MOCK BATTLE V2 ({engine.round_number} rounds) ===")
        print(text)
        print(f"=== RESULT: {result.name} ===")
        captured = capsys.readouterr()
        assert "Round" in captured.out
        assert result.name in captured.out
