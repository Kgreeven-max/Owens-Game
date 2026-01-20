"""
Arena Brawl - Health Box Entity
Tiered health boxes with unlock tiers
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import random


class HealthBoxTier(Enum):
    COMMON = "common"      # Brown box - small heal
    RARE = "rare"          # Silver box - medium heal + buff
    EPIC = "epic"          # Gold box - full heal + invincibility


TIER_PROPERTIES = {
    HealthBoxTier.COMMON: {
        'color': '#8B4513',  # Brown
        'heal_amount': 15,
        'speed_boost': 1.1,
        'speed_duration': 3.0,
        'spawn_weight': 60  # 60% chance
    },
    HealthBoxTier.RARE: {
        'color': '#C0C0C0',  # Silver
        'heal_amount': 35,
        'damage_boost': 1.25,
        'damage_duration': 5.0,
        'spawn_weight': 30  # 30% chance
    },
    HealthBoxTier.EPIC: {
        'color': '#FFD700',  # Gold
        'heal_amount': 100,
        'invincibility_duration': 3.0,
        'spawn_weight': 10  # 10% chance
    }
}


@dataclass
class HealthBox:
    """A health box that heals players and may provide buffs"""
    id: str
    x: float
    y: float
    tier: HealthBoxTier

    # Animation
    animation_frame: int = 0
    glow_intensity: float = 0.0

    # State
    is_active: bool = True
    spawn_time: float = 0.0

    @property
    def properties(self) -> dict:
        """Get tier properties"""
        return TIER_PROPERTIES[self.tier]

    @property
    def color(self) -> str:
        """Get box color"""
        return self.properties['color']

    @property
    def heal_amount(self) -> int:
        """Get heal amount"""
        return self.properties['heal_amount']

    def update(self, dt: float):
        """Update health box animation"""
        self.animation_frame = (self.animation_frame + 1) % 120
        # Pulsing glow effect
        self.glow_intensity = 0.5 + 0.5 * abs((self.animation_frame / 60) - 1)

    def apply_to_player(self, player) -> dict:
        """Apply health box effects to a player"""
        effects = {
            'healed': 0,
            'buff_type': None,
            'buff_duration': 0
        }

        # Heal
        old_hp = player.hp
        player.heal(self.heal_amount)
        effects['healed'] = player.hp - old_hp

        props = self.properties

        # Apply tier-specific buffs
        if self.tier == HealthBoxTier.COMMON:
            if 'speed_boost' in props:
                player.apply_buff(speed_boost=props['speed_boost'],
                                  duration=props['speed_duration'])
                effects['buff_type'] = 'speed'
                effects['buff_duration'] = props['speed_duration']

        elif self.tier == HealthBoxTier.RARE:
            if 'damage_boost' in props:
                player.apply_buff(damage_boost=props['damage_boost'],
                                  duration=props['damage_duration'])
                effects['buff_type'] = 'damage'
                effects['buff_duration'] = props['damage_duration']

        elif self.tier == HealthBoxTier.EPIC:
            if 'invincibility_duration' in props:
                player.set_invincible(props['invincibility_duration'])
                effects['buff_type'] = 'invincibility'
                effects['buff_duration'] = props['invincibility_duration']

        self.is_active = False
        return effects

    def to_dict(self) -> dict:
        """Serialize for network"""
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'tier': self.tier.value,
            'color': self.color,
            'glow': self.glow_intensity,
            'is_active': self.is_active
        }

    @staticmethod
    def create_random(id: str, x: float, y: float) -> 'HealthBox':
        """Create a random tier health box based on spawn weights"""
        total_weight = sum(props['spawn_weight'] for props in TIER_PROPERTIES.values())
        roll = random.randint(1, total_weight)

        cumulative = 0
        for tier, props in TIER_PROPERTIES.items():
            cumulative += props['spawn_weight']
            if roll <= cumulative:
                return HealthBox(id=id, x=x, y=y, tier=tier)

        return HealthBox(id=id, x=x, y=y, tier=HealthBoxTier.COMMON)
