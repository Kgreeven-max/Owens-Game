"""
Arena Brawl - Obstacle Entity
Map obstacles that block movement and provide cover
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Obstacle:
    """An obstacle in the arena"""
    id: str
    x: float
    y: float
    width: float
    height: float

    # Properties
    is_destructible: bool = False
    hp: int = 100
    max_hp: int = 100
    provides_cover: bool = True  # For cop mechanic

    # Visual
    obstacle_type: str = "crate"  # crate, barrel, wall, etc.
    color: str = "#8B4513"

    # State
    is_destroyed: bool = False

    def take_damage(self, damage: int) -> bool:
        """Damage the obstacle, return True if destroyed"""
        if not self.is_destructible:
            return False

        self.hp -= damage
        if self.hp <= 0:
            self.is_destroyed = True
            return True
        return False

    def to_dict(self) -> dict:
        """Serialize for network"""
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'type': self.obstacle_type,
            'color': self.color,
            'is_destructible': self.is_destructible,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'is_destroyed': self.is_destroyed
        }


# Predefined obstacle types
OBSTACLE_PRESETS = {
    'crate': {
        'width': 60,
        'height': 60,
        'is_destructible': True,
        'hp': 50,
        'color': '#8B4513',
        'provides_cover': True
    },
    'barrel': {
        'width': 40,
        'height': 50,
        'is_destructible': True,
        'hp': 30,
        'color': '#654321',
        'provides_cover': True
    },
    'wall': {
        'width': 20,
        'height': 150,
        'is_destructible': False,
        'hp': 999,
        'color': '#696969',
        'provides_cover': True
    },
    'platform': {
        'width': 200,
        'height': 20,
        'is_destructible': False,
        'hp': 999,
        'color': '#556B2F',
        'provides_cover': False
    }
}


def create_obstacle(id: str, x: float, y: float, obstacle_type: str) -> Obstacle:
    """Create an obstacle from preset"""
    preset = OBSTACLE_PRESETS.get(obstacle_type, OBSTACLE_PRESETS['crate'])
    return Obstacle(
        id=id,
        x=x,
        y=y,
        width=preset['width'],
        height=preset['height'],
        is_destructible=preset['is_destructible'],
        hp=preset['hp'],
        max_hp=preset['hp'],
        provides_cover=preset['provides_cover'],
        obstacle_type=obstacle_type,
        color=preset['color']
    )
