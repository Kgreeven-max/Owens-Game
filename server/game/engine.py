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
from server.game.modes import ModeManager, ModeSettings, GameMode, TeamColor, get_preset_mode
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
        self.mode_manager = ModeManager()

        # Mode settings
        self.game_mode: GameMode = GameMode.STOCK
        self.team_assignments: Dict[str, TeamColor] = {}

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

    def set_mode(self, mode_name: str):
        """Set the game mode using a preset name"""
        settings = get_preset_mode(mode_name)
        self.mode_manager = ModeManager(settings)
        self.game_mode = settings.mode

    def set_mode_settings(self, settings: ModeSettings):
        """Set the game mode using custom settings"""
        self.mode_manager = ModeManager(settings)
        self.game_mode = settings.mode

    def set_team(self, player_id: str, team: TeamColor):
        """Assign a player to a team"""
        self.team_assignments[player_id] = team

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

            # Set HP based on mode
            if self.game_mode == GameMode.STAMINA:
                player.hp = self.mode_manager.settings.stamina_hp
            else:
                player.hp = player.stats.max_hp

            # Set lives from mode settings
            player.lives = self.mode_manager.settings.stock_count
            player.state = PlayerState.IDLE

    def start_match(self):
        """Start the actual match"""
        self.state = MatchState.PLAYING
        self.match_start_time = time.time()

        # Use mode manager's time limit if set
        time_limit = self.mode_manager.settings.time_limit if self.mode_manager.settings.time_limit > 0 else self.config.MATCH_TIME
        self.match_end_time = self.match_start_time + time_limit
        self.last_update = time.time()

        # Initialize mode manager with players
        self.mode_manager.initialize(
            player_ids=list(self.players.keys()),
            team_assignments=self.team_assignments if self.game_mode == GameMode.TEAMS else None
        )

        # Initialize events (respect mode settings)
        if self.mode_manager.settings.items_enabled:
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

        # Update moving platforms
        if hasattr(self.arena, 'update'):
            self.arena.update(current_time)

        # Update physics obstacles from arena
        physics_obstacles = self._get_physics_obstacles()
        platforms = self._get_platforms()

        # Process each player
        hits = []
        for player in self.players.values():
            if player.state == PlayerState.DEAD:
                continue

            # Process dodge/parry input
            self.physics.process_dodge_input(player)

            # Update dodge state
            self.physics.update_dodge_state(player)

            # Process attack input
            self.combat.process_attack_input(player)

            # Update physics
            self.physics.update_player(player, platforms, physics_obstacles, dt)

            # Check for ledge grab
            self.physics.check_ledge_grab(player, platforms)

            # Process ledge options
            self.physics.process_ledge_options(player)

        # Update combat and get hits
        combat_hits = self.combat.update_attacks(list(self.players.values()))
        hits.extend(combat_hits)

        # Check for grab connections
        for player in self.players.values():
            if player.state == PlayerState.ATTACKING:
                grabbed = self.combat.process_grab_hit(player, list(self.players.values()))

        # Update active grabs and throws
        grab_hits = self.combat.update_grabs(self.players)
        hits.extend(grab_hits)

        # Process hits
        for hit in hits:
            self._process_hit(hit)

        # Update events (cop, powerups, etc.)
        event_results = self.events.update(current_time)
        for event_data in event_results:
            if self.on_event:
                self.on_event(event_data)

        # Check item collection
        self._check_item_collection()

        # Check blast zones (SSB-style KO boundaries)
        self._check_blast_zones()

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
        # Check if team attack is allowed
        if not self.mode_manager.is_team_attack_allowed(hit.attacker_id, hit.target_id):
            return  # Block friendly fire

        # Update stats
        if hit.attacker_id in self.player_stats:
            self.player_stats[hit.attacker_id]['damage_dealt'] += hit.damage_dealt
        if hit.target_id in self.player_stats:
            self.player_stats[hit.target_id]['damage_taken'] += hit.damage_dealt

        # Process hit in mode manager (handles stamina mode KOs)
        mode_result = self.mode_manager.process_hit(
            hit.attacker_id, hit.target_id, hit.damage_dealt
        )

        # Handle stamina mode KO
        if mode_result.get('ko') and mode_result.get('ko_type') == 'stamina':
            target = self.players.get(hit.target_id)
            if target:
                target.state = PlayerState.DEAD
                if self.on_event:
                    self.on_event({
                        'type': 'stamina_ko',
                        'player_id': hit.target_id,
                        'attacker_id': hit.attacker_id
                    })

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

    def _check_blast_zones(self):
        """Check if any players have crossed blast zone boundaries (SSB-style KO)"""
        if not self.arena or not hasattr(self.arena, 'blast_zones'):
            return

        blast_zones = self.arena.blast_zones

        for player in self.players.values():
            if player.state == PlayerState.DEAD:
                continue

            # Check if player is outside blast zones
            ko_direction = blast_zones.is_player_out(player.x, player.y)

            if ko_direction:
                # Process KO through mode manager
                ko_result = self.mode_manager.process_blast_zone_ko(
                    player.id, player.last_hit_by
                )

                # Update player state
                player.state = PlayerState.DEAD

                # Stock mode: Decrement lives from mode manager
                if self.game_mode == GameMode.STOCK:
                    player.lives = self.mode_manager.player_states[player.id].stocks

                # Record kill credit
                if player.last_hit_by and player.last_hit_by in self.player_stats:
                    self.player_stats[player.last_hit_by]['kills'] += 1

                # Self-destruct penalty in time mode
                if ko_result.get('is_sd') and player.id in self.player_stats:
                    self.player_stats[player.id]['deaths'] += 1

                # Send KO event
                if self.on_event:
                    self.on_event({
                        'type': 'blast_zone_ko',
                        'player_id': player.id,
                        'player_name': player.name,
                        'direction': ko_direction,
                        'x': player.x,
                        'y': player.y,
                        'last_hit_by': player.last_hit_by,
                        'lives_remaining': player.lives,
                        'is_sd': ko_result.get('is_sd', False),
                        'score': self.mode_manager.player_states.get(player.id, {})
                    })

    def _check_eliminations(self):
        """Check for player eliminations and respawns"""
        for player in self.players.values():
            if player.state == PlayerState.DEAD and player.id not in self.eliminated_players:
                # Check with mode manager if respawn is allowed
                respawn_result = self.mode_manager.respawn_player(player.id)

                if not respawn_result['can_respawn']:
                    # Permanently eliminated
                    self.eliminated_players.append(player.id)
                    if player.id in self.player_stats:
                        self.player_stats[player.id]['deaths'] += 1
                    if self.on_player_eliminated:
                        self.on_player_eliminated(player.id, player.name)
                else:
                    # Respawn after delay
                    spawn_idx = self.player_order.index(player.id) % len(self.arena.spawn_points)
                    spawn_x, spawn_y = self.arena.spawn_points[spawn_idx]

                    # Set HP based on mode
                    if self.game_mode == GameMode.STAMINA:
                        player.hp = respawn_result.get('hp', self.mode_manager.settings.stamina_hp)
                    else:
                        player.hp = player.stats.max_hp

                    player.respawn(spawn_x, spawn_y, self.config.RESPAWN_INVINCIBILITY)

    def _check_win_condition(self):
        """Check if match should end"""
        # Use mode manager's win condition check
        win_result = self.mode_manager.check_win_condition()

        if win_result['match_over']:
            if win_result.get('winner_team'):
                # Team win - find a player from winning team
                team_color = win_result['winner_team']
                team = self.mode_manager.teams.get(team_color)
                if team and team.player_ids:
                    winner = self.players.get(team.player_ids[0])
                else:
                    winner = None
            else:
                # Individual win
                winner_id = win_result.get('winner_id')
                winner = self.players.get(winner_id) if winner_id else None

            self._end_match(winner, win_result)

    def _end_match_timeout(self):
        """End match due to timeout - use mode manager to determine winner"""
        # Mode manager handles timeout logic
        win_result = {
            'match_over': True,
            'reason': 'time_up'
        }

        # Get winner based on mode
        if self.game_mode == GameMode.TIME:
            # Highest score wins
            scoreboard = self.mode_manager.get_scoreboard()
            if scoreboard:
                winner = self.players.get(scoreboard[0]['player_id'])
            else:
                winner = None
        else:
            # Most lives/HP wins
            alive_players = [p for p in self.players.values() if p.state != PlayerState.DEAD]
            if alive_players:
                alive_players.sort(key=lambda p: (p.lives, p.hp), reverse=True)
                winner = alive_players[0]
            else:
                winner = None

        self._end_match(winner, win_result)

    def _end_match(self, winner: Optional[Player], win_result: dict = None):
        """End the match"""
        self.state = MatchState.FINISHED

        result = MatchResult(
            winner_id=winner.id if winner else None,
            winner_name=winner.name if winner else None,
            match_duration=time.time() - self.match_start_time,
            player_stats=self.player_stats
        )

        # Add mode-specific info to result
        if win_result:
            result.player_stats['_mode_result'] = {
                'reason': win_result.get('reason'),
                'winner_team': win_result.get('winner_team').value if win_result.get('winner_team') else None,
                'scoreboard': self.mode_manager.get_scoreboard()
            }

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
        player.input_up = input_data.get('up', False)
        player.input_down = input_data.get('down', False)

        action = input_data.get('action', 'none')
        player.input_attack = action == 'attack'
        player.input_heavy = input_data.get('heavy', False)  # Smash modifier
        player.input_special = action == 'special'
        player.input_block = action == 'block'
        player.input_dodge = action == 'dodge' or input_data.get('dodge', False)
        player.input_grab = action == 'grab' or input_data.get('grab', False)

        # Update DI direction during hitstun
        if player.state in [PlayerState.STUNNED, PlayerState.TUMBLING]:
            di_x = 1 if player.input_right else (-1 if player.input_left else 0)
            di_y = -1 if player.input_up else (1 if player.input_down else 0)
            player.di_direction = (di_x, di_y)


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
            'eliminated': self.eliminated_players,
            'mode': self.mode_manager.get_state(),
            'scoreboard': self.mode_manager.get_scoreboard() if self.state == MatchState.PLAYING else None
        }

    def get_player(self, player_id: str) -> Optional[Player]:
        """Get a player by ID"""
        return self.players.get(player_id)
