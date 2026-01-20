"""
Arena Brawl - Lobby Management
Handles room creation, player joining, and matchmaking
"""
import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum

from server.config import Config
from server.game.engine import GameEngine, MatchState
from server.entities.character import get_character_names
from server.maps.arenas import get_arena_names


class RoomState(Enum):
    OPEN = "open"          # Accepting players
    FULL = "full"          # Max players, waiting to start
    IN_GAME = "in_game"    # Match in progress
    CLOSED = "closed"      # Room is closing


@dataclass
class RoomPlayer:
    """Player info in a room"""
    player_id: str
    socket_id: str
    name: str
    character: str = "Storm"
    is_ready: bool = False
    is_host: bool = False


@dataclass
class Room:
    """A game room/lobby"""
    room_id: str
    name: str
    host_id: str
    arena: str = "street"
    max_players: int = 4
    is_private: bool = False
    password: Optional[str] = None

    state: RoomState = RoomState.OPEN
    players: Dict[str, RoomPlayer] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    # Game instance
    game: Optional[GameEngine] = None

    def add_player(self, player_id: str, socket_id: str, name: str,
                   character: str = "Storm") -> Optional[RoomPlayer]:
        """Add a player to the room"""
        if len(self.players) >= self.max_players:
            return None
        if self.state != RoomState.OPEN:
            return None

        is_host = len(self.players) == 0
        player = RoomPlayer(
            player_id=player_id,
            socket_id=socket_id,
            name=name,
            character=character,
            is_host=is_host
        )
        self.players[player_id] = player

        if len(self.players) >= self.max_players:
            self.state = RoomState.FULL

        return player

    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the room"""
        if player_id not in self.players:
            return False

        was_host = self.players[player_id].is_host
        del self.players[player_id]

        # Assign new host if needed
        if was_host and self.players:
            new_host_id = next(iter(self.players))
            self.players[new_host_id].is_host = True
            self.host_id = new_host_id

        if self.state == RoomState.FULL:
            self.state = RoomState.OPEN

        return True

    def set_player_ready(self, player_id: str, ready: bool = True) -> bool:
        """Set player ready status"""
        if player_id not in self.players:
            return False
        self.players[player_id].is_ready = ready
        return True

    def set_player_character(self, player_id: str, character: str) -> bool:
        """Set player's character selection"""
        if player_id not in self.players:
            return False
        if character not in get_character_names():
            return False
        self.players[player_id].character = character
        return True

    def all_ready(self) -> bool:
        """Check if all players are ready"""
        if len(self.players) < 2:
            return False
        return all(p.is_ready for p in self.players.values())

    def can_start(self) -> bool:
        """Check if game can start"""
        return len(self.players) >= 2 and self.all_ready()

    def start_game(self, config: Config = None) -> GameEngine:
        """Start the game"""
        self.state = RoomState.IN_GAME

        # Create game engine
        self.game = GameEngine(self.room_id, config)
        self.game.set_arena(self.arena)

        # Add all players
        for player in self.players.values():
            self.game.add_player(player.player_id, player.name, player.character)

        # Start countdown
        self.game.start_countdown()

        return self.game

    def to_dict(self) -> dict:
        """Serialize room info"""
        return {
            'room_id': self.room_id,
            'name': self.name,
            'host_id': self.host_id,
            'arena': self.arena,
            'max_players': self.max_players,
            'player_count': len(self.players),
            'state': self.state.value,
            'is_private': self.is_private,
            'players': [
                {
                    'id': p.player_id,
                    'name': p.name,
                    'character': p.character,
                    'is_ready': p.is_ready,
                    'is_host': p.is_host
                }
                for p in self.players.values()
            ]
        }


class LobbyManager:
    """Manages all game rooms"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.rooms: Dict[str, Room] = {}
        self.player_rooms: Dict[str, str] = {}  # player_id -> room_id

    def create_room(self, host_id: str, host_socket: str, host_name: str,
                    room_name: str = None, arena: str = "street",
                    is_private: bool = False, password: str = None) -> Room:
        """Create a new game room"""
        if len(self.rooms) >= self.config.MAX_ROOMS:
            return None

        room_id = str(uuid.uuid4())[:8]
        room_name = room_name or f"{host_name}'s Room"

        room = Room(
            room_id=room_id,
            name=room_name,
            host_id=host_id,
            arena=arena,
            max_players=self.config.MAX_PLAYERS_PER_ROOM,
            is_private=is_private,
            password=password
        )

        # Add host as first player
        room.add_player(host_id, host_socket, host_name)

        self.rooms[room_id] = room
        self.player_rooms[host_id] = room_id

        return room

    def join_room(self, room_id: str, player_id: str, socket_id: str,
                  player_name: str, password: str = None) -> Optional[Room]:
        """Join an existing room"""
        room = self.rooms.get(room_id)
        if not room:
            return None

        if room.state != RoomState.OPEN:
            return None

        if room.is_private and room.password and room.password != password:
            return None

        player = room.add_player(player_id, socket_id, player_name)
        if not player:
            return None

        self.player_rooms[player_id] = room_id
        return room

    def leave_room(self, player_id: str) -> Optional[Room]:
        """Leave current room"""
        room_id = self.player_rooms.get(player_id)
        if not room_id:
            return None

        room = self.rooms.get(room_id)
        if not room:
            del self.player_rooms[player_id]
            return None

        room.remove_player(player_id)
        del self.player_rooms[player_id]

        # Delete empty rooms
        if not room.players:
            del self.rooms[room_id]
            return None

        return room

    def get_room(self, room_id: str) -> Optional[Room]:
        """Get a room by ID"""
        return self.rooms.get(room_id)

    def get_player_room(self, player_id: str) -> Optional[Room]:
        """Get the room a player is in"""
        room_id = self.player_rooms.get(player_id)
        if room_id:
            return self.rooms.get(room_id)
        return None

    def get_public_rooms(self) -> List[Room]:
        """Get list of public, joinable rooms"""
        return [
            room for room in self.rooms.values()
            if not room.is_private and room.state == RoomState.OPEN
        ]

    def quick_match(self, player_id: str, socket_id: str,
                    player_name: str) -> Optional[Room]:
        """Find or create a room for quick matchmaking"""
        # First try to join an existing public room
        public_rooms = self.get_public_rooms()
        for room in public_rooms:
            if room.state == RoomState.OPEN:
                result = self.join_room(room.room_id, player_id, socket_id, player_name)
                if result:
                    return result

        # No available rooms, create a new one
        return self.create_room(player_id, socket_id, player_name)

    def close_room(self, room_id: str):
        """Close and remove a room"""
        room = self.rooms.get(room_id)
        if room:
            room.state = RoomState.CLOSED
            for player_id in list(room.players.keys()):
                if player_id in self.player_rooms:
                    del self.player_rooms[player_id]
            del self.rooms[room_id]

    def get_room_list(self) -> List[dict]:
        """Get list of all rooms for display"""
        return [room.to_dict() for room in self.rooms.values()
                if not room.is_private]


# Global lobby manager instance
lobby_manager = LobbyManager()
