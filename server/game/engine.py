"""
Arena Brawl - Main Game Engine
Handles the game loop, state management, and match logic
"""
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum

from server.config import Config
from server.entities.player import Player, PlayerState
from server.entities.character import get_character, get_character_names
from server.game.physics import PhysicsEngine, Platform, Obstacle as PhysicsObstacle, Rectangle
from server.game.combat import CombatSystem, HitResult
from server.game.events import EventManager
from server.maps.arenas import Arena, get_arena


class MatchState(Enum):
    WAITING = "waiting"      # Waiting for players
    COUNTDOWN = "countdown"  # Pre-match countdown
    PLAYING = "playing"      # Match in progress
    FINISHED = "finished"    # Match ended


@dataclass
class MatchResult:
    """Result of a completed match"""
    winner_id: Optional[str]
    winner_name: Optional[str]
    match_duration: float
    player_stats: Dict[str, dict]


class GameEngine:
    """Main game engine that runs the match"""

    def __init__(self, room_id: str, config: Config = None):
        self.room_id = room_id
        self.config = config or Config()

        # Subsystems
        self.physics = PhysicsEngine(self.config)
        self.combat = CombatSystem(self.config)
        self.events = EventManager(self.config)

        # Game state
        self.state = MatchState.WAITING
        self.arena: Optional[Arena] = None
        self.players: Dict[str, Player] = {}
        self.player_order: List[str] = []  # For consistent ordering

        # Timing
        self.match_start_time = 0.0
        self.match_end_time = 0.0
        self.countdown_start = 0.0
        self.countdown_duration = 3.0
        self.last_update = 0.0

        # Match stats
        self.player_stats: Dict[str, dict] = {}
        self.eliminated_players: List[str] = []

        # Callbacks for network events
        self.on_state_update: Optional[Callable] = None
        self.on_player_eliminated: Optional[Callable] = None
        self.on_match_end: Optional[Callable] = None
        self.on_event: Optional[Callable] = None

    def add_player(self, player_id: str, name: str, character: str = "Storm") -> Player:
        """Add a player to the match"""
        if len(self.players) >= self.config.MAX_PLAYERS_PER_ROOM:
            return None

        # Validate character
        if character not in get_character_names():
            character = "Storm"

        player = Player(id=player_id, name=name, character=character)

        # Apply character stats
        char_def = get_character(character)
        if char_def:
            player.set_character_stats(char_def.stats)

        self.players[player_id] = player
        self.player_order.append(player_id)

        # Initialize stats tracking
        self.player_stats[player_id] = {
            'kills': 0,
            'deaths': 0,
            'damage_dealt': 0,
            'damage_taken': 0,
            'powerups_collected': 0
        }

        return player

    def remove_player(self, player_id: str):
        """Remove a player from the match"""
        if player_id in self.players:
            del self.players[player_id]
            self.player_order.remove(player_id)

    def set_arena(self, arena_name: str):
        """Set the arena for the match"""
        self.arena = get_arena(arena_name)

    def start_countdown(self):
        """Start the pre-match countdown"""
        if self.state != MatchState.WAITING:
            return

        if not self.arena:
            self.arena = get_arena("street")

        self.state = MatchState.COUNTDOWN
        self.countdown_start = time.time()

        # Position players at spawn points
        self._spawn_players()

    def _spawn_players(self):
        """Spawn all players at their starting positions"""
        spawn_points = self.arena.spawn_points
        for i, player_id in enumerate(self.player_order):
            player = self.players[player_id]
            spawn_idx = i % len(spawn_points)
            spawn_x, spawn_y = spawn_points[spawn_idx]
            player.x = spawn_x
            player.y = spawn_y
            player.hp = player.stats.max_hp
            player.lives = self.config.LIVES_PER_PLAYER
            player.state = PlayerState.IDLE

    def start_match(self):
        """Start the actual match"""
        self.state = MatchState.PLAYING
        self.match_start_time = time.time()
        self.match_end_time = self.match_start_time + self.config.MATCH_TIME
        self.last_update = time.time()

        # Initialize events
        self.events.initialize(self.match_start_time)

    def update(self) -> dict:
        """Main game loop update - should be called at 60 FPS"""
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time

        if self.state == MatchState.COUNTDOWN:
            elapsed = current_time - self.countdown_start
            if elapsed >= self.countdown_duration:
                self.start_match()
            return self._get_state()

        if self.state != MatchState.PLAYING:
            return self._get_state()

        # Check match timer
        time_remaining = max(0, self.match_end_time - current_time)
        if time_remaining <= 0:
            self._end_match_timeout()
            return self._get_state()

        # Update physics obstacles from arena
        physics_obstacles = self._get_physics_obstacles()
        platforms = self._get_platforms()

        # Process each player
        hits = []
        for player in self.players.values():
            if player.state == PlayerState.DEAD:
                continue

            # Process attack input
            self.combat.process_attack_input(player)

            # Update physics
            self.physics.update_player(player, platforms, physics_obstacles, dt)

        # Update combat and get hits
        combat_hits = self.combat.update_attacks(list(self.players.values()))
        hits.extend(combat_hits)

        # Process hits
        for hit in hits:
            self._process_hit(hit)

        # Update events (cop, powerups, etc.)
        event_results = self.events.update(current_time)
        for event_data in event_results:
            if self.on_event:
                self.on_event(event_data)

        # Check cop damage
        if self.events.cop_active:
            for player in self.players.values():
                if player.state != PlayerState.DEAD:
                    cop_result = self.events.check_cop_damage(player, self.arena.obstacles)
                    if cop_result and self.on_event:
                        self.on_event(cop_result)

        # Check item collection
        self._check_item_collection()

        # Check for eliminations
        self._check_eliminations()

        # Check win condition
        self._check_win_condition()

        return self._get_state()

    def _get_physics_obstacles(self) -> List[PhysicsObstacle]:
        """Convert arena obstacles to physics obstacles"""
        obstacles = []
        for obs in self.arena.obstacles:
            if obs.is_destroyed:
                continue
            obstacles.append(PhysicsObstacle(
                rect=Rectangle(obs.x, obs.y, obs.width, obs.height),
                is_destructible=obs.is_destructible,
                hp=obs.hp,
                provides_cover=obs.provides_cover
            ))
        return obstacles

    def _get_platforms(self) -> List[Platform]:
        """Get platforms from arena obstacles"""
        platforms = []
        for obs in self.arena.obstacles:
            if obs.is_destroyed:
                continue
            if obs.obstacle_type == 'platform':
                platforms.append(Platform(
                    rect=Rectangle(obs.x, obs.y, obs.width, obs.height),
                    is_passthrough=True
                ))
        return platforms

    def _process_hit(self, hit: HitResult):
        """Process a combat hit"""
        # Update stats
        if hit.attacker_id in self.player_stats:
            self.player_stats[hit.attacker_id]['damage_dealt'] += hit.damage_dealt
        if hit.target_id in self.player_stats:
            self.player_stats[hit.target_id]['damage_taken'] += hit.damage_dealt

    def _check_item_collection(self):
        """Check if players are collecting powerups/healthboxes"""
        for player in self.players.values():
            if player.state == PlayerState.DEAD:
                continue

            player_rect = self.physics.get_player_hitbox(player)

            # Check powerups
            for powerup in self.events.active_powerups[:]:
                if not powerup.is_active:
                    continue
                item_rect = Rectangle(powerup.x - 20, powerup.y - 20, 40, 40)
                if player_rect.intersects(item_rect):
                    result = self.events.collect_powerup(powerup.id, player)
                    if result:
                        self.player_stats[player.id]['powerups_collected'] += 1
                        if self.on_event:
                            self.on_event(result)

            # Check healthboxes
            for healthbox in self.events.active_healthboxes[:]:
                if not healthbox.is_active:
                    continue
                item_rect = Rectangle(healthbox.x - 20, healthbox.y - 20, 40, 40)
                if player_rect.intersects(item_rect):
                    result = self.events.collect_healthbox(healthbox.id, player)
                    if result:
                        self.player_stats[player.id]['powerups_collected'] += 1
                        if self.on_event:
                            self.on_event(result)

    def _check_eliminations(self):
        """Check for player eliminations and respawns"""
        for player in self.players.values():
            if player.state == PlayerState.DEAD and player.id not in self.eliminated_players:
                if player.lives <= 0:
                    # Permanently eliminated
                    self.eliminated_players.append(player.id)
                    self.player_stats[player.id]['deaths'] += 1
                    if self.on_player_eliminated:
                        self.on_player_eliminated(player.id, player.name)
                else:
                    # Respawn after delay
                    spawn_idx = self.player_order.index(player.id) % len(self.arena.spawn_points)
                    spawn_x, spawn_y = self.arena.spawn_points[spawn_idx]
                    player.respawn(spawn_x, spawn_y, self.config.RESPAWN_INVINCIBILITY)

    def _check_win_condition(self):
        """Check if match should end"""
        alive_players = [p for p in self.players.values()
                         if p.state != PlayerState.DEAD or p.lives > 0]

        if len(alive_players) <= 1 and len(self.players) > 1:
            winner = alive_players[0] if alive_players else None
            self._end_match(winner)

    def _end_match_timeout(self):
        """End match due to timeout - winner is player with most lives/hp"""
        alive_players = [p for p in self.players.values() if p.state != PlayerState.DEAD]

        if not alive_players:
            self._end_match(None)
            return

        # Sort by lives, then HP
        alive_players.sort(key=lambda p: (p.lives, p.hp), reverse=True)
        self._end_match(alive_players[0])

    def _end_match(self, winner: Optional[Player]):
        """End the match"""
        self.state = MatchState.FINISHED

        result = MatchResult(
            winner_id=winner.id if winner else None,
            winner_name=winner.name if winner else None,
            match_duration=time.time() - self.match_start_time,
            player_stats=self.player_stats
        )

        if self.on_match_end:
            self.on_match_end(result)

    def process_input(self, player_id: str, input_data: dict):
        """Process input from a player"""
        if player_id not in self.players:
            return

        player = self.players[player_id]
        if player.state == PlayerState.DEAD:
            return

        # Update input state
        move = input_data.get('move', 'none')
        player.input_left = move == 'left'
        player.input_right = move == 'right'
        player.input_jump = move == 'jump' or input_data.get('jump', False)

        action = input_data.get('action', 'none')
        player.input_attack = action == 'attack'
        player.input_heavy = action == 'heavy'
        player.input_special = action == 'special'
        player.input_block = action == 'block'

        # Hiding state (for cop mechanic)
        player.is_hiding = input_data.get('hide', False)

    def _get_state(self) -> dict:
        """Get current game state for network sync"""
        current_time = time.time()

        # Calculate countdown or time remaining
        countdown = 0
        time_remaining = 0
        if self.state == MatchState.COUNTDOWN:
            countdown = max(0, self.countdown_duration - (current_time - self.countdown_start))
        elif self.state == MatchState.PLAYING:
            time_remaining = max(0, self.match_end_time - current_time)

        return {
            'room_id': self.room_id,
            'state': self.state.value,
            'countdown': round(countdown, 1),
            'time_remaining': round(time_remaining, 1),
            'arena': self.arena.to_dict() if self.arena else None,
            'players': [self.players[pid].to_dict() for pid in self.player_order
                        if pid in self.players],
            'events': self.events.get_state(),
            'eliminated': self.eliminated_players
        }

    def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID"""
        return self.players.get(player_id)
