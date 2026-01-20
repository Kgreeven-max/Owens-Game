"""
Arena Brawl - Training Mode
Practice mode with frame data display, hitbox visualization, and combo counter
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import time

from server.entities.player import Player, PlayerState, AttackType
from server.entities.character import get_character, ATTACK_DATA


class TrainingOption(Enum):
    """Training mode options"""
    CPU_BEHAVIOR = "cpu_behavior"
    HITBOX_DISPLAY = "hitbox_display"
    FRAME_DATA = "frame_data"
    DI_DISPLAY = "di_display"
    INFINITE_JUMPS = "infinite_jumps"
    INVINCIBILITY = "invincibility"
    DAMAGE_DISPLAY = "damage_display"
    INPUT_DISPLAY = "input_display"


class CPUBehavior(Enum):
    """CPU training dummy behaviors"""
    STAND = "stand"            # Just stand still
    WALK = "walk"              # Walk back and forth
    JUMP = "jump"              # Jump repeatedly
    CROUCH = "crouch"          # Stay crouched
    SHIELD = "shield"          # Always shielding/blocking
    DODGE = "dodge"            # Spot dodge on hit
    ATTACK = "attack"          # Attack randomly
    GRAB_BREAK = "grab_break"  # Mash out of grabs
    DI_RANDOM = "di_random"    # Random DI during hitstun
    DI_AWAY = "di_away"        # Always DI away
    DI_TOWARD = "di_toward"    # Always DI toward


@dataclass
class FrameDataInfo:
    """Frame data for an attack"""
    attack_name: str
    startup_frames: int        # Frames before hitbox active
    active_frames: int         # Frames hitbox is active
    endlag_frames: int         # Frames of recovery
    total_frames: int          # Total animation length
    damage: int
    base_knockback: float
    knockback_scaling: float
    angle: int                 # Knockback angle in degrees
    on_shield: int             # Frame advantage on shield
    landing_lag: int = 0       # Landing lag for aerials
    autocancels: str = ""      # Autocancel windows


@dataclass
class ComboData:
    """Tracks combo information"""
    hit_count: int = 0
    total_damage: int = 0
    last_hit_time: float = 0.0
    combo_window: float = 0.8  # Seconds before combo resets
    max_combo: int = 0
    attacks_used: List[str] = field(default_factory=list)
    is_true_combo: bool = True  # True if no escape frames


@dataclass
class TrainingState:
    """State for training mode"""
    # Options
    cpu_behavior: CPUBehavior = CPUBehavior.STAND
    show_hitboxes: bool = True
    show_frame_data: bool = True
    show_di: bool = False
    infinite_jumps: bool = False
    player_invincible: bool = False
    show_damage: bool = True
    show_inputs: bool = True

    # CPU state
    cpu_damage: int = 0        # Can be set manually
    cpu_auto_reset: bool = True  # Auto reset damage after combo drops

    # Combo tracking per player
    player_combo: ComboData = field(default_factory=ComboData)
    cpu_combo: ComboData = field(default_factory=ComboData)

    # Frame counter
    current_frame: int = 0
    attack_frame: int = 0
    stun_frames_remaining: int = 0

    # Input history
    input_history: List[dict] = field(default_factory=list)
    max_input_history: int = 60  # Show last 60 inputs


class TrainingMode:
    """Training mode manager"""

    def __init__(self):
        self.state = TrainingState()
        self.active = False
        self.player_id: str = ""
        self.cpu_id: str = ""

    def initialize(self, player_id: str, cpu_id: str):
        """Start training mode"""
        self.active = True
        self.player_id = player_id
        self.cpu_id = cpu_id
        self.state = TrainingState()

    def set_option(self, option: TrainingOption, value):
        """Set a training option"""
        if option == TrainingOption.CPU_BEHAVIOR:
            if isinstance(value, str):
                self.state.cpu_behavior = CPUBehavior(value)
            else:
                self.state.cpu_behavior = value
        elif option == TrainingOption.HITBOX_DISPLAY:
            self.state.show_hitboxes = bool(value)
        elif option == TrainingOption.FRAME_DATA:
            self.state.show_frame_data = bool(value)
        elif option == TrainingOption.DI_DISPLAY:
            self.state.show_di = bool(value)
        elif option == TrainingOption.INFINITE_JUMPS:
            self.state.infinite_jumps = bool(value)
        elif option == TrainingOption.INVINCIBILITY:
            self.state.player_invincible = bool(value)
        elif option == TrainingOption.DAMAGE_DISPLAY:
            self.state.show_damage = bool(value)
        elif option == TrainingOption.INPUT_DISPLAY:
            self.state.show_inputs = bool(value)

    def set_cpu_damage(self, damage: int):
        """Set CPU damage percentage"""
        self.state.cpu_damage = max(0, min(999, damage))

    def reset_cpu(self, player: Player):
        """Reset CPU to starting state"""
        player.hp = player.stats.max_hp
        player.vx = 0
        player.vy = 0
        player.state = PlayerState.IDLE
        self.state.cpu_damage = 0
        self.state.cpu_combo = ComboData()

    def get_cpu_input(self, cpu: Player, player: Player) -> dict:
        """Generate CPU input based on behavior setting"""
        behavior = self.state.cpu_behavior
        input_data = {
            'move': 'none',
            'action': 'none',
            'up': False,
            'down': False,
            'jump': False,
            'heavy': False,
            'dodge': False,
            'grab': False
        }

        if behavior == CPUBehavior.STAND:
            pass  # No input

        elif behavior == CPUBehavior.WALK:
            # Walk toward player
            if cpu.x < player.x - 50:
                input_data['move'] = 'right'
            elif cpu.x > player.x + 50:
                input_data['move'] = 'left'

        elif behavior == CPUBehavior.JUMP:
            if cpu.on_ground:
                input_data['jump'] = True

        elif behavior == CPUBehavior.CROUCH:
            input_data['down'] = True

        elif behavior == CPUBehavior.SHIELD:
            input_data['action'] = 'block'

        elif behavior == CPUBehavior.DODGE:
            if cpu.state == PlayerState.STUNNED:
                input_data['action'] = 'dodge'

        elif behavior == CPUBehavior.ATTACK:
            import random
            if random.random() < 0.02:  # 2% chance per frame
                input_data['action'] = 'attack'

        elif behavior == CPUBehavior.GRAB_BREAK:
            if cpu.grabbed_by_id:
                # Mash inputs to escape grab
                input_data['move'] = 'left' if (self.state.current_frame % 2) == 0 else 'right'
                input_data['action'] = 'attack'

        elif behavior == CPUBehavior.DI_RANDOM:
            if cpu.state in [PlayerState.STUNNED, PlayerState.TUMBLING]:
                import random
                directions = ['left', 'right', 'none']
                input_data['move'] = random.choice(directions)
                input_data['up'] = random.random() < 0.5
                input_data['down'] = random.random() < 0.5

        elif behavior == CPUBehavior.DI_AWAY:
            if cpu.state in [PlayerState.STUNNED, PlayerState.TUMBLING]:
                if cpu.x < player.x:
                    input_data['move'] = 'left'
                else:
                    input_data['move'] = 'right'

        elif behavior == CPUBehavior.DI_TOWARD:
            if cpu.state in [PlayerState.STUNNED, PlayerState.TUMBLING]:
                if cpu.x < player.x:
                    input_data['move'] = 'right'
                else:
                    input_data['move'] = 'left'

        return input_data

    def record_input(self, input_data: dict):
        """Record player input for display"""
        self.state.input_history.append({
            'frame': self.state.current_frame,
            'time': time.time(),
            **input_data
        })

        # Keep only recent inputs
        if len(self.state.input_history) > self.state.max_input_history:
            self.state.input_history.pop(0)

    def record_hit(self, attacker_id: str, damage: int, attack_type: AttackType,
                   hitstun_frames: int):
        """Record a hit for combo tracking"""
        current_time = time.time()

        if attacker_id == self.player_id:
            combo = self.state.player_combo
        else:
            combo = self.state.cpu_combo

        # Check if combo continues
        time_since_last = current_time - combo.last_hit_time
        if time_since_last > combo.combo_window:
            # Combo dropped, reset
            combo.hit_count = 0
            combo.total_damage = 0
            combo.attacks_used = []
            combo.is_true_combo = True

        # Add this hit
        combo.hit_count += 1
        combo.total_damage += damage
        combo.last_hit_time = current_time
        combo.attacks_used.append(attack_type.value)

        # Update max combo
        if combo.hit_count > combo.max_combo:
            combo.max_combo = combo.hit_count

        # Track stun frames for true combo detection
        self.state.stun_frames_remaining = hitstun_frames

    def update(self, player: Player, cpu: Player):
        """Update training state each frame"""
        self.state.current_frame += 1

        # Track stun frames
        if self.state.stun_frames_remaining > 0:
            self.state.stun_frames_remaining -= 1

        # Reset CPU damage if combo dropped and auto-reset enabled
        if self.state.cpu_auto_reset:
            player_combo = self.state.player_combo
            if player_combo.hit_count > 0:
                time_since = time.time() - player_combo.last_hit_time
                if time_since > player_combo.combo_window:
                    # Combo dropped, reset CPU
                    cpu.hp = cpu.stats.max_hp
                    self.state.cpu_damage = 0

        # Apply infinite jumps if enabled
        if self.state.infinite_jumps:
            player.air_jumps_used = 0

        # Apply invincibility if enabled
        if self.state.player_invincible:
            player.invincible_until = time.time() + 1.0

        # Track attack frame data
        if player.state == PlayerState.ATTACKING:
            self.state.attack_frame += 1
        else:
            self.state.attack_frame = 0

    def get_attack_frame_data(self, character: str, attack_type: AttackType) -> FrameDataInfo:
        """Get frame data for a specific attack"""
        char_def = get_character(character)
        if not char_def:
            return self._get_default_frame_data(attack_type)

        # Get attack data from character definition
        attack_key = attack_type.value
        if attack_key in ATTACK_DATA:
            data = ATTACK_DATA[attack_key]

            # Calculate frames from attack duration
            startup = data.get('startup_frames', 4)
            active = data.get('active_frames', 3)
            endlag = data.get('endlag_frames', 10)
            total = startup + active + endlag

            return FrameDataInfo(
                attack_name=attack_type.value.replace('_', ' ').title(),
                startup_frames=startup,
                active_frames=active,
                endlag_frames=endlag,
                total_frames=total,
                damage=data.get('base_damage', 10),
                base_knockback=data.get('knockback', 5),
                knockback_scaling=data.get('kb_scaling', 0.1),
                angle=data.get('angle', 45),
                on_shield=data.get('shield_stun', -5),
                landing_lag=data.get('landing_lag', 6) if 'air' in attack_key or attack_key in ['nair', 'fair', 'bair', 'uair', 'dair'] else 0,
                autocancels=data.get('autocancel', '')
            )

        return self._get_default_frame_data(attack_type)

    def _get_default_frame_data(self, attack_type: AttackType) -> FrameDataInfo:
        """Default frame data if not defined"""
        # Default values based on attack type
        defaults = {
            AttackType.JAB: (3, 2, 8, 8, 3, 0, 45),
            AttackType.FTILT: (6, 3, 12, 10, 8, 0.05, 40),
            AttackType.UTILT: (5, 4, 14, 9, 7, 0.05, 80),
            AttackType.DTILT: (5, 3, 10, 8, 5, 0.04, 30),
            AttackType.DASH_ATTACK: (8, 4, 16, 12, 10, 0.08, 50),
            AttackType.FSMASH: (14, 3, 24, 18, 15, 0.12, 45),
            AttackType.USMASH: (12, 4, 22, 17, 14, 0.11, 85),
            AttackType.DSMASH: (10, 4, 20, 15, 12, 0.1, 30),
            AttackType.NAIR: (5, 12, 10, 10, 6, 0.05, 45),
            AttackType.FAIR: (8, 3, 14, 12, 10, 0.08, 45),
            AttackType.BAIR: (7, 3, 16, 14, 12, 0.1, 35),
            AttackType.UAIR: (5, 4, 12, 11, 9, 0.07, 80),
            AttackType.DAIR: (12, 3, 18, 13, 11, 0.09, 270),
        }

        if attack_type in defaults:
            s, a, e, d, kb, kbs, ang = defaults[attack_type]
            return FrameDataInfo(
                attack_name=attack_type.value.replace('_', ' ').title(),
                startup_frames=s,
                active_frames=a,
                endlag_frames=e,
                total_frames=s + a + e,
                damage=d,
                base_knockback=kb,
                knockback_scaling=kbs,
                angle=ang,
                on_shield=-5,
                landing_lag=8 if attack_type in [AttackType.NAIR, AttackType.FAIR, AttackType.BAIR, AttackType.UAIR, AttackType.DAIR] else 0
            )

        return FrameDataInfo(
            attack_name=attack_type.value,
            startup_frames=6,
            active_frames=3,
            endlag_frames=12,
            total_frames=21,
            damage=10,
            base_knockback=8,
            knockback_scaling=0.08,
            angle=45,
            on_shield=-5
        )

    def get_hitbox_data(self, player: Player) -> List[dict]:
        """Get hitbox visualization data for current attack"""
        if player.state != PlayerState.ATTACKING:
            return []

        hitboxes = []
        attack_type = player.current_attack
        frame_data = self.get_attack_frame_data(player.character, attack_type)

        # Check if in active frames
        if frame_data.startup_frames <= self.state.attack_frame < frame_data.startup_frames + frame_data.active_frames:
            # Generate hitbox based on attack type
            hitbox = self._generate_hitbox(player, attack_type)
            if hitbox:
                hitboxes.append(hitbox)

        return hitboxes

    def _generate_hitbox(self, player: Player, attack_type: AttackType) -> Optional[dict]:
        """Generate hitbox data for attack visualization"""
        facing = 1 if player.facing_right else -1

        # Default hitbox dimensions based on attack type
        hitbox_configs = {
            AttackType.JAB: {'x': 20, 'y': -15, 'w': 35, 'h': 25},
            AttackType.FTILT: {'x': 25, 'y': -20, 'w': 45, 'h': 35},
            AttackType.UTILT: {'x': 0, 'y': -50, 'w': 40, 'h': 45},
            AttackType.DTILT: {'x': 20, 'y': 5, 'w': 50, 'h': 20},
            AttackType.DASH_ATTACK: {'x': 30, 'y': -15, 'w': 50, 'h': 40},
            AttackType.FSMASH: {'x': 30, 'y': -25, 'w': 60, 'h': 50},
            AttackType.USMASH: {'x': 0, 'y': -60, 'w': 50, 'h': 60},
            AttackType.DSMASH: {'x': 0, 'y': 0, 'w': 80, 'h': 30},
            AttackType.NAIR: {'x': 0, 'y': 0, 'w': 50, 'h': 50},
            AttackType.FAIR: {'x': 25, 'y': -10, 'w': 45, 'h': 35},
            AttackType.BAIR: {'x': -30, 'y': -10, 'w': 45, 'h': 35},
            AttackType.UAIR: {'x': 0, 'y': -45, 'w': 40, 'h': 45},
            AttackType.DAIR: {'x': 0, 'y': 20, 'w': 35, 'h': 45},
        }

        config = hitbox_configs.get(attack_type)
        if not config:
            return None

        return {
            'x': player.x + (config['x'] * facing),
            'y': player.y + config['y'],
            'width': config['w'],
            'height': config['h'],
            'type': 'attack',
            'attack': attack_type.value
        }

    def get_hurtbox_data(self, player: Player) -> dict:
        """Get hurtbox visualization data"""
        # Basic hurtbox - varies by state
        width = 40
        height = 60

        if player.state == PlayerState.CROUCHING:
            height = 35
        elif not player.on_ground:
            height = 50

        return {
            'x': player.x - width / 2,
            'y': player.y - height,
            'width': width,
            'height': height,
            'type': 'hurtbox'
        }

    def get_state(self) -> dict:
        """Get training mode state for network sync"""
        return {
            'active': self.active,
            'cpu_behavior': self.state.cpu_behavior.value,
            'options': {
                'show_hitboxes': self.state.show_hitboxes,
                'show_frame_data': self.state.show_frame_data,
                'show_di': self.state.show_di,
                'infinite_jumps': self.state.infinite_jumps,
                'player_invincible': self.state.player_invincible,
                'show_damage': self.state.show_damage,
                'show_inputs': self.state.show_inputs
            },
            'cpu_damage': self.state.cpu_damage,
            'player_combo': {
                'hits': self.state.player_combo.hit_count,
                'damage': self.state.player_combo.total_damage,
                'max_combo': self.state.player_combo.max_combo,
                'is_true': self.state.player_combo.is_true_combo,
                'attacks': self.state.player_combo.attacks_used[-5:]  # Last 5 attacks
            },
            'frame': self.state.current_frame,
            'attack_frame': self.state.attack_frame,
            'stun_remaining': self.state.stun_frames_remaining,
            'input_history': self.state.input_history[-10:]  # Last 10 inputs
        }


# Attack data reference (would normally be in character definitions)
ATTACK_DATA = {
    'jab': {'startup_frames': 3, 'active_frames': 2, 'endlag_frames': 8, 'base_damage': 3, 'knockback': 2, 'kb_scaling': 0.01, 'angle': 80},
    'jab2': {'startup_frames': 3, 'active_frames': 2, 'endlag_frames': 8, 'base_damage': 3, 'knockback': 2, 'kb_scaling': 0.01, 'angle': 80},
    'jab3': {'startup_frames': 4, 'active_frames': 3, 'endlag_frames': 12, 'base_damage': 5, 'knockback': 5, 'kb_scaling': 0.03, 'angle': 45},
    'ftilt': {'startup_frames': 6, 'active_frames': 3, 'endlag_frames': 12, 'base_damage': 10, 'knockback': 8, 'kb_scaling': 0.05, 'angle': 40},
    'utilt': {'startup_frames': 5, 'active_frames': 4, 'endlag_frames': 14, 'base_damage': 9, 'knockback': 7, 'kb_scaling': 0.05, 'angle': 80},
    'dtilt': {'startup_frames': 5, 'active_frames': 3, 'endlag_frames': 10, 'base_damage': 8, 'knockback': 5, 'kb_scaling': 0.04, 'angle': 30},
    'dash_attack': {'startup_frames': 8, 'active_frames': 4, 'endlag_frames': 16, 'base_damage': 12, 'knockback': 10, 'kb_scaling': 0.08, 'angle': 50},
    'fsmash': {'startup_frames': 14, 'active_frames': 3, 'endlag_frames': 24, 'base_damage': 18, 'knockback': 15, 'kb_scaling': 0.12, 'angle': 45},
    'usmash': {'startup_frames': 12, 'active_frames': 4, 'endlag_frames': 22, 'base_damage': 17, 'knockback': 14, 'kb_scaling': 0.11, 'angle': 85},
    'dsmash': {'startup_frames': 10, 'active_frames': 4, 'endlag_frames': 20, 'base_damage': 15, 'knockback': 12, 'kb_scaling': 0.1, 'angle': 30},
    'nair': {'startup_frames': 5, 'active_frames': 12, 'endlag_frames': 10, 'base_damage': 10, 'knockback': 6, 'kb_scaling': 0.05, 'angle': 45, 'landing_lag': 6},
    'fair': {'startup_frames': 8, 'active_frames': 3, 'endlag_frames': 14, 'base_damage': 12, 'knockback': 10, 'kb_scaling': 0.08, 'angle': 45, 'landing_lag': 8},
    'bair': {'startup_frames': 7, 'active_frames': 3, 'endlag_frames': 16, 'base_damage': 14, 'knockback': 12, 'kb_scaling': 0.1, 'angle': 35, 'landing_lag': 10},
    'uair': {'startup_frames': 5, 'active_frames': 4, 'endlag_frames': 12, 'base_damage': 11, 'knockback': 9, 'kb_scaling': 0.07, 'angle': 80, 'landing_lag': 6},
    'dair': {'startup_frames': 12, 'active_frames': 3, 'endlag_frames': 18, 'base_damage': 13, 'knockback': 11, 'kb_scaling': 0.09, 'angle': 270, 'landing_lag': 14},
    'neutral_b': {'startup_frames': 10, 'active_frames': 5, 'endlag_frames': 20, 'base_damage': 15, 'knockback': 10, 'kb_scaling': 0.08, 'angle': 45},
    'side_b': {'startup_frames': 12, 'active_frames': 8, 'endlag_frames': 18, 'base_damage': 14, 'knockback': 12, 'kb_scaling': 0.1, 'angle': 45},
    'up_b': {'startup_frames': 8, 'active_frames': 10, 'endlag_frames': 30, 'base_damage': 12, 'knockback': 8, 'kb_scaling': 0.06, 'angle': 80},
    'down_b': {'startup_frames': 15, 'active_frames': 4, 'endlag_frames': 22, 'base_damage': 16, 'knockback': 14, 'kb_scaling': 0.11, 'angle': 60},
}
