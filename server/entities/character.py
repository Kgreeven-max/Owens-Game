"""
Arena Brawl - Character Definitions
12 unique fighters with different abilities and stats (SSB-style roster)
"""
from dataclasses import dataclass, field
from typing import Callable, Optional, Dict
from enum import Enum

from .player import PlayerStats


class SpecialAbility(Enum):
    # Original 4
    FIRE_DASH = "fire_dash"
    SHIELD_BLOCK = "shield_block"
    TELEPORT = "teleport"
    LIGHTNING_STRIKE = "lightning_strike"
    # New characters
    ICE_SHARD = "ice_shard"           # Frost
    COMMAND_GRAB = "command_grab"     # Titan
    CLONE_ILLUSION = "clone_illusion" # Whisper
    ELECTRIC_CHAIN = "electric_chain" # Volt
    ROCK_ARMOR = "rock_armor"         # Golem
    WIND_GUST = "wind_gust"           # Aria
    RAGE_BOOST = "rage_boost"         # Fang
    HADOUKEN = "hadouken"             # Nova


@dataclass
class MovesetModifiers:
    """Character-specific attack modifiers"""
    # Ground attack damage multipliers
    jab_damage: float = 1.0
    ftilt_damage: float = 1.0
    utilt_damage: float = 1.0
    dtilt_damage: float = 1.0
    fsmash_damage: float = 1.0
    usmash_damage: float = 1.0
    dsmash_damage: float = 1.0
    # Aerial attack damage multipliers
    nair_damage: float = 1.0
    fair_damage: float = 1.0
    bair_damage: float = 1.0
    uair_damage: float = 1.0
    dair_damage: float = 1.0
    # Throw damage multipliers
    fthrow_damage: float = 1.0
    bthrow_damage: float = 1.0
    uthrow_damage: float = 1.0
    dthrow_damage: float = 1.0
    # Special properties
    has_super_armor_smash: bool = False  # Armor during smash attacks
    has_meteor_dair: bool = True         # Dair can spike
    air_jumps: int = 2                   # Number of air jumps
    wall_jump: bool = False              # Can wall jump
    float_ability: bool = False          # Can float in air


@dataclass
class CharacterDefinition:
    """Defines a playable character"""
    name: str
    display_name: str
    description: str
    style: str                  # Archetype description
    weight: str                 # light/medium/heavy
    stats: PlayerStats
    special_ability: SpecialAbility
    special_cooldown: float     # seconds
    color: str                  # Primary color for UI/effects
    secondary_color: str = ""   # Secondary color

    # Attack ranges
    light_attack_range: float = 60.0
    heavy_attack_range: float = 80.0
    special_range: float = 100.0

    # Moveset modifiers
    moveset: MovesetModifiers = field(default_factory=MovesetModifiers)

    # Animation frames (for frontend)
    sprite_sheet: str = ""

    # Unique traits
    traits: list = field(default_factory=list)


# Character Definitions - Full 12 Character Roster
CHARACTERS = {
    # ==================== ORIGINAL 4 (Upgraded) ====================

    "Blaze": CharacterDefinition(
        name="Blaze",
        display_name="Blaze",
        description="Aggressive rushdown fighter with fire abilities. High damage, low defense.",
        style="Rushdown",
        weight="medium",
        stats=PlayerStats(
            max_hp=90,
            attack=1.3,      # High ATK
            defense=0.8,     # Low DEF
            speed=1.15,
            jump_power=1.0
        ),
        special_ability=SpecialAbility.FIRE_DASH,
        special_cooldown=8.0,
        color="#FF4500",  # Orange-red
        secondary_color="#FFD700",
        light_attack_range=65,
        heavy_attack_range=85,
        special_range=150,
        moveset=MovesetModifiers(
            jab_damage=1.1,
            ftilt_damage=1.2,
            fair_damage=1.3,     # Strong forward air
            bair_damage=1.2,
            fsmash_damage=1.4,   # High damage smashes
            usmash_damage=1.3,
            has_meteor_dair=True,
            air_jumps=2
        ),
        traits=["fire_attacks", "damage_over_time", "fast_startup"]
    ),

    "Tank": CharacterDefinition(
        name="Tank",
        display_name="Tank",
        description="Defensive superheavy with damage reduction and armored attacks.",
        style="Super Heavy",
        weight="heavy",
        stats=PlayerStats(
            max_hp=130,
            attack=0.9,
            defense=1.4,     # High DEF
            speed=0.7,       # Low SPD
            jump_power=0.8
        ),
        special_ability=SpecialAbility.SHIELD_BLOCK,
        special_cooldown=10.0,
        color="#4169E1",  # Royal blue
        secondary_color="#1E3A8A",
        light_attack_range=55,
        heavy_attack_range=90,  # Long range smashes
        special_range=0,
        moveset=MovesetModifiers(
            fsmash_damage=1.5,   # Devastating smashes
            usmash_damage=1.4,
            dsmash_damage=1.4,
            fthrow_damage=1.3,
            bthrow_damage=1.5,   # Strong back throw
            has_super_armor_smash=True,  # Armor on smashes!
            has_meteor_dair=True,
            air_jumps=1          # Only 1 air jump
        ),
        traits=["super_armor", "slow_but_strong", "hard_to_kill"]
    ),

    "Shadow": CharacterDefinition(
        name="Shadow",
        display_name="Shadow",
        description="Glass cannon with teleportation and devastating combos.",
        style="Glass Cannon",
        weight="light",
        stats=PlayerStats(
            max_hp=75,       # Low HP
            attack=1.15,
            defense=0.85,
            speed=1.4,       # High SPD
            jump_power=1.2
        ),
        special_ability=SpecialAbility.TELEPORT,
        special_cooldown=6.0,
        color="#8A2BE2",  # Purple
        secondary_color="#4B0082",
        light_attack_range=55,
        heavy_attack_range=70,
        special_range=200,
        moveset=MovesetModifiers(
            jab_damage=0.9,
            dtilt_damage=1.2,    # Good combo starter
            nair_damage=1.1,
            fair_damage=1.2,
            uair_damage=1.3,     # Strong juggle
            dair_damage=1.4,     # Powerful spike
            has_meteor_dair=True,
            air_jumps=3,         # Triple jump!
            wall_jump=True       # Can wall jump
        ),
        traits=["teleport", "combo_focused", "high_mobility"]
    ),

    "Storm": CharacterDefinition(
        name="Storm",
        display_name="Storm",
        description="Balanced all-rounder with chain lightning attacks.",
        style="All-Rounder",
        weight="medium",
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
        secondary_color="#87CEEB",
        light_attack_range=60,
        heavy_attack_range=80,
        special_range=120,
        moveset=MovesetModifiers(
            # All balanced at 1.0
            utilt_damage=1.1,    # Slight boost to anti-air
            uair_damage=1.1,
            has_meteor_dair=True,
            air_jumps=2
        ),
        traits=["electric_stun", "chain_lightning", "versatile"]
    ),

    # ==================== NEW CHARACTERS ====================

    "Frost": CharacterDefinition(
        name="Frost",
        display_name="Frost",
        description="Zoner with ice projectiles and freeze traps. Controls space.",
        style="Zoner",
        weight="medium",
        stats=PlayerStats(
            max_hp=95,
            attack=0.95,
            defense=1.0,
            speed=0.9,       # Slightly slow
            jump_power=1.0
        ),
        special_ability=SpecialAbility.ICE_SHARD,
        special_cooldown=5.0,  # Fast projectile cooldown
        color="#00CED1",  # Dark Cyan
        secondary_color="#E0FFFF",
        light_attack_range=70,   # Long range pokes
        heavy_attack_range=85,
        special_range=300,       # Long range projectile
        moveset=MovesetModifiers(
            ftilt_damage=1.1,
            dtilt_damage=1.0,
            fair_damage=0.9,     # Weak aerials
            bair_damage=1.2,     # Good bair for spacing
            fsmash_damage=1.1,
            has_meteor_dair=False,  # No spike
            air_jumps=2
        ),
        traits=["ice_projectile", "freeze_effect", "stage_control"]
    ),

    "Titan": CharacterDefinition(
        name="Titan",
        display_name="Titan",
        description="Grappler with devastating command grabs and piledrivers.",
        style="Grappler",
        weight="heavy",
        stats=PlayerStats(
            max_hp=120,
            attack=1.2,
            defense=1.2,
            speed=0.65,      # Very slow
            jump_power=0.75
        ),
        special_ability=SpecialAbility.COMMAND_GRAB,
        special_cooldown=8.0,
        color="#8B4513",  # Saddle Brown
        secondary_color="#654321",
        light_attack_range=50,
        heavy_attack_range=70,
        special_range=80,        # Command grab range
        moveset=MovesetModifiers(
            jab_damage=1.0,
            fsmash_damage=1.3,
            dsmash_damage=1.2,
            fthrow_damage=1.6,   # Devastating throws!
            bthrow_damage=1.8,   # Best throw in game
            uthrow_damage=1.4,
            dthrow_damage=1.5,   # Piledriver!
            has_super_armor_smash=True,
            has_meteor_dair=True,
            air_jumps=1
        ),
        traits=["command_grab", "throw_combos", "piledriver"]
    ),

    "Whisper": CharacterDefinition(
        name="Whisper",
        display_name="Whisper",
        description="Tricky fighter with clones, counters, and misdirection.",
        style="Tricky",
        weight="light",
        stats=PlayerStats(
            max_hp=80,
            attack=1.0,
            defense=0.9,
            speed=1.2,
            jump_power=1.1
        ),
        special_ability=SpecialAbility.CLONE_ILLUSION,
        special_cooldown=7.0,
        color="#9932CC",  # Dark Orchid
        secondary_color="#DA70D6",
        light_attack_range=55,
        heavy_attack_range=70,
        special_range=0,         # Clone appears at position
        moveset=MovesetModifiers(
            jab_damage=0.85,     # Weak jab
            dtilt_damage=1.1,
            nair_damage=1.2,     # Good nair
            fair_damage=1.0,
            bair_damage=1.3,     # Tricky bair
            has_meteor_dair=False,
            air_jumps=2,
            wall_jump=True
        ),
        traits=["clone_illusion", "counter", "mix_ups"]
    ),

    "Volt": CharacterDefinition(
        name="Volt",
        display_name="Volt",
        description="Speed demon with electric dash chains. Fastest fighter.",
        style="Speedster",
        weight="light",
        stats=PlayerStats(
            max_hp=70,       # Lowest HP
            attack=0.9,
            defense=0.75,    # Fragile
            speed=1.6,       # FASTEST
            jump_power=1.15
        ),
        special_ability=SpecialAbility.ELECTRIC_CHAIN,
        special_cooldown=4.0,    # Fast cooldown
        color="#00FF00",  # Lime
        secondary_color="#ADFF2F",
        light_attack_range=50,
        heavy_attack_range=65,
        special_range=120,
        moveset=MovesetModifiers(
            jab_damage=0.8,      # Weak but fast
            ftilt_damage=0.85,
            utilt_damage=0.9,
            dtilt_damage=1.0,
            nair_damage=1.1,
            fair_damage=1.0,
            uair_damage=1.0,
            dair_damage=1.2,     # Decent spike
            fsmash_damage=0.9,   # Weak smashes
            has_meteor_dair=True,
            air_jumps=3,
            wall_jump=True
        ),
        traits=["electric_chains", "multi_dash", "hit_and_run"]
    ),

    "Golem": CharacterDefinition(
        name="Golem",
        display_name="Golem",
        description="Slowest but heaviest. Rock armor and ground-shaking attacks.",
        style="Juggernaut",
        weight="heavy",
        stats=PlayerStats(
            max_hp=150,      # HIGHEST HP
            attack=1.1,
            defense=1.5,     # HIGHEST DEF
            speed=0.5,       # SLOWEST
            jump_power=0.7
        ),
        special_ability=SpecialAbility.ROCK_ARMOR,
        special_cooldown=15.0,   # Long cooldown
        color="#708090",  # Slate Gray
        secondary_color="#2F4F4F",
        light_attack_range=60,
        heavy_attack_range=100,  # Huge range
        special_range=0,
        moveset=MovesetModifiers(
            jab_damage=1.2,
            ftilt_damage=1.3,
            fsmash_damage=1.6,   # Enormous damage
            usmash_damage=1.5,
            dsmash_damage=1.7,   # Ground pound!
            dair_damage=1.8,     # Devastating spike
            has_super_armor_smash=True,
            has_meteor_dair=True,
            air_jumps=1
        ),
        traits=["rock_armor", "ground_pound", "earthquake"]
    ),

    "Aria": CharacterDefinition(
        name="Aria",
        display_name="Aria",
        description="Aerial specialist with wind attacks. Best air game.",
        style="Aerial",
        weight="light",
        stats=PlayerStats(
            max_hp=85,
            attack=0.95,
            defense=0.9,
            speed=1.1,
            jump_power=1.4   # HIGHEST jump
        ),
        special_ability=SpecialAbility.WIND_GUST,
        special_cooldown=6.0,
        color="#87CEEB",  # Sky Blue
        secondary_color="#F0F8FF",
        light_attack_range=55,
        heavy_attack_range=70,
        special_range=150,       # Wind push distance
        moveset=MovesetModifiers(
            jab_damage=0.85,
            ftilt_damage=0.9,
            dtilt_damage=0.9,
            nair_damage=1.4,     # Excellent aerials
            fair_damage=1.3,
            bair_damage=1.4,     # Kill move
            uair_damage=1.5,     # Best uair
            dair_damage=1.2,
            fsmash_damage=0.85,  # Weak ground game
            has_meteor_dair=True,
            air_jumps=4,         # FOUR air jumps!
            float_ability=True   # Can float!
        ),
        traits=["wind_control", "float", "aerial_dominance"]
    ),

    "Fang": CharacterDefinition(
        name="Fang",
        display_name="Fang",
        description="Wild brawler with rage mechanic. Gets stronger at low HP.",
        style="Brawler",
        weight="medium",
        stats=PlayerStats(
            max_hp=105,
            attack=1.1,
            defense=0.95,
            speed=1.05,
            jump_power=1.0
        ),
        special_ability=SpecialAbility.RAGE_BOOST,
        special_cooldown=20.0,   # Long cooldown, powerful effect
        color="#DC143C",  # Crimson
        secondary_color="#8B0000",
        light_attack_range=60,
        heavy_attack_range=80,
        special_range=0,
        moveset=MovesetModifiers(
            jab_damage=1.15,
            ftilt_damage=1.2,
            utilt_damage=1.1,
            dtilt_damage=1.1,
            nair_damage=1.1,
            fair_damage=1.2,
            bair_damage=1.3,
            fsmash_damage=1.3,
            usmash_damage=1.2,
            has_meteor_dair=True,
            air_jumps=2
        ),
        traits=["rage_mechanic", "wild_attacks", "bite"]
    ),

    "Nova": CharacterDefinition(
        name="Nova",
        display_name="Nova",
        description="Classic shoto with hadouken, uppercut, and hurricane kick.",
        style="Shoto",
        weight="medium",
        stats=PlayerStats(
            max_hp=100,
            attack=1.05,
            defense=1.0,
            speed=1.0,
            jump_power=1.0
        ),
        special_ability=SpecialAbility.HADOUKEN,
        special_cooldown=3.0,    # Fast projectile
        color="#FF6347",  # Tomato
        secondary_color="#FF4500",
        light_attack_range=60,
        heavy_attack_range=80,
        special_range=400,       # Fireball travels far
        moveset=MovesetModifiers(
            jab_damage=1.0,
            ftilt_damage=1.1,
            utilt_damage=1.2,    # Uppercut reference
            dtilt_damage=1.0,
            nair_damage=1.0,
            fair_damage=1.1,
            bair_damage=1.1,
            uair_damage=1.2,
            fsmash_damage=1.2,
            usmash_damage=1.4,   # Shoryuken smash!
            has_meteor_dair=True,
            air_jumps=2
        ),
        traits=["hadouken", "shoryuken", "tatsumaki"]
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
    """Handles special ability execution for all 12 characters"""

    # ==================== ORIGINAL 4 ====================

    @staticmethod
    def fire_dash(player, direction: float, arena) -> dict:
        """
        Blaze's Fire Dash - Rapid gap closer that damages enemies
        Leaves a fire trail that deals damage over time
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
            'damage': 15 * player.stats.attack,
            'burn_damage': 3,  # DoT per tick
            'burn_duration': 2.0
        }

    @staticmethod
    def shield_block(player, duration: float = 3.0) -> dict:
        """
        Tank's Shield Block - Massive damage reduction for a duration
        Also reflects 20% of blocked damage
        """
        player.stats.defense *= 2.5  # 2.5x defense during shield
        player.shield_active = True
        player.shield_end_time = duration

        return {
            'type': 'shield_block',
            'player_id': player.id,
            'duration': duration,
            'defense_boost': 2.5,
            'reflect_percent': 0.2
        }

    @staticmethod
    def teleport(player, target_x: float, target_y: float, arena) -> dict:
        """
        Shadow's Teleport - Short-range blink to target location
        Brief invincibility during teleport
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
            'to_y': target_y,
            'invincible_frames': 8
        }

    @staticmethod
    def lightning_strike(player, arena) -> dict:
        """
        Storm's Lightning Strike - AoE damage around the player
        Can chain to nearby enemies
        """
        aoe_radius = 120
        damage = 25 * player.stats.attack

        return {
            'type': 'lightning_strike',
            'player_id': player.id,
            'x': player.x,
            'y': player.y,
            'radius': aoe_radius,
            'damage': damage,
            'chain_range': 80,
            'chain_damage_falloff': 0.6
        }

    # ==================== NEW CHARACTERS ====================

    @staticmethod
    def ice_shard(player, direction: float, arena) -> dict:
        """
        Frost's Ice Shard - Fast projectile that slows enemies
        Can create ice trap on ground
        """
        projectile_speed = 15
        shard_damage = 8 * player.stats.attack

        return {
            'type': 'ice_shard',
            'player_id': player.id,
            'start_x': player.x,
            'start_y': player.y,
            'direction': direction,
            'speed': projectile_speed,
            'damage': shard_damage,
            'slow_percent': 0.4,
            'slow_duration': 1.5,
            'creates_trap': player.input_down  # Hold down to create ground trap
        }

    @staticmethod
    def command_grab(player, direction: float, arena) -> dict:
        """
        Titan's Command Grab - Unblockable grab with armor
        Leads into piledriver if successful
        """
        grab_range = 80
        grab_speed = 12

        # Armored lunge forward
        player.vx = grab_speed * direction
        player.has_armor = True

        return {
            'type': 'command_grab',
            'player_id': player.id,
            'direction': direction,
            'range': grab_range,
            'damage': 20 * player.stats.attack,
            'armor_frames': 15,
            'grab_startup': 8,
            'grab_active': 6
        }

    @staticmethod
    def clone_illusion(player, direction: float, arena) -> dict:
        """
        Whisper's Clone Illusion - Create a clone that mimics actions
        Clone can be detonated or used as misdirection
        """
        clone_offset = 100 * direction

        return {
            'type': 'clone_illusion',
            'player_id': player.id,
            'clone_x': player.x + clone_offset,
            'clone_y': player.y,
            'clone_duration': 4.0,
            'clone_hp': 1,  # Dies in one hit
            'detonate_damage': 12 * player.stats.attack,
            'detonate_radius': 60
        }

    @staticmethod
    def electric_chain(player, direction: float, arena) -> dict:
        """
        Volt's Electric Chain - Dash that can be chained 3 times
        Each chain can change direction
        """
        chain_distance = 100
        chain_speed = 20

        # Track chain count
        if not hasattr(player, 'electric_chain_count'):
            player.electric_chain_count = 0

        player.electric_chain_count += 1
        can_chain = player.electric_chain_count < 3

        player.vx = chain_speed * direction

        return {
            'type': 'electric_chain',
            'player_id': player.id,
            'chain_number': player.electric_chain_count,
            'can_chain_again': can_chain,
            'direction': direction,
            'distance': chain_distance,
            'damage': 6 * player.stats.attack,
            'stun_frames': 5
        }

    @staticmethod
    def rock_armor(player, duration: float = 5.0) -> dict:
        """
        Golem's Rock Armor - Become super armored but even slower
        Take reduced damage but can't be knocked back
        """
        player.stats.defense *= 2.0
        player.stats.speed *= 0.5  # Even slower
        player.has_super_armor = True
        player.rock_armor_end = duration

        return {
            'type': 'rock_armor',
            'player_id': player.id,
            'duration': duration,
            'defense_boost': 2.0,
            'speed_reduction': 0.5,
            'knockback_resistance': 0.8  # 80% knockback reduction
        }

    @staticmethod
    def wind_gust(player, direction: float, arena) -> dict:
        """
        Aria's Wind Gust - Push enemies away and boost own air mobility
        Can be aimed in 8 directions
        """
        push_force = 15
        push_radius = 120

        # Determine gust direction from input
        gust_dx = direction
        gust_dy = -1 if player.input_up else (1 if player.input_down else 0)

        return {
            'type': 'wind_gust',
            'player_id': player.id,
            'x': player.x,
            'y': player.y,
            'direction_x': gust_dx,
            'direction_y': gust_dy,
            'push_force': push_force,
            'radius': push_radius,
            'damage': 5 * player.stats.attack,
            'self_boost': 8  # Boost own movement opposite direction
        }

    @staticmethod
    def rage_boost(player, arena) -> dict:
        """
        Fang's Rage Boost - Temporarily massively boost damage
        Bonus scales with missing HP
        """
        # Calculate rage bonus based on missing HP
        hp_percent = player.hp / player.stats.max_hp
        missing_hp_bonus = 1.0 + (1.0 - hp_percent) * 0.5  # Up to 50% bonus at low HP

        base_attack_boost = 1.5
        total_boost = base_attack_boost * missing_hp_bonus

        player.stats.attack *= total_boost
        player.rage_active = True
        player.rage_end = 6.0  # 6 second duration

        return {
            'type': 'rage_boost',
            'player_id': player.id,
            'attack_boost': total_boost,
            'duration': 6.0,
            'hp_percent': hp_percent,
            'visual_intensity': 1.0 - hp_percent  # More intense visuals at low HP
        }

    @staticmethod
    def hadouken(player, direction: float, arena) -> dict:
        """
        Nova's Hadouken - Classic fireball projectile
        Can be charged for more damage and size
        """
        # Check if charged (hold special button)
        charge_level = getattr(player, 'hadouken_charge', 0)
        is_charged = charge_level > 30  # 30 frames = half second

        projectile_speed = 10 if is_charged else 12
        base_damage = 12 if is_charged else 8
        projectile_size = 1.5 if is_charged else 1.0

        # Reset charge
        player.hadouken_charge = 0

        return {
            'type': 'hadouken',
            'player_id': player.id,
            'start_x': player.x + (40 * direction),
            'start_y': player.y,
            'direction': direction,
            'speed': projectile_speed,
            'damage': base_damage * player.stats.attack,
            'size': projectile_size,
            'is_charged': is_charged,
            'transcendent': is_charged  # Charged version goes through other projectiles
        }


# Mapping abilities to handlers - All 12 characters
ABILITY_HANDLERS = {
    # Original 4
    SpecialAbility.FIRE_DASH: SpecialAbilityHandler.fire_dash,
    SpecialAbility.SHIELD_BLOCK: SpecialAbilityHandler.shield_block,
    SpecialAbility.TELEPORT: SpecialAbilityHandler.teleport,
    SpecialAbility.LIGHTNING_STRIKE: SpecialAbilityHandler.lightning_strike,
    # New 8
    SpecialAbility.ICE_SHARD: SpecialAbilityHandler.ice_shard,
    SpecialAbility.COMMAND_GRAB: SpecialAbilityHandler.command_grab,
    SpecialAbility.CLONE_ILLUSION: SpecialAbilityHandler.clone_illusion,
    SpecialAbility.ELECTRIC_CHAIN: SpecialAbilityHandler.electric_chain,
    SpecialAbility.ROCK_ARMOR: SpecialAbilityHandler.rock_armor,
    SpecialAbility.WIND_GUST: SpecialAbilityHandler.wind_gust,
    SpecialAbility.RAGE_BOOST: SpecialAbilityHandler.rage_boost,
    SpecialAbility.HADOUKEN: SpecialAbilityHandler.hadouken,
}
