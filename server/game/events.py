"""
Arena Brawl - Game Events
Handles power-up drops and other timed events
"""
import time
import random
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Callable
from enum import Enum

from server.config import Config
from server.entities.powerup import PowerUp
from server.entities.healthbox import HealthBox


class EventType(Enum):
    POWERUP_SPAWN = "powerup_spawn"
    HEALTHBOX_SPAWN = "healthbox_spawn"
    SUDDEN_DEATH = "sudden_death"


@dataclass
class GameEvent:
    """A scheduled game event"""
    event_type: EventType
    trigger_time: float
    data: dict = field(default_factory=dict)
    is_triggered: bool = False


class EventManager:
    """Manages game events and timing"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.events: List[GameEvent] = []
        self.active_powerups: List[PowerUp] = []
        self.active_healthboxes: List[HealthBox] = []

        # Spawn positions for items
        self.arena_width = self.config.ARENA_WIDTH
        self.arena_height = self.config.ARENA_HEIGHT
        self.ground_y = self.config.GROUND_Y

        # Timing
        self.last_item_spawn = 0.0
        self.next_item_time = 0.0

        # Callbacks
        self.on_event: Optional[Callable] = None

    def initialize(self, match_start_time: float):
        """Initialize events for a new match"""
        self.events.clear()
        self.active_powerups.clear()
        self.active_healthboxes.clear()

        # Schedule first item spawn
        self._schedule_next_item(match_start_time)

    def _schedule_next_item(self, current_time: float):
        """Schedule next power-up or health box spawn"""
        min_interval, max_interval = self.config.POWERUP_SPAWN_INTERVAL
        delay = random.uniform(min_interval, max_interval)
        self.next_item_time = current_time + delay

        # Randomly choose power-up or health box
        event_type = random.choice([EventType.POWERUP_SPAWN, EventType.HEALTHBOX_SPAWN])

        # Random spawn position
        spawn_x = random.uniform(100, self.arena_width - 100)
        spawn_y = random.uniform(self.ground_y - 200, self.ground_y - 50)

        self.events.append(GameEvent(
            event_type=event_type,
            trigger_time=self.next_item_time,
            data={'x': spawn_x, 'y': spawn_y}
        ))

    def update(self, current_time: float) -> List[dict]:
        """Update events and return any triggered event data"""
        triggered_events = []

        for event in self.events:
            if event.is_triggered:
                continue
            if current_time >= event.trigger_time:
                event.is_triggered = True
                event_data = self._handle_event(event, current_time)
                if event_data:
                    triggered_events.append(event_data)

        # Clean up old events
        self.events = [e for e in self.events if not e.is_triggered]

        # Update active items
        for powerup in self.active_powerups:
            powerup.update(1/60)
        for healthbox in self.active_healthboxes:
            healthbox.update(1/60)

        return triggered_events

    def _handle_event(self, event: GameEvent, current_time: float) -> Optional[dict]:
        """Handle a triggered event"""
        if event.event_type == EventType.POWERUP_SPAWN:
            powerup = PowerUp.create_random(
                id=str(uuid.uuid4())[:8],
                x=event.data['x'],
                y=event.data['y']
            )
            powerup.spawn_time = current_time
            self.active_powerups.append(powerup)
            # Schedule next item
            self._schedule_next_item(current_time)
            return {
                'type': 'powerup_spawn',
                'powerup': powerup.to_dict()
            }

        elif event.event_type == EventType.HEALTHBOX_SPAWN:
            healthbox = HealthBox.create_random(
                id=str(uuid.uuid4())[:8],
                x=event.data['x'],
                y=event.data['y']
            )
            healthbox.spawn_time = current_time
            self.active_healthboxes.append(healthbox)
            # Schedule next item
            self._schedule_next_item(current_time)
            return {
                'type': 'healthbox_spawn',
                'healthbox': healthbox.to_dict()
            }

        return None

    def collect_powerup(self, powerup_id: str, player) -> Optional[dict]:
        """Player collects a power-up"""
        for powerup in self.active_powerups:
            if powerup.id == powerup_id and powerup.is_active:
                powerup.is_active = False

                # Apply effect
                if powerup.powerup_type.value == 'speed_boost':
                    player.apply_buff(speed_boost=powerup.multiplier,
                                      duration=powerup.duration)
                elif powerup.powerup_type.value == 'damage_boost':
                    player.apply_buff(damage_boost=powerup.multiplier,
                                      duration=powerup.duration)
                elif powerup.powerup_type.value == 'invincibility':
                    player.set_invincible(powerup.duration)

                self.active_powerups.remove(powerup)
                return {
                    'type': 'powerup_collected',
                    'powerup_id': powerup_id,
                    'player_id': player.id,
                    'effect': powerup.powerup_type.value,
                    'duration': powerup.duration
                }
        return None

    def collect_healthbox(self, healthbox_id: str, player) -> Optional[dict]:
        """Player collects a health box"""
        for healthbox in self.active_healthboxes:
            if healthbox.id == healthbox_id and healthbox.is_active:
                effects = healthbox.apply_to_player(player)
                self.active_healthboxes.remove(healthbox)
                return {
                    'type': 'healthbox_collected',
                    'healthbox_id': healthbox_id,
                    'player_id': player.id,
                    'tier': healthbox.tier.value,
                    'healed': effects['healed'],
                    'buff_type': effects['buff_type'],
                    'buff_duration': effects['buff_duration']
                }
        return None

    def get_state(self) -> dict:
        """Get current event state for network sync"""
        return {
            'powerups': [p.to_dict() for p in self.active_powerups if p.is_active],
            'healthboxes': [h.to_dict() for h in self.active_healthboxes if h.is_active]
        }
