"""
Arena Brawl - Combat System
Handles attacks, damage, combos, and special abilities
"""
import time
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
    range: float
    startup_frames: int  # Frames before attack is active
    active_frames: int   # Frames attack hitbox is active
    recovery_frames: int  # Frames after attack before can act


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

        # Attack frame data (at 60 FPS)
        self.attack_data = {
            AttackType.LIGHT: AttackData(
                attacker_id="",
                attack_type=AttackType.LIGHT,
                damage=self.config.LIGHT_ATTACK_DAMAGE,
                knockback_x=3,
                knockback_y=-2,
                range=60,
                startup_frames=3,
                active_frames=4,
                recovery_frames=8
            ),
            AttackType.HEAVY: AttackData(
                attacker_id="",
                attack_type=AttackType.HEAVY,
                damage=self.config.HEAVY_ATTACK_DAMAGE,
                knockback_x=8,
                knockback_y=-5,
                range=80,
                startup_frames=10,
                active_frames=6,
                recovery_frames=20
            ),
            AttackType.SPECIAL: AttackData(
                attacker_id="",
                attack_type=AttackType.SPECIAL,
                damage=25,  # Base special damage
                knockback_x=10,
                knockback_y=-6,
                range=100,
                startup_frames=8,
                active_frames=8,
                recovery_frames=25
            )
        }

        # Track attack states
        self.active_attacks: Dict[str, dict] = {}  # player_id -> attack info
        self.hit_this_attack: Dict[str, set] = {}  # player_id -> set of hit targets

    def process_attack_input(self, player: Player) -> Optional[AttackType]:
        """Process player attack input and start attack if valid"""
        if player.state in [PlayerState.STUNNED, PlayerState.DEAD, PlayerState.ATTACKING]:
            return None

        current_time = time.time()

        # Check special attack
        if player.input_special and current_time >= player.special_cooldown:
            if player.start_attack(AttackType.SPECIAL):
                self._start_attack(player, AttackType.SPECIAL)
                character = get_character(player.character)
                if character:
                    player.special_cooldown = current_time + character.special_cooldown
                return AttackType.SPECIAL

        # Check heavy attack
        if player.input_heavy and current_time >= player.attack_cooldown:
            if player.start_attack(AttackType.HEAVY):
                self._start_attack(player, AttackType.HEAVY)
                return AttackType.HEAVY

        # Check light attack
        if player.input_attack and current_time >= player.attack_cooldown:
            if player.start_attack(AttackType.LIGHT):
                self._start_attack(player, AttackType.LIGHT)
                return AttackType.LIGHT

        return None

    def _start_attack(self, player: Player, attack_type: AttackType):
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
            'data': attack_data
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

        # Calculate damage
        base_damage = attack_data.damage
        damage = int(base_damage * attacker.stats.attack * attacker.damage_boost)

        # Check blocking
        was_blocked = target.state == PlayerState.BLOCKING
        if was_blocked:
            damage = int(damage * self.config.BLOCK_REDUCTION)

        # Apply damage and knockback
        knockback_x = attack_data.knockback_x * self.config.KNOCKBACK_BASE
        knockback_y = attack_data.knockback_y

        actual_damage = target.take_damage(damage, knockback_x, knockback_y)
        self.physics.apply_knockback(target, knockback_x, knockback_y, attacker.x)

        # Update combo
        attacker.add_combo_hit()

        # Stun target briefly
        if not was_blocked:
            stun_duration = 0.2 if attack_info['type'] == AttackType.LIGHT else 0.4
            target.stun(stun_duration)

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
