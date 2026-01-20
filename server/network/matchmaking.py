"""
Arena Brawl - Matchmaking
Handles automatic matchmaking and room assignment
"""
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import deque

from server.config import Config
from server.network.lobby import LobbyManager, Room


@dataclass
class QueuedPlayer:
    """A player waiting in matchmaking queue"""
    player_id: str
    socket_id: str
    name: str
    character: str = "Storm"
    queue_time: float = field(default_factory=time.time)


class Matchmaker:
    """Automatic matchmaking system"""

    def __init__(self, lobby_manager: LobbyManager, config: Config = None):
        self.lobby = lobby_manager
        self.config = config or Config()

        # Queue of players waiting for a match
        self.queue: deque = deque()
        self.queued_players: Dict[str, QueuedPlayer] = {}

        # Matchmaking settings
        self.min_players = 2
        self.max_players = 4
        self.max_wait_time = 30.0  # Start with 2 players after 30 seconds

    def add_to_queue(self, player_id: str, socket_id: str,
                     name: str, character: str = "Storm") -> bool:
        """Add a player to the matchmaking queue"""
        if player_id in self.queued_players:
            return False

        player = QueuedPlayer(
            player_id=player_id,
            socket_id=socket_id,
            name=name,
            character=character
        )

        self.queue.append(player_id)
        self.queued_players[player_id] = player
        return True

    def remove_from_queue(self, player_id: str) -> bool:
        """Remove a player from the queue"""
        if player_id not in self.queued_players:
            return False

        del self.queued_players[player_id]
        # Note: We don't remove from deque, will be skipped when processing
        return True

    def process_queue(self) -> List[Room]:
        """Process the queue and create matches"""
        created_rooms = []
        current_time = time.time()

        # Clean up old queue entries
        self.queue = deque([
            pid for pid in self.queue
            if pid in self.queued_players
        ])

        while len(self.queue) >= self.min_players:
            # Check if we have enough players or someone waited too long
            oldest_player_id = self.queue[0]
            oldest_player = self.queued_players.get(oldest_player_id)

            if not oldest_player:
                self.queue.popleft()
                continue

            wait_time = current_time - oldest_player.queue_time

            # Determine how many players to match
            if len(self.queue) >= self.max_players:
                match_size = self.max_players
            elif wait_time >= self.max_wait_time and len(self.queue) >= self.min_players:
                match_size = len(self.queue)
            else:
                break  # Wait for more players

            # Create a match
            room = self._create_match(match_size)
            if room:
                created_rooms.append(room)

        return created_rooms

    def _create_match(self, player_count: int) -> Optional[Room]:
        """Create a match with queued players"""
        if player_count > len(self.queue):
            return None

        # Get players from queue
        match_players = []
        for _ in range(player_count):
            if not self.queue:
                break

            player_id = self.queue.popleft()
            player = self.queued_players.pop(player_id, None)
            if player:
                match_players.append(player)

        if len(match_players) < self.min_players:
            # Put players back in queue
            for player in match_players:
                self.queue.appendleft(player.player_id)
                self.queued_players[player.player_id] = player
            return None

        # Create room with first player as host
        host = match_players[0]
        room = self.lobby.create_room(
            host_id=host.player_id,
            host_socket=host.socket_id,
            host_name=host.name,
            room_name="Quick Match"
        )

        if not room:
            # Put players back
            for player in match_players:
                self.queue.appendleft(player.player_id)
                self.queued_players[player.player_id] = player
            return None

        # Set host's character
        room.set_player_character(host.player_id, host.character)

        # Add remaining players
        for player in match_players[1:]:
            self.lobby.join_room(
                room.room_id,
                player.player_id,
                player.socket_id,
                player.name
            )
            room.set_player_character(player.player_id, player.character)

        # Auto-ready all players
        for player in match_players:
            room.set_player_ready(player.player_id, True)

        return room

    def get_queue_status(self) -> dict:
        """Get current queue status"""
        return {
            'players_in_queue': len(self.queued_players),
            'estimated_wait': self._estimate_wait_time()
        }

    def _estimate_wait_time(self) -> float:
        """Estimate wait time for new players"""
        players_needed = self.min_players - len(self.queue)
        if players_needed <= 0:
            return 0.0

        # Rough estimate based on recent activity
        # For now, return a simple estimate
        return max(0, players_needed * 5.0)  # ~5 seconds per player needed

    def get_queued_player_ids(self) -> List[str]:
        """Get list of queued player IDs"""
        return list(self.queued_players.keys())
