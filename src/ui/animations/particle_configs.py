"""Particle configs per element — data-driven visual tuning."""

from __future__ import annotations

from src.ui.animations.particle import ParticleConfig

FIRE_CONFIG = ParticleConfig(
    name="fire",
    count=25, duration_ms=500,
    lifetime_range=(200, 400),
    speed_range=(0.03, 0.08),
    angle_range=(240, 300),
    size_range=(2, 5), size_decay=0.3,
    colors=[(255, 120, 30), (255, 80, 0), (255, 200, 50)],
    gravity=-0.0001, shape="circle", spawn_area="bottom",
)

ICE_CONFIG = ParticleConfig(
    name="ice",
    count=15, duration_ms=450,
    lifetime_range=(300, 450),
    speed_range=(0.04, 0.10),
    angle_range=(0, 360),
    size_range=(3, 7), size_decay=0.8,
    colors=[(130, 200, 255), (180, 230, 255), (220, 240, 255)],
    gravity=0.00005, shape="diamond", spawn_area="center",
)

LIGHTNING_CONFIG = ParticleConfig(
    name="lightning",
    count=12, duration_ms=300,
    lifetime_range=(100, 200),
    speed_range=(0.05, 0.12),
    angle_range=(0, 360),
    size_range=(2, 3), size_decay=0.4,
    colors=[(255, 255, 100), (255, 255, 200), (200, 200, 255)],
    gravity=0.0, shape="spark", spawn_area="full",
)

HOLY_CONFIG = ParticleConfig(
    name="holy",
    count=20, duration_ms=600,
    lifetime_range=(400, 600),
    speed_range=(0.02, 0.04),
    angle_range=(240, 300),
    size_range=(2, 4), size_decay=0.5,
    colors=[(255, 255, 200), (255, 240, 150), (255, 220, 100)],
    gravity=0.00003, shape="diamond", spawn_area="full",
)

DARKNESS_CONFIG = ParticleConfig(
    name="darkness",
    count=18, duration_ms=550,
    lifetime_range=(350, 550),
    speed_range=(0.01, 0.03),
    angle_range=(0, 360),
    size_range=(4, 8), size_decay=0.6,
    colors=[(100, 50, 150), (80, 30, 120), (60, 20, 100)],
    gravity=0.0, shape="circle", spawn_area="edges",
)

WATER_CONFIG = ParticleConfig(
    name="water",
    count=20, duration_ms=450,
    lifetime_range=(250, 400),
    speed_range=(0.05, 0.10),
    angle_range=(200, 340),
    size_range=(2, 4), size_decay=0.5,
    colors=[(50, 130, 255), (80, 160, 255), (120, 190, 255)],
    gravity=0.00015, shape="circle", spawn_area="center",
)

EARTH_CONFIG = ParticleConfig(
    name="earth",
    count=15, duration_ms=400,
    lifetime_range=(200, 350),
    speed_range=(0.06, 0.12),
    angle_range=(220, 320),
    size_range=(3, 6), size_decay=0.6,
    colors=[(160, 120, 60), (140, 100, 40), (120, 80, 30)],
    gravity=0.0002, shape="diamond", spawn_area="bottom",
)

PSYCHIC_CONFIG = ParticleConfig(
    name="psychic",
    count=12, duration_ms=500,
    lifetime_range=(300, 500),
    speed_range=(0.02, 0.05),
    angle_range=(0, 360),
    size_range=(2, 4), size_decay=0.5,
    colors=[(255, 150, 200), (255, 120, 180), (220, 100, 160)],
    gravity=0.0, shape="diamond", spawn_area="edges",
)

FORCE_CONFIG = ParticleConfig(
    name="force",
    count=20, duration_ms=350,
    lifetime_range=(150, 300),
    speed_range=(0.05, 0.10),
    angle_range=(0, 360),
    size_range=(2, 5), size_decay=0.4,
    colors=[(200, 200, 200), (220, 220, 220), (240, 240, 240)],
    gravity=0.00005, shape="spark", spawn_area="center",
)

CELESTIAL_CONFIG = ParticleConfig(
    name="celestial",
    count=16, duration_ms=600,
    lifetime_range=(400, 600),
    speed_range=(0.02, 0.04),
    angle_range=(0, 360),
    size_range=(2, 4), size_decay=0.5,
    colors=[(200, 180, 255), (180, 160, 240), (220, 200, 255)],
    gravity=0.0, shape="circle", spawn_area="center",
)

HEAL_CONFIG = ParticleConfig(
    name="heal",
    count=15, duration_ms=500,
    lifetime_range=(300, 500),
    speed_range=(0.02, 0.05),
    angle_range=(240, 300),
    size_range=(2, 5), size_decay=0.5,
    colors=[(80, 255, 80), (120, 255, 120), (160, 255, 160)],
    gravity=-0.00005, shape="circle", spawn_area="bottom",
    blocking=True,
)
