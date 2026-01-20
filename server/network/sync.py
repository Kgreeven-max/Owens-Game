"""
Arena Brawl - State Synchronization
Handles game state synchronization between server and clients
"""
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from collections import deque


@dataclass
class InputFrame:
    """A single frame of player input"""
    frame_number: int
    timestamp: float
    move: str = "none"
    action: str = "none"
    jump: bool = False
    hide: bool = False


class InputBuffer:
    """Buffer for handling client inputs with latency compensation"""

    def __init__(self, buffer_size: int = 10):
        self.buffer_size = buffer_size
        self.inputs: deque = deque(maxlen=buffer_size)
        self.last_processed_frame = 0

    def add_input(self, input_frame: InputFrame):
        """Add an input frame to the buffer"""
        # Only accept newer inputs
        if input_frame.frame_number > self.last_processed_frame:
            self.inputs.append(input_frame)

    def get_next_input(self) -> Optional[InputFrame]:
        """Get the next input to process"""
        if not self.inputs:
            return None

        input_frame = self.inputs.popleft()
        self.last_processed_frame = input_frame.frame_number
        return input_frame

    def clear(self):
        """Clear the buffer"""
        self.inputs.clear()


class StateSynchronizer:
    """Manages game state synchronization"""

    def __init__(self, tick_rate: int = 60):
        self.tick_rate = tick_rate
        self.tick_interval = 1.0 / tick_rate

        # State tracking
        self.current_frame = 0
        self.last_sync_time = 0.0

        # Player input buffers
        self.input_buffers: Dict[str, InputBuffer] = {}

        # Delta compression - track last sent state
        self.last_sent_state: Dict[str, Any] = {}

        # Latency tracking per player
        self.player_latency: Dict[str, float] = {}

    def register_player(self, player_id: str):
        """Register a new player for synchronization"""
        self.input_buffers[player_id] = InputBuffer()
        self.player_latency[player_id] = 0.0

    def unregister_player(self, player_id: str):
        """Unregister a player"""
        if player_id in self.input_buffers:
            del self.input_buffers[player_id]
        if player_id in self.player_latency:
            del self.player_latency[player_id]

    def receive_input(self, player_id: str, input_data: dict):
        """Receive input from a client"""
        if player_id not in self.input_buffers:
            return

        # Calculate latency
        client_time = input_data.get('timestamp', 0)
        if client_time > 0:
            latency = time.time() * 1000 - client_time
            # Smooth latency estimate
            old_latency = self.player_latency.get(player_id, latency)
            self.player_latency[player_id] = old_latency * 0.8 + latency * 0.2

        input_frame = InputFrame(
            frame_number=input_data.get('frame', self.current_frame),
            timestamp=input_data.get('timestamp', time.time() * 1000),
            move=input_data.get('move', 'none'),
            action=input_data.get('action', 'none'),
            jump=input_data.get('jump', False),
            hide=input_data.get('hide', False)
        )

        self.input_buffers[player_id].add_input(input_frame)

    def get_pending_inputs(self, player_id: str) -> List[InputFrame]:
        """Get all pending inputs for a player"""
        if player_id not in self.input_buffers:
            return []

        inputs = []
        buffer = self.input_buffers[player_id]
        while True:
            input_frame = buffer.get_next_input()
            if not input_frame:
                break
            inputs.append(input_frame)

        return inputs

    def get_latest_input(self, player_id: str) -> Optional[dict]:
        """Get the most recent input for a player"""
        inputs = self.get_pending_inputs(player_id)
        if not inputs:
            return None

        # Return the latest input as dict
        latest = inputs[-1]
        return {
            'move': latest.move,
            'action': latest.action,
            'jump': latest.jump,
            'hide': latest.hide
        }

    def should_sync(self) -> bool:
        """Check if it's time for a state sync"""
        current_time = time.time()
        if current_time - self.last_sync_time >= self.tick_interval:
            self.last_sync_time = current_time
            self.current_frame += 1
            return True
        return False

    def create_state_update(self, game_state: dict) -> dict:
        """Create a state update packet with frame info"""
        return {
            'frame': self.current_frame,
            'timestamp': int(time.time() * 1000),
            'state': game_state
        }

    def create_delta_update(self, player_id: str, game_state: dict) -> Optional[dict]:
        """Create a delta update (only changed data) for a player"""
        last_state = self.last_sent_state.get(player_id, {})
        delta = self._compute_delta(last_state, game_state)

        if not delta:
            return None

        self.last_sent_state[player_id] = game_state.copy()

        return {
            'frame': self.current_frame,
            'timestamp': int(time.time() * 1000),
            'delta': delta
        }

    def _compute_delta(self, old_state: dict, new_state: dict) -> dict:
        """Compute the difference between two states"""
        delta = {}

        for key, new_value in new_state.items():
            old_value = old_state.get(key)
            if old_value != new_value:
                delta[key] = new_value

        return delta

    def get_player_latency(self, player_id: str) -> float:
        """Get estimated latency for a player in milliseconds"""
        return self.player_latency.get(player_id, 0.0)

    def get_all_latencies(self) -> Dict[str, float]:
        """Get latencies for all players"""
        return self.player_latency.copy()


class InterpolationBuffer:
    """Client-side interpolation buffer for smooth rendering"""

    def __init__(self, buffer_time_ms: float = 100.0):
        self.buffer_time = buffer_time_ms
        self.states: deque = deque(maxlen=60)  # ~1 second at 60 FPS

    def add_state(self, state: dict, timestamp: float):
        """Add a received state to the buffer"""
        self.states.append({
            'state': state,
            'timestamp': timestamp
        })

    def get_interpolated_state(self, render_time: float) -> Optional[dict]:
        """Get interpolated state for rendering"""
        if len(self.states) < 2:
            return self.states[-1]['state'] if self.states else None

        # Find states to interpolate between
        target_time = render_time - self.buffer_time

        before = None
        after = None

        for state_entry in self.states:
            if state_entry['timestamp'] <= target_time:
                before = state_entry
            else:
                after = state_entry
                break

        if not before:
            return self.states[0]['state']
        if not after:
            return self.states[-1]['state']

        # Calculate interpolation factor
        time_diff = after['timestamp'] - before['timestamp']
        if time_diff <= 0:
            return before['state']

        t = (target_time - before['timestamp']) / time_diff
        t = max(0, min(1, t))

        # Interpolate player positions
        return self._interpolate_states(before['state'], after['state'], t)

    def _interpolate_states(self, state1: dict, state2: dict, t: float) -> dict:
        """Interpolate between two game states"""
        result = state2.copy()

        # Interpolate player positions
        if 'players' in state1 and 'players' in state2:
            result['players'] = []
            for i, player2 in enumerate(state2['players']):
                if i < len(state1['players']):
                    player1 = state1['players'][i]
                    interpolated = player2.copy()

                    # Lerp position
                    interpolated['x'] = player1['x'] + (player2['x'] - player1['x']) * t
                    interpolated['y'] = player1['y'] + (player2['y'] - player1['y']) * t

                    result['players'].append(interpolated)
                else:
                    result['players'].append(player2)

        return result
