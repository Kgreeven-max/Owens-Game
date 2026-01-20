"""
Arena Brawl - Player Entity
Handles player state, movement, and actions
"""
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class PlayerState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    JUMPING = "jumping"
    FALLING = "falling"
    ATTACKING = "attacking"
    BLOCKING = "blocking"
    STUNNED = "stunned"
    DEAD = "dead"


class AttackType(Enum):
    NONE = "none"
    LIGHT = "light"
    HEAVY = "heavy"
    SPECIAL = "special"


@dataclass
class PlayerStats:
    """Character-specific stats"""
    max_hp: int = 100
    attack: float = 1.0  # Damage multiplier
    defense: float = 1.0  # Damage reduction multiplier
    speed: float = 1.0  # Movement speed multiplier
    jump_power: float = 1.0  # Jump height multiplier


@dataclass
class Player:
    """Main player class for Arena Brawl"""
    id: str
    name: str
    character: str = "Storm"  # Default character

    # Position and physics
    x: float = 640.0
    y: float = 600.0
    vx: float = 0.0
    vy: float = 0.0
    facing_right: bool = True
    on_ground: bool = True

    # Stats
    stats: PlayerStats = field(default_factory=PlayerStats)
    hp: int = 100
    lives: int = 3

    # State
    state: PlayerState = PlayerState.IDLE
    current_attack: AttackType = AttackType.NONE

    # Combat timing
    attack_start_time: float = 0.0
    attack_cooldown: float = 0.0
    special_cooldown: float = 0.0
    stun_end_time: float = 0.0
    invincible_until: float = 0.0

    # Combo system
    combo_count: int = 0
    last_hit_time: float = 0.0
    combo_window: float = 0.5

    # Buffs
    damage_boost: float = 1.0
    speed_boost: float = 1.0
    buff_end_time: float = 0.0

    # Input state (set by network/AI)
    input_left: bool = False
    input_right: bool = False
    input_jump: bool = False
    input_attack: bool = False
    input_heavy: bool = False
    input_special: bool = False
    input_block: bool = False

    # Hiding state (for cop mechanic)
    is_hiding: bool = False

    # Animation
    animation: str = "idle"
    animation_frame: int = 0

    # Network
    is_bot: bool = False
    is_connected: bool = True

    def __post_init__(self):
        """Initialize HP from stats"""
        self.hp = self.stats.max_hp

    def set_character_stats(self, stats: PlayerStats):
        """Apply character-specific stats"""
        self.stats = stats
        self.hp = stats.max_hp

    def take_damage(self, damage: int, knockback_x: float = 0, knockback_y: float = 0):
        """Apply damage to player with knockback"""
        if time.time() < self.invincible_until:
            return 0

        # Apply defense and block reduction
        actual_damage = damage * (1.0 / self.stats.defense)
        if self.state == PlayerState.BLOCKING:
            actual_damage *= 0.5
            knockback_x *= 0.3
            knockback_y *= 0.3

        self.hp = max(0, self.hp - int(actual_damage))
        self.vx += knockback_x
        self.vy += knockback_y

        if self.hp <= 0:
            self.die()

        return int(actual_damage)

    def heal(self, amount: int):
        """Heal the player"""
        self.hp = min(self.stats.max_hp, self.hp + amount)

    def die(self):
        """Handle player death"""
        self.state = PlayerState.DEAD
        self.lives -= 1
        self.animation = "death"

    def respawn(self, x: float, y: float, invincibility_time: float = 2.0):
        """Respawn player at position with brief invincibility"""
        if self.lives > 0:
            self.x = x
            self.y = y
            self.vx = 0
            self.vy = 0
            self.hp = self.stats.max_hp
            self.state = PlayerState.IDLE
            self.invincible_until = time.time() + invincibility_time
            self.animation = "spawn"

    def start_attack(self, attack_type: AttackType):
        """Begin an attack animation"""
        if self.state in [PlayerState.ATTACKING, PlayerState.STUNNED, PlayerState.DEAD]:
            return False

        self.state = PlayerState.ATTACKING
        self.current_attack = attack_type
        self.attack_start_time = time.time()

        # Set animation based on attack type
        if attack_type == AttackType.LIGHT:
            self.animation = f"attack_light_{self.combo_count % 3}"
        elif attack_type == AttackType.HEAVY:
            self.animation = "attack_heavy"
        elif attack_type == AttackType.SPECIAL:
            self.animation = "special"

        return True

    def can_combo(self) -> bool:
        """Check if player is within combo window"""
        return time.time() - self.last_hit_time < self.combo_window

    def add_combo_hit(self):
        """Register a hit for combo tracking"""
        if self.can_combo():
            self.combo_count += 1
        else:
            self.combo_count = 1
        self.last_hit_time = time.time()

    def apply_buff(self, damage_boost: float = 1.0, speed_boost: float = 1.0, duration: float = 5.0):
        """Apply temporary buff to player"""
        self.damage_boost = damage_boost
        self.speed_boost = speed_boost
        self.buff_end_time = time.time() + duration

    def set_invincible(self, duration: float):
        """Make player invincible for duration"""
        self.invincible_until = time.time() + duration

    def stun(self, duration: float):
        """Stun the player"""
        if self.state != PlayerState.DEAD:
            self.state = PlayerState.STUNNED
            self.stun_end_time = time.time() + duration
            self.animation = "stunned"

    def update_state(self):
        """Update player state based on timers"""
        current_time = time.time()

        # Clear buffs
        if current_time > self.buff_end_time:
            self.damage_boost = 1.0
            self.speed_boost = 1.0

        # Clear stun
        if self.state == PlayerState.STUNNED and current_time > self.stun_end_time:
            self.state = PlayerState.IDLE

        # Update animation based on state
        if self.state == PlayerState.IDLE and self.on_ground:
            if abs(self.vx) > 0.5:
                self.animation = "walk"
            else:
                self.animation = "idle"
        elif not self.on_ground:
            if self.vy < 0:
                self.animation = "jump"
            else:
                self.animation = "fall"

    def to_dict(self) -> dict:
        """Serialize player state for network transmission"""
        return {
            'id': self.id,
            'name': self.name,
            'character': self.character,
            'x': round(self.x, 1),
            'y': round(self.y, 1),
            'vx': round(self.vx, 1),
            'vy': round(self.vy, 1),
            'facing_right': self.facing_right,
            'hp': self.hp,
            'max_hp': self.stats.max_hp,
            'lives': self.lives,
            'state': self.state.value,
            'animation': self.animation,
            'animation_frame': self.animation_frame,
            'combo_count': self.combo_count,
            'is_invincible': time.time() < self.invincible_until,
            'is_hiding': self.is_hiding
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Player':
        """Create player from dict (for deserialization)"""
        player = cls(
            id=data['id'],
            name=data['name'],
            character=data.get('character', 'Storm')
        )
        player.x = data.get('x', 640)
        player.y = data.get('y', 600)
        return player
