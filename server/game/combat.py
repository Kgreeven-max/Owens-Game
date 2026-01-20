"""
Arena Brawl - Combat System
Handles attacks, damage, combos, and special abilities
"""
import time
import math
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum

from server.entities.player import Player, PlayerState, AttackType
from server.entities.character import (
    get_character, ABILITY_HANDLERS, SpecialAbility, CharacterDefinition
)
from server.game.physics import PhysicsEngine
from server.config import Config


class HitType(Enum):
    LIGHT = "light"
    HEAVY = "heavy"
    SPECIAL = "special"
    ENVIRONMENTAL = "environmental"


@dataclass
class AttackData:
    """Data for an attack"""
    attacker_id: str
    attack_type: AttackType
    damage: int
    knockback_x: float
    knockback_y: float
    knockback_angle: float  # Angle in degrees (0 = right, 90 = up)
    base_knockback: float   # Fixed knockback component
    knockback_scaling: float  # Scales with target damage %
    range: float
    startup_frames: int  # Frames before attack is active
    active_frames: int   # Frames attack hitbox is active
    recovery_frames: int  # Frames after attack before can act
    hitbox_offset_x: float = 0  # Offset from player center
    hitbox_offset_y: float = 0
    hitbox_width: float = 50
    hitbox_height: float = 40
    can_meteor: bool = False  # Can spike/meteor smash
    is_multihit: bool = False  # Hits multiple times


@dataclass
class HitResult:
    """Result of a hit connecting"""
    attacker_id: str
    target_id: str
    damage_dealt: int
    was_blocked: bool
    knockback_applied: Tuple[float, float]
    combo_count: int


class CombatSystem:
    """Manages all combat interactions"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.physics = PhysicsEngine(config)

        # Default attack data template
        def atk(attack_type, damage, angle, base_kb, kb_scaling, range_val,
                startup, active, recovery, **kwargs):
            return AttackData(
                attacker_id="",
                attack_type=attack_type,
                damage=damage,
                knockback_x=0,  # Calculated from angle
                knockback_y=0,
                knockback_angle=angle,
                base_knockback=base_kb,
                knockback_scaling=kb_scaling,
                range=range_val,
                startup_frames=startup,
                active_frames=active,
                recovery_frames=recovery,
                **kwargs
            )

        # Attack frame data (at 60 FPS) - SSB-style
        self.attack_data = {
            # === GROUND ATTACKS ===
            # Jab combo (3 hits)
            AttackType.JAB: atk(AttackType.JAB, 3, 45, 2, 0.05, 50,
                               startup=2, active=2, recovery=6),
            AttackType.JAB2: atk(AttackType.JAB2, 3, 45, 2, 0.05, 50,
                                startup=2, active=2, recovery=6),
            AttackType.JAB3: atk(AttackType.JAB3, 5, 45, 4, 0.1, 55,
                                startup=3, active=3, recovery=12),

            # Tilts
            AttackType.FTILT: atk(AttackType.FTILT, 9, 35, 4, 0.08, 65,
                                 startup=6, active=4, recovery=12),
            AttackType.UTILT: atk(AttackType.UTILT, 8, 80, 5, 0.1, 60,
                                 startup=5, active=5, recovery=14,
                                 hitbox_offset_y=-40),
            AttackType.DTILT: atk(AttackType.DTILT, 7, 25, 3, 0.06, 60,
                                 startup=5, active=3, recovery=10,
                                 hitbox_offset_y=20),

            # Dash attack
            AttackType.DASH_ATTACK: atk(AttackType.DASH_ATTACK, 10, 50, 5, 0.1, 70,
                                       startup=7, active=4, recovery=18),

            # === SMASH ATTACKS (base damage, scales with charge) ===
            AttackType.FSMASH: atk(AttackType.FSMASH, 16, 40, 8, 0.15, 80,
                                  startup=12, active=4, recovery=28),
            AttackType.USMASH: atk(AttackType.USMASH, 15, 85, 7, 0.14, 70,
                                  startup=10, active=5, recovery=26,
                                  hitbox_offset_y=-50),
            AttackType.DSMASH: atk(AttackType.DSMASH, 14, 30, 7, 0.12, 75,
                                  startup=8, active=6, recovery=24),

            # === AERIAL ATTACKS ===
            AttackType.NAIR: atk(AttackType.NAIR, 8, 45, 3, 0.08, 55,
                                startup=4, active=10, recovery=8,
                                hitbox_width=60, hitbox_height=60),
            AttackType.FAIR: atk(AttackType.FAIR, 10, 40, 4, 0.1, 60,
                                startup=6, active=3, recovery=14),
            AttackType.BAIR: atk(AttackType.BAIR, 12, 35, 6, 0.12, 55,
                                startup=8, active=3, recovery=16),
            AttackType.UAIR: atk(AttackType.UAIR, 9, 75, 4, 0.1, 55,
                                startup=5, active=4, recovery=12,
                                hitbox_offset_y=-45),
            AttackType.DAIR: atk(AttackType.DAIR, 11, 270, 5, 0.1, 50,
                                startup=10, active=3, recovery=20,
                                hitbox_offset_y=40, can_meteor=True),

            # === SPECIAL MOVES (base - overridden per character) ===
            AttackType.NEUTRAL_B: atk(AttackType.NEUTRAL_B, 12, 45, 5, 0.1, 100,
                                     startup=15, active=5, recovery=20),
            AttackType.SIDE_B: atk(AttackType.SIDE_B, 10, 40, 6, 0.1, 80,
                                  startup=12, active=8, recovery=18),
            AttackType.UP_B: atk(AttackType.UP_B, 8, 80, 4, 0.08, 60,
                                startup=8, active=10, recovery=25),
            AttackType.DOWN_B: atk(AttackType.DOWN_B, 14, 50, 6, 0.12, 70,
                                  startup=18, active=4, recovery=22),

            # === GRAB AND THROWS ===
            AttackType.GRAB: atk(AttackType.GRAB, 0, 0, 0, 0, 55,
                                startup=6, active=2, recovery=20),
            AttackType.PUMMEL: atk(AttackType.PUMMEL, 2, 0, 0, 0, 0,
                                  startup=2, active=1, recovery=8),
            AttackType.FTHROW: atk(AttackType.FTHROW, 8, 45, 6, 0.08, 0,
                                  startup=10, active=1, recovery=20),
            AttackType.BTHROW: atk(AttackType.BTHROW, 9, 135, 7, 0.1, 0,
                                  startup=12, active=1, recovery=22),
            AttackType.UTHROW: atk(AttackType.UTHROW, 7, 90, 5, 0.08, 0,
                                  startup=8, active=1, recovery=18),
            AttackType.DTHROW: atk(AttackType.DTHROW, 6, 270, 3, 0.05, 0,
                                  startup=10, active=1, recovery=20),

            # Legacy compatibility
            AttackType.LIGHT: atk(AttackType.LIGHT, 8, 45, 3, 0.08, 60,
                                 startup=3, active=4, recovery=8),
            AttackType.HEAVY: atk(AttackType.HEAVY, 20, 45, 8, 0.15, 80,
                                 startup=10, active=6, recovery=20),
            AttackType.SPECIAL: atk(AttackType.SPECIAL, 25, 50, 10, 0.12, 100,
                                   startup=8, active=8, recovery=25),
        }

        # Track attack states
        self.active_attacks: Dict[str, dict] = {}  # player_id -> attack info
        self.hit_this_attack: Dict[str, set] = {}  # player_id -> set of hit targets

        # Track grab states
        self.active_grabs: Dict[str, str] = {}  # grabber_id -> grabbed_id

    def process_attack_input(self, player: Player) -> Optional[AttackType]:
        """Process player attack input and start attack if valid"""
        # Can't attack in certain states
        locked_states = [PlayerState.STUNNED, PlayerState.DEAD, PlayerState.ATTACKING,
                        PlayerState.SPOT_DODGING, PlayerState.AIR_DODGING,
                        PlayerState.TUMBLING, PlayerState.LEDGE_HANG]
        if player.state in locked_states:
            return None

        current_time = time.time()

        # Handle smash charge release
        if player.smash_charging:
            if not player.input_attack and not player.input_heavy:
                # Release smash attack
                attack_type = self._get_smash_type(player.smash_type)
                if attack_type:
                    charge_mult = 1.0 + (player.smash_charge_frames / 60.0) * 0.4  # Up to 40% more damage
                    self._start_attack(player, attack_type, charge_multiplier=charge_mult)
                    player.smash_charging = False
                    player.smash_charge_frames = 0
                    return attack_type
            else:
                # Continue charging (max 60 frames = 1 second)
                player.smash_charge_frames = min(60, player.smash_charge_frames + 1)
            return None

        # Check grab input first
        if player.input_grab and player.on_ground and current_time >= player.attack_cooldown:
            return self._process_grab(player)

        # Check special attack (B button)
        if player.input_special and current_time >= player.special_cooldown:
            return self._process_special_input(player)

        # Check attack button
        if not player.input_attack:
            return None

        if current_time < player.attack_cooldown:
            return None

        # Determine attack type based on ground/air and direction
        if player.on_ground:
            return self._process_ground_attack(player, current_time)
        else:
            return self._process_aerial_attack(player)

    def _process_ground_attack(self, player: Player, current_time: float) -> Optional[AttackType]:
        """Determine and execute ground attack based on input"""
        # Check for dash attack
        if player.state in [PlayerState.DASHING, PlayerState.RUNNING]:
            if player.start_attack(AttackType.DASH_ATTACK):
                self._start_attack(player, AttackType.DASH_ATTACK)
                return AttackType.DASH_ATTACK

        # Determine direction
        has_forward = (player.facing_right and player.input_right) or \
                     (not player.facing_right and player.input_left)
        has_up = player.input_up or player.input_jump
        has_down = player.input_down

        # Check for smash attacks (heavy + direction held)
        if player.input_heavy:
            if has_forward:
                player.smash_charging = True
                player.smash_charge_frames = 0
                player.smash_type = "fsmash"
                player.state = PlayerState.ATTACKING
                return None  # Charging, not attacking yet
            elif has_up:
                player.smash_charging = True
                player.smash_charge_frames = 0
                player.smash_type = "usmash"
                player.state = PlayerState.ATTACKING
                return None
            elif has_down:
                player.smash_charging = True
                player.smash_charge_frames = 0
                player.smash_type = "dsmash"
                player.state = PlayerState.ATTACKING
                return None

        # Tilt attacks (direction + attack)
        if has_forward:
            if player.start_attack(AttackType.FTILT):
                self._start_attack(player, AttackType.FTILT)
                return AttackType.FTILT
        elif has_up:
            if player.start_attack(AttackType.UTILT):
                self._start_attack(player, AttackType.UTILT)
                return AttackType.UTILT
        elif has_down:
            if player.start_attack(AttackType.DTILT):
                self._start_attack(player, AttackType.DTILT)
                return AttackType.DTILT
        else:
            # Neutral attack = jab combo
            return self._process_jab(player, current_time)

        return None

    def _process_jab(self, player: Player, current_time: float) -> Optional[AttackType]:
        """Process jab combo (up to 3 hits)"""
        # Check if within jab combo window
        if current_time < player.jab_window_end and player.jab_count < 3:
            # Continue combo
            if player.jab_count == 0:
                attack_type = AttackType.JAB
            elif player.jab_count == 1:
                attack_type = AttackType.JAB2
            else:
                attack_type = AttackType.JAB3
        else:
            # Start new jab
            attack_type = AttackType.JAB
            player.jab_count = 0

        if player.start_attack(attack_type):
            self._start_attack(player, attack_type)
            player.jab_count += 1
            # Set window for next jab
            attack_data = self.attack_data[attack_type]
            total_frames = attack_data.startup_frames + attack_data.active_frames + attack_data.recovery_frames
            player.jab_window_end = current_time + (total_frames / 60.0) + 0.15  # 0.15s window after attack ends
            return attack_type

        return None

    def _process_aerial_attack(self, player: Player) -> Optional[AttackType]:
        """Determine and execute aerial attack based on input"""
        # Determine direction relative to facing
        has_forward = (player.facing_right and player.input_right) or \
                     (not player.facing_right and player.input_left)
        has_back = (player.facing_right and player.input_left) or \
                  (not player.facing_right and player.input_right)
        has_up = player.input_up or player.input_jump
        has_down = player.input_down

        if has_forward:
            attack_type = AttackType.FAIR
        elif has_back:
            attack_type = AttackType.BAIR
        elif has_up:
            attack_type = AttackType.UAIR
        elif has_down:
            attack_type = AttackType.DAIR
        else:
            attack_type = AttackType.NAIR

        if player.start_attack(attack_type):
            self._start_attack(player, attack_type)
            return attack_type

        return None

    def _process_special_input(self, player: Player) -> Optional[AttackType]:
        """Process special move input (B button)"""
        # Determine direction
        has_forward = (player.facing_right and player.input_right) or \
                     (not player.facing_right and player.input_left)
        has_up = player.input_up or player.input_jump
        has_down = player.input_down

        if has_up:
            attack_type = AttackType.UP_B
        elif has_forward:
            attack_type = AttackType.SIDE_B
        elif has_down:
            attack_type = AttackType.DOWN_B
        else:
            attack_type = AttackType.NEUTRAL_B

        if player.start_attack(attack_type):
            self._start_attack(player, attack_type)
            character = get_character(player.character)
            if character:
                player.special_cooldown = time.time() + character.special_cooldown
            return attack_type

        return None

    def _process_grab(self, player: Player) -> Optional[AttackType]:
        """Process grab input"""
        if player.start_attack(AttackType.GRAB):
            self._start_attack(player, AttackType.GRAB)
            return AttackType.GRAB
        return None

    def _get_smash_type(self, smash_str: str) -> Optional[AttackType]:
        """Convert smash type string to AttackType"""
        mapping = {
            "fsmash": AttackType.FSMASH,
            "usmash": AttackType.USMASH,
            "dsmash": AttackType.DSMASH
        }
        return mapping.get(smash_str)

    def _start_attack(self, player: Player, attack_type: AttackType, charge_multiplier: float = 1.0):
        """Initialize attack tracking for a player"""
        attack_data = self.attack_data[attack_type]
        total_frames = (attack_data.startup_frames +
                        attack_data.active_frames +
                        attack_data.recovery_frames)

        self.active_attacks[player.id] = {
            'type': attack_type,
            'frame': 0,
            'total_frames': total_frames,
            'startup': attack_data.startup_frames,
            'active_start': attack_data.startup_frames,
            'active_end': attack_data.startup_frames + attack_data.active_frames,
            'data': attack_data,
            'charge_mult': charge_multiplier,  # For smash attacks
            'facing_right': player.facing_right  # Store facing for bair, etc.
        }
        self.hit_this_attack[player.id] = set()

    def update_attacks(self, players: List[Player]) -> List[HitResult]:
        """Update all active attacks and check for hits"""
        hits = []

        for player in players:
            if player.id not in self.active_attacks:
                continue

            attack_info = self.active_attacks[player.id]
            attack_info['frame'] += 1

            # Check if in active frames
            if attack_info['active_start'] <= attack_info['frame'] <= attack_info['active_end']:
                # Check for hits on other players
                for target in players:
                    if target.id == player.id:
                        continue
                    if target.id in self.hit_this_attack[player.id]:
                        continue  # Already hit this target
                    if target.state == PlayerState.DEAD:
                        continue

                    hit = self._check_hit(player, target, attack_info)
                    if hit:
                        hits.append(hit)
                        self.hit_this_attack[player.id].add(target.id)

            # Check if attack is complete
            if attack_info['frame'] >= attack_info['total_frames']:
                self._end_attack(player)

        return hits

    def _check_hit(self, attacker: Player, target: Player, attack_info: dict) -> Optional[HitResult]:
        """Check if an attack hits a target"""
        attack_data = attack_info['data']
        character = get_character(attacker.character)
        charge_mult = attack_info.get('charge_mult', 1.0)
        attacker_facing_right = attack_info.get('facing_right', attacker.facing_right)

        # Get attack range from character or default
        attack_range = attack_data.range
        if character:
            if attack_info['type'] == AttackType.LIGHT:
                attack_range = character.light_attack_range
            elif attack_info['type'] == AttackType.HEAVY:
                attack_range = character.heavy_attack_range
            elif attack_info['type'] == AttackType.SPECIAL:
                attack_range = character.special_range

        # Check if target is in range
        if not self.physics.is_in_range(attacker, target, attack_range):
            return None

        # Check for i-frames (dodge invincibility)
        if self.physics.is_invincible(target):
            return None

        # Check for parry (frame-perfect block)
        if self.physics.is_in_parry_window(target):
            self.physics.trigger_parry_success(target, attacker)
            return HitResult(
                attacker_id=attacker.id,
                target_id=target.id,
                damage_dealt=0,
                was_blocked=True,
                knockback_applied=(0, 0),
                combo_count=0
            )

        # Calculate damage with charge multiplier
        base_damage = attack_data.damage
        damage = int(base_damage * attacker.stats.attack * attacker.damage_boost * charge_mult)

        # Check blocking (legacy)
        was_blocked = target.state == PlayerState.BLOCKING
        if was_blocked:
            damage = int(damage * self.config.BLOCK_REDUCTION)

        # Apply damage and track attacker for kill credit
        actual_damage = target.take_damage(damage, 0, 0)  # Knockback applied separately
        target.last_hit_by = attacker.id  # Track for blast zone KO credit

        # Calculate SSB-style knockback from angle
        # Knockback = base_kb + (kb_scaling * target_damage% * damage_dealt * 0.05)
        target_damage_percent = (1 - (target.hp / target.stats.max_hp)) * 100
        knockback_power = (attack_data.base_knockback +
                          attack_data.knockback_scaling * target_damage_percent * 0.5)
        knockback_power *= charge_mult  # Charged smash = more knockback

        # Convert angle to velocity components
        # Angle 0 = right, 90 = up, 180 = left, 270 = down
        angle_rad = math.radians(attack_data.knockback_angle)

        # Flip horizontal knockback based on attacker facing
        if not attacker_facing_right:
            angle_rad = math.pi - angle_rad  # Mirror the angle

        knockback_x = knockback_power * math.cos(angle_rad)
        knockback_y = -knockback_power * math.sin(angle_rad)  # Negative because Y is inverted

        # Apply DI (Directional Influence) - target can slightly alter knockback angle
        if target.di_direction != (0, 0):
            di_influence = 0.15  # 15% angle shift max
            di_x, di_y = target.di_direction
            knockback_x += di_x * knockback_power * di_influence
            knockback_y += di_y * knockback_power * di_influence

        # Apply knockback
        self.physics.apply_knockback(target, knockback_x, knockback_y, attacker.x)

        # Update combo
        attacker.add_combo_hit()

        # Calculate hitstun (frames target can't act)
        # SSB formula: hitstun = knockback * 0.4
        hitstun_frames = knockback_power * 0.4
        hitstun_duration = hitstun_frames / 60.0  # Convert to seconds

        # Check for tumble (high knockback)
        if knockback_power > 8:
            target.state = PlayerState.TUMBLING
            target.stun(hitstun_duration)
        elif not was_blocked:
            target.stun(hitstun_duration)

        # Check for meteor smash (spike)
        if attack_data.can_meteor and attack_data.knockback_angle > 200:
            # Meteor smashes send downward
            pass  # Already handled by angle

        return HitResult(
            attacker_id=attacker.id,
            target_id=target.id,
            damage_dealt=actual_damage,
            was_blocked=was_blocked,
            knockback_applied=(knockback_x, knockback_y),
            combo_count=attacker.combo_count
        )

    def _end_attack(self, player: Player):
        """End a player's attack"""
        if player.id in self.active_attacks:
            attack_info = self.active_attacks[player.id]

            # Set cooldown based on attack type
            if attack_info['type'] == AttackType.LIGHT:
                player.attack_cooldown = time.time() + 0.15
            elif attack_info['type'] == AttackType.HEAVY:
                player.attack_cooldown = time.time() + 0.4

            del self.active_attacks[player.id]
            del self.hit_this_attack[player.id]

        if player.state == PlayerState.ATTACKING:
            player.state = PlayerState.IDLE
            player.current_attack = AttackType.NONE

    def execute_special(self, player: Player, arena, target_x: float = None,
                        target_y: float = None) -> Optional[dict]:
        """Execute a character's special ability"""
        character = get_character(player.character)
        if not character:
            return None

        ability = character.special_ability
        handler = ABILITY_HANDLERS.get(ability)
        if not handler:
            return None

        # Execute ability based on type
        if ability == SpecialAbility.FIRE_DASH:
            direction = 1 if player.facing_right else -1
            return handler(player, direction, arena)

        elif ability == SpecialAbility.SHIELD_BLOCK:
            return handler(player, 3.0)

        elif ability == SpecialAbility.TELEPORT:
            tx = target_x if target_x else player.x + (200 if player.facing_right else -200)
            ty = target_y if target_y else player.y
            return handler(player, tx, ty, arena)

        elif ability == SpecialAbility.LIGHTNING_STRIKE:
            return handler(player, arena)

        return None

    def process_special_effect(self, effect: dict, players: List[Player]) -> List[HitResult]:
        """Process the effects of a special ability on other players"""
        hits = []
        effect_type = effect.get('type')

        if effect_type == 'fire_dash':
            # Fire dash damages players in its path
            start_x = effect['start_x']
            end_x = effect['end_x']
            damage = effect['damage']

            for player in players:
                if player.id == effect['player_id']:
                    continue
                if player.state == PlayerState.DEAD:
                    continue

                # Check if player is in dash path
                player_x = player.x
                if min(start_x, end_x) <= player_x <= max(start_x, end_x):
                    actual_damage = player.take_damage(int(damage), 8, -4)
                    hits.append(HitResult(
                        attacker_id=effect['player_id'],
                        target_id=player.id,
                        damage_dealt=actual_damage,
                        was_blocked=False,
                        knockback_applied=(8, -4),
                        combo_count=1
                    ))

        elif effect_type == 'lightning_strike':
            # AoE damage around the caster
            center_x = effect['x']
            center_y = effect['y']
            radius = effect['radius']
            damage = effect['damage']

            for player in players:
                if player.id == effect['player_id']:
                    continue
                if player.state == PlayerState.DEAD:
                    continue

                # Check distance from center
                dx = player.x - center_x
                dy = player.y - center_y
                distance = (dx**2 + dy**2) ** 0.5

                if distance <= radius:
                    # Knockback away from center
                    kb_x = (dx / distance) * 10 if distance > 0 else 5
                    kb_y = -6
                    actual_damage = player.take_damage(int(damage), kb_x, kb_y)
                    hits.append(HitResult(
                        attacker_id=effect['player_id'],
                        target_id=player.id,
                        damage_dealt=actual_damage,
                        was_blocked=False,
                        knockback_applied=(kb_x, kb_y),
                        combo_count=1
                    ))

        return hits

    def cancel_attack(self, player: Player):
        """Cancel a player's current attack (used when stunned/hit)"""
        if player.id in self.active_attacks:
            del self.active_attacks[player.id]
            del self.hit_this_attack[player.id]
        player.state = PlayerState.IDLE
        player.current_attack = AttackType.NONE

    # ========== GRAB SYSTEM ==========

    def process_grab_hit(self, grabber: Player, targets: List[Player]) -> Optional[Player]:
        """Check if grab connects with any target"""
        if grabber.id not in self.active_attacks:
            return None

        attack_info = self.active_attacks[grabber.id]
        if attack_info['type'] != AttackType.GRAB:
            return None

        # Only check during active frames
        if not (attack_info['active_start'] <= attack_info['frame'] <= attack_info['active_end']):
            return None

        for target in targets:
            if target.id == grabber.id:
                continue
            if target.state == PlayerState.DEAD:
                continue
            if target.grabbed_by_id:  # Already grabbed
                continue

            # Check range
            if self.physics.is_in_range(grabber, target, self.attack_data[AttackType.GRAB].range):
                # Can't grab invincible players
                if self.physics.is_invincible(target):
                    continue

                # Grab successful!
                self._initiate_grab(grabber, target)
                return target

        return None

    def _initiate_grab(self, grabber: Player, target: Player):
        """Start a grab between two players"""
        grabber.grabbed_player_id = target.id
        target.grabbed_by_id = grabber.id

        # Position target in front of grabber
        offset = 40 if grabber.facing_right else -40
        target.x = grabber.x + offset
        target.y = grabber.y

        # Set grab release timer (can hold for ~90 frames, varies by target damage)
        base_hold = 90  # frames
        damage_bonus = int((1 - target.hp / target.stats.max_hp) * 60)  # More damaged = easier to hold
        grabber.grab_release_frame = base_hold + damage_bonus

        # Clear attack state
        if grabber.id in self.active_attacks:
            del self.active_attacks[grabber.id]
            del self.hit_this_attack[grabber.id]

        grabber.state = PlayerState.ATTACKING  # Use attacking state for grab hold
        target.state = PlayerState.STUNNED

        self.active_grabs[grabber.id] = target.id

    def update_grabs(self, players_dict: Dict[str, Player]) -> List[HitResult]:
        """Update all active grabs and process throws"""
        hits = []
        grabs_to_remove = []

        for grabber_id, target_id in list(self.active_grabs.items()):
            grabber = players_dict.get(grabber_id)
            target = players_dict.get(target_id)

            if not grabber or not target:
                grabs_to_remove.append(grabber_id)
                continue

            # Decrement grab timer
            grabber.grab_release_frame -= 1

            # Check for mash out (target can escape by mashing)
            # In a real implementation, this would check target's button presses
            # For now, use damage-based release

            # Check for throw input
            throw_type = self._get_throw_input(grabber)
            if throw_type:
                hit = self._execute_throw(grabber, target, throw_type)
                if hit:
                    hits.append(hit)
                grabs_to_remove.append(grabber_id)
                continue

            # Check for pummel input
            if grabber.input_attack and grabber.attack_cooldown <= time.time():
                hit = self._execute_pummel(grabber, target)
                if hit:
                    hits.append(hit)
                grabber.attack_cooldown = time.time() + 0.15  # Pummel cooldown

            # Auto-release if timer expires
            if grabber.grab_release_frame <= 0:
                self._release_grab(grabber, target)
                grabs_to_remove.append(grabber_id)

        # Clean up finished grabs
        for grabber_id in grabs_to_remove:
            if grabber_id in self.active_grabs:
                del self.active_grabs[grabber_id]

        return hits

    def _get_throw_input(self, grabber: Player) -> Optional[AttackType]:
        """Check for throw direction input"""
        # Forward throw
        if (grabber.facing_right and grabber.input_right) or \
           (not grabber.facing_right and grabber.input_left):
            if grabber.input_attack or grabber.input_special:
                return AttackType.FTHROW

        # Back throw
        if (grabber.facing_right and grabber.input_left) or \
           (not grabber.facing_right and grabber.input_right):
            if grabber.input_attack or grabber.input_special:
                return AttackType.BTHROW

        # Up throw
        if grabber.input_up or grabber.input_jump:
            if grabber.input_attack or grabber.input_special:
                return AttackType.UTHROW

        # Down throw
        if grabber.input_down:
            if grabber.input_attack or grabber.input_special:
                return AttackType.DTHROW

        return None

    def _execute_throw(self, grabber: Player, target: Player, throw_type: AttackType) -> HitResult:
        """Execute a throw attack"""
        attack_data = self.attack_data[throw_type]

        # Calculate damage
        damage = int(attack_data.damage * grabber.stats.attack)
        target.take_damage(damage, 0, 0)

        # Calculate knockback
        target_damage_percent = (1 - (target.hp / target.stats.max_hp)) * 100
        knockback_power = (attack_data.base_knockback +
                          attack_data.knockback_scaling * target_damage_percent * 0.5)

        angle_rad = math.radians(attack_data.knockback_angle)
        if not grabber.facing_right:
            angle_rad = math.pi - angle_rad

        knockback_x = knockback_power * math.cos(angle_rad)
        knockback_y = -knockback_power * math.sin(angle_rad)

        # Release grab
        self._release_grab(grabber, target)

        # Apply knockback
        target.vx = knockback_x
        target.vy = knockback_y
        target.on_ground = False

        # Stun target
        hitstun = knockback_power * 0.4 / 60.0
        target.stun(hitstun)

        return HitResult(
            attacker_id=grabber.id,
            target_id=target.id,
            damage_dealt=damage,
            was_blocked=False,
            knockback_applied=(knockback_x, knockback_y),
            combo_count=1
        )

    def _execute_pummel(self, grabber: Player, target: Player) -> HitResult:
        """Execute a pummel during grab"""
        attack_data = self.attack_data[AttackType.PUMMEL]
        damage = int(attack_data.damage * grabber.stats.attack)
        target.take_damage(damage, 0, 0)

        return HitResult(
            attacker_id=grabber.id,
            target_id=target.id,
            damage_dealt=damage,
            was_blocked=False,
            knockback_applied=(0, 0),
            combo_count=1
        )

    def _release_grab(self, grabber: Player, target: Player):
        """Release a grab without throwing"""
        grabber.grabbed_player_id = ""
        target.grabbed_by_id = ""
        grabber.state = PlayerState.IDLE
        target.state = PlayerState.IDLE
        grabber.grab_release_frame = 0

    def get_attack_state(self, player: Player) -> Optional[dict]:
        """Get the current attack state for a player (for network sync)"""
        if player.id not in self.active_attacks:
            return None

        attack_info = self.active_attacks[player.id]
        return {
            'type': attack_info['type'].value,
            'frame': attack_info['frame'],
            'total_frames': attack_info['total_frames'],
            'is_active': attack_info['active_start'] <= attack_info['frame'] <= attack_info['active_end']
        }
