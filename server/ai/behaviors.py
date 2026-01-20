"""
Arena Brawl - AI Behaviors
Attack, defend, and evade logic for AI bots
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Tuple
import random
import math

from server.entities.player import Player, PlayerState


class BehaviorState(Enum):
    IDLE = "idle"
    APPROACH = "approach"
    ATTACK = "attack"
    RETREAT = "retreat"
    EVADE = "evade"
    COLLECT = "collect"    # Going for powerup/health


@dataclass
class BehaviorDecision:
    """Output of behavior decision"""
    move: str = "none"      # left, right, jump, none
    action: str = "none"    # attack, heavy, special, block, none
    jump: bool = False
    hide: bool = False
    target_x: Optional[float] = None
    target_y: Optional[float] = None


class BehaviorTree:
    """Decision-making system for AI bots"""

    def __init__(self, difficulty: str = "medium"):
        self.difficulty = difficulty
        self.current_state = BehaviorState.IDLE
        self.state_timer = 0.0
        self.target_player: Optional[str] = None

        # Difficulty settings
        self.settings = self._get_difficulty_settings(difficulty)

        # Combat memory
        self.last_attack_time = 0.0
        self.combo_attempts = 0

    def _get_difficulty_settings(self, difficulty: str) -> dict:
        """Get AI settings based on difficulty"""
        settings = {
            'easy': {
                'reaction_time': 0.5,
                'accuracy': 0.6,
                'aggression': 0.3,
                'dodge_chance': 0.2,
                'combo_skill': 0.3,
                'special_use': 0.1
            },
            'medium': {
                'reaction_time': 0.3,
                'accuracy': 0.75,
                'aggression': 0.5,
                'dodge_chance': 0.4,
                'combo_skill': 0.5,
                'special_use': 0.3
            },
            'hard': {
                'reaction_time': 0.1,
                'accuracy': 0.9,
                'aggression': 0.7,
                'dodge_chance': 0.7,
                'combo_skill': 0.8,
                'special_use': 0.5
            }
        }
        return settings.get(difficulty, settings['medium'])

    def decide(self, bot: Player, enemies: List[Player], game_state: dict) -> BehaviorDecision:
        """Main decision-making function"""
        decision = BehaviorDecision()

        # Find nearest enemy
        nearest_enemy = self._find_nearest_enemy(bot, enemies)
        if not nearest_enemy:
            return self._wander_behavior(bot, decision)

        # Check for nearby collectibles
        collectible = self._find_nearby_collectible(bot, game_state)
        if collectible and self._should_collect(bot, collectible, nearest_enemy):
            return self._collect_behavior(bot, collectible, decision)

        # Determine behavior based on situation
        distance = self._get_distance(bot, nearest_enemy)
        health_ratio = bot.hp / bot.stats.max_hp

        # Low health - more defensive
        if health_ratio < 0.3:
            if random.random() < 0.6:
                return self._retreat_behavior(bot, nearest_enemy, decision)

        # In attack range
        if distance < 80:
            return self._combat_behavior(bot, nearest_enemy, distance, decision)

        # Approach enemy
        return self._approach_behavior(bot, nearest_enemy, decision)

    def _find_nearest_enemy(self, bot: Player, enemies: List[Player]) -> Optional[Player]:
        """Find the nearest alive enemy"""
        alive_enemies = [e for e in enemies
                        if e.id != bot.id and e.state != PlayerState.DEAD]

        if not alive_enemies:
            return None

        return min(alive_enemies, key=lambda e: self._get_distance(bot, e))

    def _get_distance(self, player1: Player, player2: Player) -> float:
        """Get distance between two players"""
        dx = player1.x - player2.x
        dy = player1.y - player2.y
        return math.sqrt(dx**2 + dy**2)

    def _find_nearby_collectible(self, bot: Player, game_state: dict) -> Optional[dict]:
        """Find nearby powerup or healthbox"""
        events = game_state.get('events', {})
        powerups = events.get('powerups', [])
        healthboxes = events.get('healthboxes', [])

        all_items = powerups + healthboxes
        if not all_items:
            return None

        # Find closest item
        closest = None
        closest_dist = float('inf')

        for item in all_items:
            dist = math.sqrt((bot.x - item['x'])**2 + (bot.y - item['y'])**2)
            if dist < closest_dist:
                closest_dist = dist
                closest = item

        return closest if closest_dist < 300 else None

    def _should_collect(self, bot: Player, collectible: dict,
                        nearest_enemy: Player) -> bool:
        """Decide if bot should go for collectible"""
        item_dist = math.sqrt((bot.x - collectible['x'])**2 +
                              (bot.y - collectible['y'])**2)
        enemy_dist = self._get_distance(bot, nearest_enemy)

        # Go for health if low HP
        if 'tier' in collectible and bot.hp / bot.stats.max_hp < 0.5:
            return True

        # Go for item if closer than enemy
        if item_dist < enemy_dist * 0.7:
            return True

        return random.random() < 0.3

    def _wander_behavior(self, bot: Player, decision: BehaviorDecision) -> BehaviorDecision:
        """Wander when no enemies"""
        self.current_state = BehaviorState.IDLE

        if random.random() < 0.02:
            decision.move = random.choice(['left', 'right', 'none'])

        if random.random() < 0.01 and bot.on_ground:
            decision.jump = True

        return decision

    def _collect_behavior(self, bot: Player, collectible: dict,
                          decision: BehaviorDecision) -> BehaviorDecision:
        """Move toward collectible"""
        self.current_state = BehaviorState.COLLECT

        dx = collectible['x'] - bot.x
        dy = collectible['y'] - bot.y

        if abs(dx) > 20:
            decision.move = 'right' if dx > 0 else 'left'

        if dy < -50 and bot.on_ground:
            decision.jump = True

        return decision

    def _approach_behavior(self, bot: Player, enemy: Player,
                           decision: BehaviorDecision) -> BehaviorDecision:
        """Approach the enemy"""
        self.current_state = BehaviorState.APPROACH

        dx = enemy.x - bot.x
        dy = enemy.y - bot.y

        # Move toward enemy
        if abs(dx) > 50:
            decision.move = 'right' if dx > 0 else 'left'

        # Jump if enemy is above
        if dy < -50 and bot.on_ground:
            decision.jump = True

        # Jump randomly while approaching
        if random.random() < 0.05 and bot.on_ground:
            decision.jump = True

        return decision

    def _combat_behavior(self, bot: Player, enemy: Player, distance: float,
                         decision: BehaviorDecision) -> BehaviorDecision:
        """Combat behavior when in attack range"""
        self.current_state = BehaviorState.ATTACK

        # Face the enemy
        if enemy.x > bot.x:
            bot.facing_right = True
        else:
            bot.facing_right = False

        # Check if enemy is attacking - maybe block or dodge
        if enemy.state == PlayerState.ATTACKING:
            if random.random() < self.settings['dodge_chance']:
                decision.action = 'block'
                return decision
            elif random.random() < self.settings['dodge_chance'] * 0.5:
                decision.move = 'left' if bot.facing_right else 'right'
                decision.jump = True
                return decision

        # Decide attack type based on combo skill
        attack_roll = random.random()

        if attack_roll < self.settings['special_use']:
            decision.action = 'special'
        elif attack_roll < self.settings['combo_skill']:
            # Try combo
            if self.combo_attempts < 2:
                decision.action = 'attack'
                self.combo_attempts += 1
            else:
                decision.action = 'heavy'
                self.combo_attempts = 0
        else:
            decision.action = random.choice(['attack', 'attack', 'heavy'])
            self.combo_attempts = 0

        return decision

    def _retreat_behavior(self, bot: Player, enemy: Player,
                          decision: BehaviorDecision) -> BehaviorDecision:
        """Retreat when low health"""
        self.current_state = BehaviorState.RETREAT

        dx = enemy.x - bot.x

        # Move away from enemy
        decision.move = 'left' if dx > 0 else 'right'

        # Jump to escape
        if random.random() < 0.1 and bot.on_ground:
            decision.jump = True

        # Block if enemy gets close
        if abs(dx) < 100:
            if random.random() < 0.4:
                decision.action = 'block'

        return decision
