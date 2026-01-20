"""
Arena Brawl - Character Definitions
4 unique fighters with different abilities and stats
"""
from dataclasses import dataclass
from typing import Callable, Optional
from enum import Enum

from .player import PlayerStats


class SpecialAbility(Enum):
    FIRE_DASH = "fire_dash"
    SHIELD_BLOCK = "shield_block"
    TELEPORT = "teleport"
    LIGHTNING_STRIKE = "lightning_strike"


@dataclass
class CharacterDefinition:
    """Defines a playable character"""
    name: str
    display_name: str
    description: str
    style: str
    stats: PlayerStats
    special_ability: SpecialAbility
    special_cooldown: float  # seconds
    color: str  # Primary color for UI/effects

    # Attack properties
    light_attack_range: float = 60.0
    heavy_attack_range: float = 80.0
    special_range: float = 100.0

    # Animation frames (for frontend)
    sprite_sheet: str = ""


# Character Definitions based on the plan
CHARACTERS = {
    "Blaze": CharacterDefinition(
        name="Blaze",
        display_name="Blaze",
        description="Aggressive fighter with fire abilities",
        style="Aggressive",
        stats=PlayerStats(
            max_hp=90,
            attack=1.3,      # High ATK
            defense=0.8,     # Low DEF
            speed=1.1,
            jump_power=1.0
        ),
        special_ability=SpecialAbility.FIRE_DASH,
        special_cooldown=8.0,
        color="#FF4500",  # Orange-red
        light_attack_range=65,
        heavy_attack_range=85,
        special_range=150  # Dash distance
    ),

    "Tank": CharacterDefinition(
        name="Tank",
        display_name="Tank",
        description="Defensive powerhouse with damage reduction",
        style="Defensive",
        stats=PlayerStats(
            max_hp=130,
            attack=0.9,
            defense=1.4,     # High DEF
            speed=0.7,       # Low SPD
            jump_power=0.85
        ),
        special_ability=SpecialAbility.SHIELD_BLOCK,
        special_cooldown=10.0,
        color="#4169E1",  # Royal blue
        light_attack_range=55,
        heavy_attack_range=75,
        special_range=0  # Shield is self-buff
    ),

    "Shadow": CharacterDefinition(
        name="Shadow",
        display_name="Shadow",
        description="Elusive fighter who can teleport",
        style="Evasive",
        stats=PlayerStats(
            max_hp=75,       # Low HP
            attack=1.0,
            defense=0.9,
            speed=1.4,       # High SPD
            jump_power=1.2
        ),
        special_ability=SpecialAbility.TELEPORT,
        special_cooldown=6.0,
        color="#8A2BE2",  # Purple
        light_attack_range=55,
        heavy_attack_range=70,
        special_range=200  # Teleport distance
    ),

    "Storm": CharacterDefinition(
        name="Storm",
        display_name="Storm",
        description="Balanced fighter with lightning powers",
        style="Balanced",
        stats=PlayerStats(
            max_hp=100,
            attack=1.0,
            defense=1.0,
            speed=1.0,
            jump_power=1.0
        ),
        special_ability=SpecialAbility.LIGHTNING_STRIKE,
        special_cooldown=12.0,
        color="#FFD700",  # Gold
        light_attack_range=60,
        heavy_attack_range=80,
        special_range=120  # AoE radius
    )
}


def get_character(name: str) -> Optional[CharacterDefinition]:
    """Get character definition by name"""
    return CHARACTERS.get(name)


def get_all_characters() -> list:
    """Get list of all available characters"""
    return list(CHARACTERS.values())


def get_character_names() -> list:
    """Get list of character names"""
    return list(CHARACTERS.keys())


class SpecialAbilityHandler:
    """Handles special ability execution"""

    @staticmethod
    def fire_dash(player, direction: float, arena) -> dict:
        """
        Blaze's Fire Dash - Rapid gap closer that damages enemies
        Returns effect data for the client
        """
        dash_distance = 150
        dash_speed = 25

        # Set velocity for dash
        player.vx = dash_speed if direction > 0 else -dash_speed
        player.state = "dashing"

        return {
            'type': 'fire_dash',
            'player_id': player.id,
            'start_x': player.x,
            'end_x': player.x + (dash_distance * direction),
            'damage': 15 * player.stats.attack
        }

    @staticmethod
    def shield_block(player, duration: float = 3.0) -> dict:
        """
        Tank's Shield Block - Massive damage reduction for a duration
        """
        original_defense = player.stats.defense
        player.stats.defense *= 2.5  # 2.5x defense during shield

        return {
            'type': 'shield_block',
            'player_id': player.id,
            'duration': duration,
            'defense_boost': 2.5
        }

    @staticmethod
    def teleport(player, target_x: float, target_y: float, arena) -> dict:
        """
        Shadow's Teleport - Short-range blink to target location
        """
        max_distance = 200

        # Calculate actual teleport destination (clamped to max distance)
        dx = target_x - player.x
        dy = target_y - player.y
        distance = (dx**2 + dy**2) ** 0.5

        if distance > max_distance:
            ratio = max_distance / distance
            target_x = player.x + dx * ratio
            target_y = player.y + dy * ratio

        # Clamp to arena bounds
        target_x = max(50, min(arena.width - 50, target_x))
        target_y = max(50, min(arena.ground_y, target_y))

        old_x, old_y = player.x, player.y
        player.x = target_x
        player.y = target_y

        return {
            'type': 'teleport',
            'player_id': player.id,
            'from_x': old_x,
            'from_y': old_y,
            'to_x': target_x,
            'to_y': target_y
        }

    @staticmethod
    def lightning_strike(player, arena) -> dict:
        """
        Storm's Lightning Strike - AoE damage around the player
        """
        aoe_radius = 120
        damage = 25 * player.stats.attack

        return {
            'type': 'lightning_strike',
            'player_id': player.id,
            'x': player.x,
            'y': player.y,
            'radius': aoe_radius,
            'damage': damage
        }


# Mapping abilities to handlers
ABILITY_HANDLERS = {
    SpecialAbility.FIRE_DASH: SpecialAbilityHandler.fire_dash,
    SpecialAbility.SHIELD_BLOCK: SpecialAbilityHandler.shield_block,
    SpecialAbility.TELEPORT: SpecialAbilityHandler.teleport,
    SpecialAbility.LIGHTNING_STRIKE: SpecialAbilityHandler.lightning_strike,
}
