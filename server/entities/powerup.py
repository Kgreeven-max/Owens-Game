"""
Arena Brawl - Power-up Entity
Collectible items that provide buffs
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import random


class PowerUpType(Enum):
    SPEED_BOOST = "speed_boost"
    DAMAGE_BOOST = "damage_boost"
    INVINCIBILITY = "invincibility"


@dataclass
class PowerUp:
    """A power-up that can be collected by players"""
    id: str
    x: float
    y: float
    powerup_type: PowerUpType
    duration: float = 5.0  # How long the effect lasts
    multiplier: float = 1.25  # Boost amount

    # Animation
    animation_frame: int = 0
    bob_offset: float = 0.0  # For floating animation

    # State
    is_active: bool = True
    spawn_time: float = 0.0

    def update(self, dt: float):
        """Update power-up animation"""
        self.animation_frame = (self.animation_frame + 1) % 60
        self.bob_offset = 5 * (0.5 + 0.5 * (self.animation_frame / 30 - 1) ** 2)

    def to_dict(self) -> dict:
        """Serialize for network"""
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y + self.bob_offset,
            'type': self.powerup_type.value,
            'is_active': self.is_active
        }

    @staticmethod
    def create_random(id: str, x: float, y: float) -> 'PowerUp':
        """Create a random power-up"""
        powerup_type = random.choice(list(PowerUpType))
        multiplier = 1.25 if powerup_type != PowerUpType.INVINCIBILITY else 1.0
        duration = 5.0 if powerup_type != PowerUpType.INVINCIBILITY else 3.0

        return PowerUp(
            id=id,
            x=x,
            y=y,
            powerup_type=powerup_type,
            duration=duration,
            multiplier=multiplier
        )
