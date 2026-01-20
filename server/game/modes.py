"""
Arena Brawl - Game Modes
Implements different match types: Stock, Time, Stamina, Teams
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import time


class GameMode(Enum):
    """Available game modes"""
    STOCK = "stock"          # Lives-based, last standing wins
    TIME = "time"            # Most KOs in time limit wins
    STAMINA = "stamina"      # HP bars, reach 0 = KO
    TEAMS = "teams"          # Team-based (2v2, 3v3)


class TeamColor(Enum):
    """Team colors for team battles"""
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"


@dataclass
class ModeSettings:
    """Settings for game modes"""
    mode: GameMode = GameMode.STOCK

    # Stock mode settings
    stock_count: int = 3          # Lives per player

    # Time mode settings
    time_limit: float = 180.0     # Match duration in seconds
    time_ko_points: int = 1       # Points per KO
    time_fall_penalty: int = 1    # Points lost for self-destruct

    # Stamina mode settings
    stamina_hp: int = 150         # Starting HP in stamina mode
    stamina_ko_invincibility: float = 2.0  # Invincibility after KO

    # Team settings
    team_attack: bool = False     # Friendly fire enabled
    team_size: int = 2            # Players per team (2 or 3)
    team_stock_share: bool = False  # Share stocks between teammates

    # Common settings
    stage_hazards: bool = True    # Enable stage hazards
    items_enabled: bool = True    # Enable item spawns


@dataclass
class PlayerModeState:
    """Per-player state for different game modes"""
    player_id: str

    # Stock mode
    stocks: int = 3

    # Time mode
    ko_count: int = 0             # KOs scored
    fall_count: int = 0           # Self-destructs
    score: int = 0                # Net score (KOs - falls)

    # Stamina mode
    stamina_hp: int = 150
    stamina_max_hp: int = 150

    # Team mode
    team: Optional[TeamColor] = None

    # Common
    damage_dealt: int = 0
    damage_taken: int = 0


@dataclass
class TeamState:
    """State for a team in team battles"""
    color: TeamColor
    player_ids: List[str] = field(default_factory=list)
    total_stocks: int = 0         # Combined stocks (if stock share)
    total_score: int = 0          # Combined score (time mode)
    total_kos: int = 0


class ModeManager:
    """Manages game mode logic"""

    def __init__(self, settings: ModeSettings = None):
        self.settings = settings or ModeSettings()
        self.player_states: Dict[str, PlayerModeState] = {}
        self.teams: Dict[TeamColor, TeamState] = {}
        self.match_start_time: float = 0.0
        self.is_active: bool = False

    def initialize(self, player_ids: List[str], team_assignments: Dict[str, TeamColor] = None):
        """Initialize mode state for all players"""
        self.player_states.clear()
        self.teams.clear()
        self.match_start_time = time.time()
        self.is_active = True

        for player_id in player_ids:
            state = PlayerModeState(
                player_id=player_id,
                stocks=self.settings.stock_count,
                stamina_hp=self.settings.stamina_hp,
                stamina_max_hp=self.settings.stamina_hp
            )

            # Assign team if in team mode
            if self.settings.mode == GameMode.TEAMS and team_assignments:
                state.team = team_assignments.get(player_id)

            self.player_states[player_id] = state

        # Initialize teams if in team mode
        if self.settings.mode == GameMode.TEAMS:
            self._initialize_teams(team_assignments or {})

    def _initialize_teams(self, team_assignments: Dict[str, TeamColor]):
        """Set up team states"""
        for player_id, team_color in team_assignments.items():
            if team_color not in self.teams:
                self.teams[team_color] = TeamState(color=team_color)
            self.teams[team_color].player_ids.append(player_id)

            # Calculate total stocks for stock share mode
            if self.settings.team_stock_share:
                self.teams[team_color].total_stocks += self.settings.stock_count

    def process_hit(self, attacker_id: str, target_id: str, damage: int,
                    knockback: float = 0) -> dict:
        """Process a hit in the current game mode"""
        result = {
            'damage_dealt': damage,
            'ko': False,
            'ko_type': None,
            'attacker_id': attacker_id,
            'target_id': target_id
        }

        if target_id not in self.player_states:
            return result

        target_state = self.player_states[target_id]
        target_state.damage_taken += damage

        if attacker_id in self.player_states:
            self.player_states[attacker_id].damage_dealt += damage

        # Stamina mode: Check HP-based KO
        if self.settings.mode == GameMode.STAMINA:
            target_state.stamina_hp = max(0, target_state.stamina_hp - damage)

            if target_state.stamina_hp <= 0:
                result['ko'] = True
                result['ko_type'] = 'stamina'
                self._process_ko(attacker_id, target_id)

        return result

    def process_blast_zone_ko(self, player_id: str, last_hit_by: str = None) -> dict:
        """Process a blast zone KO"""
        result = {
            'ko': True,
            'ko_type': 'blast_zone',
            'player_id': player_id,
            'last_hit_by': last_hit_by,
            'is_sd': last_hit_by is None or last_hit_by == player_id
        }

        if player_id not in self.player_states:
            return result

        player_state = self.player_states[player_id]

        if self.settings.mode == GameMode.STOCK:
            player_state.stocks -= 1
            result['stocks_remaining'] = player_state.stocks

            if self.settings.mode == GameMode.TEAMS and self.settings.team_stock_share:
                if player_state.team and player_state.team in self.teams:
                    self.teams[player_state.team].total_stocks -= 1

        elif self.settings.mode == GameMode.TIME:
            if result['is_sd']:
                player_state.fall_count += 1
                player_state.score -= self.settings.time_fall_penalty

            if last_hit_by and last_hit_by != player_id:
                if last_hit_by in self.player_states:
                    attacker_state = self.player_states[last_hit_by]
                    attacker_state.ko_count += 1
                    attacker_state.score += self.settings.time_ko_points

                    # Update team score
                    if self.settings.mode == GameMode.TEAMS and attacker_state.team:
                        if attacker_state.team in self.teams:
                            self.teams[attacker_state.team].total_score += self.settings.time_ko_points
                            self.teams[attacker_state.team].total_kos += 1

        elif self.settings.mode == GameMode.STAMINA:
            player_state.stocks -= 1
            result['stocks_remaining'] = player_state.stocks

        return result

    def _process_ko(self, attacker_id: str, target_id: str):
        """Handle KO scoring"""
        if attacker_id and attacker_id in self.player_states:
            self.player_states[attacker_id].ko_count += 1
            self.player_states[attacker_id].score += self.settings.time_ko_points

    def respawn_player(self, player_id: str) -> dict:
        """Handle player respawn based on mode"""
        result = {
            'can_respawn': False,
            'hp': 0,
            'stocks': 0
        }

        if player_id not in self.player_states:
            return result

        state = self.player_states[player_id]

        if self.settings.mode == GameMode.STOCK:
            if state.stocks > 0:
                result['can_respawn'] = True
                result['stocks'] = state.stocks

        elif self.settings.mode == GameMode.TIME:
            # Always respawn in time mode
            result['can_respawn'] = True

        elif self.settings.mode == GameMode.STAMINA:
            if state.stocks > 0:
                result['can_respawn'] = True
                state.stamina_hp = state.stamina_max_hp
                result['hp'] = state.stamina_hp
                result['stocks'] = state.stocks

        elif self.settings.mode == GameMode.TEAMS:
            if self.settings.team_stock_share and state.team:
                team = self.teams.get(state.team)
                if team and team.total_stocks > 0:
                    result['can_respawn'] = True
                    result['stocks'] = team.total_stocks
            elif state.stocks > 0:
                result['can_respawn'] = True
                result['stocks'] = state.stocks

        return result

    def is_team_attack_allowed(self, attacker_id: str, target_id: str) -> bool:
        """Check if attack between players is allowed (team mode)"""
        if self.settings.mode != GameMode.TEAMS:
            return True

        if self.settings.team_attack:
            return True  # Friendly fire enabled

        attacker_state = self.player_states.get(attacker_id)
        target_state = self.player_states.get(target_id)

        if not attacker_state or not target_state:
            return True

        # Block attack if same team
        return attacker_state.team != target_state.team

    def get_time_remaining(self) -> float:
        """Get remaining match time"""
        if self.settings.mode not in [GameMode.TIME, GameMode.STOCK, GameMode.STAMINA]:
            return 0.0

        elapsed = time.time() - self.match_start_time
        return max(0.0, self.settings.time_limit - elapsed)

    def check_win_condition(self) -> dict:
        """Check if match should end and determine winner"""
        result = {
            'match_over': False,
            'winner_id': None,
            'winner_team': None,
            'reason': None
        }

        if not self.is_active:
            return result

        if self.settings.mode == GameMode.STOCK:
            return self._check_stock_win()
        elif self.settings.mode == GameMode.TIME:
            return self._check_time_win()
        elif self.settings.mode == GameMode.STAMINA:
            return self._check_stamina_win()
        elif self.settings.mode == GameMode.TEAMS:
            return self._check_teams_win()

        return result

    def _check_stock_win(self) -> dict:
        """Check stock mode win condition"""
        result = {'match_over': False, 'winner_id': None, 'reason': None}

        alive_players = [pid for pid, state in self.player_states.items()
                        if state.stocks > 0]

        if len(alive_players) <= 1 and len(self.player_states) > 1:
            result['match_over'] = True
            result['winner_id'] = alive_players[0] if alive_players else None
            result['reason'] = 'last_standing'
            self.is_active = False

        return result

    def _check_time_win(self) -> dict:
        """Check time mode win condition"""
        result = {'match_over': False, 'winner_id': None, 'reason': None}

        if self.get_time_remaining() <= 0:
            result['match_over'] = True
            result['reason'] = 'time_up'

            # Find player with highest score
            best_player = None
            best_score = float('-inf')

            for pid, state in self.player_states.items():
                if state.score > best_score:
                    best_score = state.score
                    best_player = pid

            result['winner_id'] = best_player
            self.is_active = False

        return result

    def _check_stamina_win(self) -> dict:
        """Check stamina mode win condition"""
        result = {'match_over': False, 'winner_id': None, 'reason': None}

        alive_players = [pid for pid, state in self.player_states.items()
                        if state.stocks > 0 or state.stamina_hp > 0]

        if len(alive_players) <= 1 and len(self.player_states) > 1:
            result['match_over'] = True
            result['winner_id'] = alive_players[0] if alive_players else None
            result['reason'] = 'last_standing'
            self.is_active = False

        # Also check time limit
        if self.get_time_remaining() <= 0:
            result['match_over'] = True
            result['reason'] = 'time_up'

            # Winner is player with most HP remaining
            best_player = None
            best_hp = -1

            for pid, state in self.player_states.items():
                total_hp = state.stamina_hp + (state.stocks * state.stamina_max_hp)
                if total_hp > best_hp:
                    best_hp = total_hp
                    best_player = pid

            result['winner_id'] = best_player
            self.is_active = False

        return result

    def _check_teams_win(self) -> dict:
        """Check teams mode win condition"""
        result = {'match_over': False, 'winner_team': None, 'reason': None}

        if self.settings.team_stock_share:
            # Check team stocks
            alive_teams = [color for color, team in self.teams.items()
                          if team.total_stocks > 0]
        else:
            # Check individual stocks per team
            alive_teams = []
            for color, team in self.teams.items():
                team_alive = any(
                    self.player_states.get(pid, PlayerModeState(pid)).stocks > 0
                    for pid in team.player_ids
                )
                if team_alive:
                    alive_teams.append(color)

        if len(alive_teams) <= 1 and len(self.teams) > 1:
            result['match_over'] = True
            result['winner_team'] = alive_teams[0] if alive_teams else None
            result['reason'] = 'team_eliminated'
            self.is_active = False

        # Also check time limit
        if self.get_time_remaining() <= 0:
            result['match_over'] = True
            result['reason'] = 'time_up'

            # Winner is team with highest score or most stocks
            best_team = None
            best_value = -1

            for color, team in self.teams.items():
                value = team.total_score if team.total_score > 0 else team.total_stocks
                if value > best_value:
                    best_value = value
                    best_team = color

            result['winner_team'] = best_team
            self.is_active = False

        return result

    def get_state(self) -> dict:
        """Get current mode state for network sync"""
        return {
            'mode': self.settings.mode.value,
            'time_remaining': round(self.get_time_remaining(), 1),
            'settings': {
                'stock_count': self.settings.stock_count,
                'time_limit': self.settings.time_limit,
                'stamina_hp': self.settings.stamina_hp,
                'team_attack': self.settings.team_attack,
                'team_stock_share': self.settings.team_stock_share,
                'stage_hazards': self.settings.stage_hazards
            },
            'players': {
                pid: {
                    'stocks': state.stocks,
                    'score': state.score,
                    'ko_count': state.ko_count,
                    'fall_count': state.fall_count,
                    'stamina_hp': state.stamina_hp,
                    'stamina_max_hp': state.stamina_max_hp,
                    'team': state.team.value if state.team else None,
                    'damage_dealt': state.damage_dealt,
                    'damage_taken': state.damage_taken
                }
                for pid, state in self.player_states.items()
            },
            'teams': {
                color.value: {
                    'player_ids': team.player_ids,
                    'total_stocks': team.total_stocks,
                    'total_score': team.total_score,
                    'total_kos': team.total_kos
                }
                for color, team in self.teams.items()
            } if self.teams else None
        }

    def get_scoreboard(self) -> List[dict]:
        """Get sorted scoreboard for display"""
        entries = []

        for pid, state in self.player_states.items():
            entry = {
                'player_id': pid,
                'stocks': state.stocks,
                'score': state.score,
                'ko_count': state.ko_count,
                'fall_count': state.fall_count,
                'damage_dealt': state.damage_dealt,
                'team': state.team.value if state.team else None
            }
            entries.append(entry)

        # Sort by score (time mode) or stocks (stock mode)
        if self.settings.mode == GameMode.TIME:
            entries.sort(key=lambda e: e['score'], reverse=True)
        else:
            entries.sort(key=lambda e: (e['stocks'], e['ko_count']), reverse=True)

        return entries


# Preset mode configurations
PRESET_MODES = {
    'stock_3': ModeSettings(
        mode=GameMode.STOCK,
        stock_count=3,
        time_limit=480.0  # 8 minute time limit
    ),
    'stock_5': ModeSettings(
        mode=GameMode.STOCK,
        stock_count=5,
        time_limit=600.0  # 10 minute time limit
    ),
    'time_3min': ModeSettings(
        mode=GameMode.TIME,
        time_limit=180.0,
        stock_count=99  # Unlimited respawns
    ),
    'time_5min': ModeSettings(
        mode=GameMode.TIME,
        time_limit=300.0,
        stock_count=99
    ),
    'stamina_150': ModeSettings(
        mode=GameMode.STAMINA,
        stamina_hp=150,
        stock_count=1,
        time_limit=300.0
    ),
    'stamina_300': ModeSettings(
        mode=GameMode.STAMINA,
        stamina_hp=300,
        stock_count=1,
        time_limit=480.0
    ),
    'teams_2v2': ModeSettings(
        mode=GameMode.TEAMS,
        team_size=2,
        stock_count=3,
        team_attack=False,
        team_stock_share=False
    ),
    'teams_2v2_share': ModeSettings(
        mode=GameMode.TEAMS,
        team_size=2,
        stock_count=3,
        team_attack=False,
        team_stock_share=True  # 6 shared stocks per team
    ),
    'competitive': ModeSettings(
        mode=GameMode.STOCK,
        stock_count=3,
        time_limit=480.0,
        stage_hazards=False,
        items_enabled=False
    )
}


def get_preset_mode(name: str) -> ModeSettings:
    """Get a preset mode configuration"""
    return PRESET_MODES.get(name, ModeSettings())


def get_available_modes() -> List[str]:
    """Get list of available preset modes"""
    return list(PRESET_MODES.keys())
