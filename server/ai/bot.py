"""
Arena Brawl - AI Bot Controller
Manages AI-controlled players
"""
import uuid
import random
from typing import List, Dict, Optional

from server.entities.player import Player, PlayerState
from server.entities.character import get_character_names
from server.ai.behaviors import BehaviorTree, BehaviorDecision
from server.config import Config


# Bot names for variety
BOT_NAMES = [
    "Sparky", "Thunder", "Blitz", "Crusher", "Shade",
    "Phoenix", "Viper", "Frost", "Blaze_Bot", "Storm_AI",
    "Ironclad", "Shadow_X", "Titan", "Rogue", "Flash"
]


class AIBot:
    """AI controller for a single bot player"""

    def __init__(self, player: Player, difficulty: str = "medium", config: Config = None):
        self.player = player
        self.difficulty = difficulty
        self.config = config or Config()

        # Behavior system
        self.behavior = BehaviorTree(difficulty)

        # Timing
        self.reaction_timer = 0.0
        self.reaction_delay = self.config.AI_REACTION_TIME.get(difficulty, 0.3)
        self.last_decision_time = 0.0
        self.decision_interval = self.reaction_delay

        # Current decision
        self.current_decision: Optional[BehaviorDecision] = None
        self.pending_decision: Optional[BehaviorDecision] = None

    def update(self, enemies: List[Player], game_state: dict, current_time: float):
        """Update AI each frame"""
        if self.player.state == PlayerState.DEAD:
            self._clear_inputs()
            return

        # Check if it's time for a new decision
        if current_time - self.last_decision_time >= self.decision_interval:
            # Make decision
            self.pending_decision = self.behavior.decide(
                self.player, enemies, game_state
            )
            self.last_decision_time = current_time

            # Apply decision after reaction delay
            self.reaction_timer = self.reaction_delay

        # Apply pending decision after reaction time
        if self.pending_decision and self.reaction_timer <= 0:
            self.current_decision = self.pending_decision
            self.pending_decision = None
            self._apply_decision(self.current_decision)

        # Count down reaction timer
        if self.reaction_timer > 0:
            self.reaction_timer -= 1/60  # Assuming 60 FPS

    def _apply_decision(self, decision: BehaviorDecision):
        """Apply AI decision to player inputs"""
        # Movement
        self.player.input_left = decision.move == 'left'
        self.player.input_right = decision.move == 'right'
        self.player.input_jump = decision.jump or decision.move == 'jump'

        # Actions
        self.player.input_attack = decision.action == 'attack'
        self.player.input_heavy = decision.action == 'heavy'
        self.player.input_special = decision.action == 'special'
        self.player.input_block = decision.action == 'block'

        # Hiding
        self.player.is_hiding = decision.hide

    def _clear_inputs(self):
        """Clear all inputs"""
        self.player.input_left = False
        self.player.input_right = False
        self.player.input_jump = False
        self.player.input_attack = False
        self.player.input_heavy = False
        self.player.input_special = False
        self.player.input_block = False
        self.player.is_hiding = False


class BotManager:
    """Manages multiple AI bots in a game"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.bots: Dict[str, AIBot] = {}
        self.used_names: set = set()

    def create_bot(self, difficulty: str = "medium", character: str = None) -> Player:
        """Create a new bot player"""
        # Generate unique ID and name
        bot_id = f"bot_{uuid.uuid4().hex[:8]}"
        bot_name = self._get_unique_name()

        # Random character if not specified
        if not character:
            character = random.choice(get_character_names())

        # Create player
        from server.entities.character import get_character
        player = Player(
            id=bot_id,
            name=bot_name,
            character=character,
            is_bot=True
        )

        # Apply character stats
        char_def = get_character(character)
        if char_def:
            player.set_character_stats(char_def.stats)

        # Create AI controller
        bot = AIBot(player, difficulty, self.config)
        self.bots[bot_id] = bot

        return player

    def _get_unique_name(self) -> str:
        """Get a unique bot name"""
        available = [n for n in BOT_NAMES if n not in self.used_names]
        if not available:
            # All names used, add suffix
            name = random.choice(BOT_NAMES) + str(len(self.used_names))
        else:
            name = random.choice(available)

        self.used_names.add(name)
        return name

    def remove_bot(self, bot_id: str):
        """Remove a bot"""
        if bot_id in self.bots:
            del self.bots[bot_id]

    def update_all(self, players: Dict[str, Player], game_state: dict, current_time: float):
        """Update all bots"""
        player_list = list(players.values())

        for bot_id, bot in self.bots.items():
            # Get enemies (all other players)
            enemies = [p for p in player_list if p.id != bot_id]
            bot.update(enemies, game_state, current_time)

    def get_bot(self, bot_id: str) -> Optional[AIBot]:
        """Get a bot by ID"""
        return self.bots.get(bot_id)

    def get_all_bots(self) -> List[AIBot]:
        """Get all bots"""
        return list(self.bots.values())

    def get_all_bot_players(self) -> List[Player]:
        """Get all bot players"""
        return [bot.player for bot in self.bots.values()]

    def clear(self):
        """Remove all bots"""
        self.bots.clear()
        self.used_names.clear()


def fill_with_bots(game_engine, target_count: int = 4,
                   difficulty: str = "medium") -> List[Player]:
    """Fill empty slots in a game with bots"""
    bot_manager = BotManager(game_engine.config)
    added_bots = []

    current_count = len(game_engine.players)
    bots_needed = target_count - current_count

    for _ in range(bots_needed):
        bot_player = bot_manager.create_bot(difficulty)
        game_engine.add_player(bot_player.id, bot_player.name, bot_player.character)

        # Copy the bot player data to the game engine's player
        game_player = game_engine.get_player(bot_player.id)
        if game_player:
            game_player.is_bot = True
            added_bots.append(game_player)

    return added_bots
