"""
Arena Brawl - Physics Engine
Handles gravity, collision detection, knockback, and movement
"""
from dataclasses import dataclass
from typing import List, Tuple, Optional
from server.entities.player import Player, PlayerState
from server.config import Config


@dataclass
class Rectangle:
    """Simple rectangle for collision detection"""
    x: float
    y: float
    width: float
    height: float

    @property
    def left(self) -> float:
        return self.x

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top(self) -> float:
        return self.y

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def intersects(self, other: 'Rectangle') -> bool:
        """Check if two rectangles overlap"""
        return (self.left < other.right and
                self.right > other.left and
                self.top < other.bottom and
                self.bottom > other.top)

    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is inside the rectangle"""
        return self.left <= x <= self.right and self.top <= y <= self.bottom


@dataclass
class Platform:
    """A platform players can stand on"""
    rect: Rectangle
    is_passthrough: bool = False  # Can jump through from below


@dataclass
class Obstacle:
    """An obstacle that blocks movement and provides cover"""
    rect: Rectangle
    is_destructible: bool = False
    hp: int = 100
    provides_cover: bool = True  # For cop mechanic


class PhysicsEngine:
    """Handles all physics calculations for the game"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.gravity = self.config.GRAVITY
        self.friction = self.config.FRICTION
        self.ground_y = self.config.GROUND_Y
        self.arena_width = self.config.ARENA_WIDTH
        self.arena_height = self.config.ARENA_HEIGHT

        # Player hitbox dimensions
        self.player_width = 50
        self.player_height = 80

        # Movement constants
        self.move_speed = 5.0
        self.jump_velocity = -15.0
        self.max_fall_speed = 20.0

    def get_player_hitbox(self, player: Player) -> Rectangle:
        """Get the collision rectangle for a player"""
        return Rectangle(
            x=player.x - self.player_width / 2,
            y=player.y - self.player_height,
            width=self.player_width,
            height=self.player_height
        )

    def update_player(self, player: Player, platforms: List[Platform] = None,
                      obstacles: List[Obstacle] = None, dt: float = 1/60):
        """Update player physics for one frame"""
        if player.state == PlayerState.DEAD:
            return

        platforms = platforms or []
        obstacles = obstacles or []

        # Process input into velocity
        self._process_movement_input(player)

        # Apply gravity
        if not player.on_ground:
            player.vy += self.gravity
            player.vy = min(player.vy, self.max_fall_speed)

        # Apply friction when on ground
        if player.on_ground:
            player.vx *= self.friction

        # Move and check collisions
        self._move_and_collide(player, platforms, obstacles)

        # Update facing direction
        if player.vx > 0.5:
            player.facing_right = True
        elif player.vx < -0.5:
            player.facing_right = False

        # Update player state
        player.update_state()

    def _process_movement_input(self, player: Player):
        """Convert input flags to velocity"""
        if player.state in [PlayerState.STUNNED, PlayerState.ATTACKING]:
            return

        # Horizontal movement
        move_speed = self.move_speed * player.stats.speed * player.speed_boost

        if player.input_left and not player.input_right:
            player.vx = -move_speed
        elif player.input_right and not player.input_left:
            player.vx = move_speed

        # Jump
        if player.input_jump and player.on_ground:
            player.vy = self.jump_velocity * player.stats.jump_power
            player.on_ground = False
            player.state = PlayerState.JUMPING

    def _move_and_collide(self, player: Player, platforms: List[Platform],
                          obstacles: List[Obstacle]):
        """Move player and handle collisions"""
        # Move horizontally
        player.x += player.vx
        self._check_horizontal_collisions(player, obstacles)

        # Clamp to arena bounds
        half_width = self.player_width / 2
        player.x = max(half_width, min(self.arena_width - half_width, player.x))

        # Move vertically
        player.y += player.vy
        self._check_vertical_collisions(player, platforms, obstacles)

        # Ground collision
        if player.y >= self.ground_y:
            player.y = self.ground_y
            player.vy = 0
            player.on_ground = True
            if player.state == PlayerState.JUMPING or player.state == PlayerState.FALLING:
                player.state = PlayerState.IDLE

    def _check_horizontal_collisions(self, player: Player, obstacles: List[Obstacle]):
        """Check and resolve horizontal collisions with obstacles"""
        player_rect = self.get_player_hitbox(player)

        for obstacle in obstacles:
            if player_rect.intersects(obstacle.rect):
                # Push player out of obstacle
                if player.vx > 0:  # Moving right
                    player.x = obstacle.rect.left - self.player_width / 2 - 1
                else:  # Moving left
                    player.x = obstacle.rect.right + self.player_width / 2 + 1
                player.vx = 0

    def _check_vertical_collisions(self, player: Player, platforms: List[Platform],
                                   obstacles: List[Obstacle]):
        """Check and resolve vertical collisions"""
        player_rect = self.get_player_hitbox(player)

        # Check obstacle collisions
        for obstacle in obstacles:
            if player_rect.intersects(obstacle.rect):
                if player.vy > 0:  # Falling
                    player.y = obstacle.rect.top
                    player.vy = 0
                    player.on_ground = True
                elif player.vy < 0:  # Jumping up
                    player.y = obstacle.rect.bottom + self.player_height
                    player.vy = 0

        # Check platform collisions
        for platform in platforms:
            if player_rect.intersects(platform.rect):
                # Only collide when falling and from above
                if player.vy > 0 and player_rect.bottom - player.vy <= platform.rect.top + 5:
                    if platform.is_passthrough and player.input_jump:
                        continue  # Allow dropping through
                    player.y = platform.rect.top
                    player.vy = 0
                    player.on_ground = True

    def apply_knockback(self, player: Player, force_x: float, force_y: float,
                        attacker_x: float = None):
        """Apply knockback force to a player"""
        # Scale knockback based on damage taken (more damage = more knockback)
        damage_percent = 1 - (player.hp / player.stats.max_hp)
        knockback_multiplier = 1 + damage_percent * 1.5

        # Determine direction if attacker position provided
        if attacker_x is not None:
            direction = 1 if player.x > attacker_x else -1
            force_x = abs(force_x) * direction

        player.vx += force_x * knockback_multiplier
        player.vy += force_y * knockback_multiplier
        player.on_ground = False

    def check_player_collision(self, player1: Player, player2: Player) -> bool:
        """Check if two players are colliding"""
        rect1 = self.get_player_hitbox(player1)
        rect2 = self.get_player_hitbox(player2)
        return rect1.intersects(rect2)

    def get_attack_hitbox(self, player: Player, attack_range: float) -> Rectangle:
        """Get the hitbox for a player's attack"""
        if player.facing_right:
            return Rectangle(
                x=player.x,
                y=player.y - self.player_height * 0.7,
                width=attack_range,
                height=self.player_height * 0.6
            )
        else:
            return Rectangle(
                x=player.x - attack_range,
                y=player.y - self.player_height * 0.7,
                width=attack_range,
                height=self.player_height * 0.6
            )

    def is_in_cover(self, player: Player, obstacles: List[Obstacle]) -> bool:
        """Check if player is behind an obstacle (for cop mechanic)"""
        player_rect = self.get_player_hitbox(player)

        for obstacle in obstacles:
            if not obstacle.provides_cover:
                continue

            # Check if player overlaps with obstacle horizontally
            if (player_rect.left < obstacle.rect.right and
                    player_rect.right > obstacle.rect.left):
                return True

        return False

    def get_distance(self, player1: Player, player2: Player) -> float:
        """Get distance between two players"""
        dx = player1.x - player2.x
        dy = player1.y - player2.y
        return (dx**2 + dy**2) ** 0.5

    def is_in_range(self, attacker: Player, target: Player, range_val: float) -> bool:
        """Check if target is within attack range"""
        attack_hitbox = self.get_attack_hitbox(attacker, range_val)
        target_hitbox = self.get_player_hitbox(target)
        return attack_hitbox.intersects(target_hitbox)
