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

        # Movement constants (SSB-style)
        self.walk_speed = self.config.WALK_SPEED
        self.run_speed = self.config.RUN_SPEED
        self.initial_dash_speed = self.config.INITIAL_DASH_SPEED
        self.initial_dash_frames = self.config.INITIAL_DASH_FRAMES
        self.turnaround_frames = self.config.TURNAROUND_FRAMES
        self.air_drift_accel = self.config.AIR_DRIFT_ACCEL
        self.air_drift_max = self.config.AIR_DRIFT_MAX
        self.fast_fall_multiplier = self.config.FAST_FALL_MULTIPLIER
        self.jump_squat_frames = self.config.JUMP_SQUAT_FRAMES
        self.short_hop_multiplier = self.config.SHORT_HOP_MULTIPLIER
        self.max_air_jumps = self.config.MAX_AIR_JUMPS

        # Legacy compatibility
        self.move_speed = self.run_speed
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

        # Apply gravity (with fast fall support)
        if not player.on_ground:
            player.vy += self.gravity
            max_fall = self.max_fall_speed
            if player.fast_falling:
                max_fall *= self.fast_fall_multiplier
            player.vy = min(player.vy, max_fall)

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
        """Convert input flags to velocity - SSB-style movement system"""
        # States that prevent movement input
        locked_states = [
            PlayerState.STUNNED, PlayerState.ATTACKING, PlayerState.TUMBLING,
            PlayerState.SPOT_DODGING, PlayerState.DEAD
        ]
        if player.state in locked_states:
            return

        # Handle dodge states separately
        if player.state == PlayerState.AIR_DODGING:
            self._process_air_dodge(player)
            return

        speed_mult = player.stats.speed * player.speed_boost

        if player.on_ground:
            self._process_ground_movement(player, speed_mult)
        else:
            self._process_air_movement(player, speed_mult)

        # Store previous input for next frame
        player.prev_input_left = player.input_left
        player.prev_input_right = player.input_right

    def _process_ground_movement(self, player: Player, speed_mult: float):
        """Handle ground movement: walk, dash, run, crouch, turnaround"""
        # Check for crouch
        if player.input_down and player.state not in [PlayerState.DASHING, PlayerState.TURNAROUND]:
            player.state = PlayerState.CROUCHING
            player.vx *= 0.5  # Slow down while crouching
            return

        # Handle jump squat (pre-jump)
        if player.state == PlayerState.JUMP_SQUAT:
            player.jump_squat_frame += 1
            if player.jump_squat_frame >= self.jump_squat_frames:
                self._execute_jump(player)
            elif not player.input_jump:
                player.is_short_hop = True
            return

        # Start jump squat on jump input
        if player.input_jump:
            player.state = PlayerState.JUMP_SQUAT
            player.jump_squat_frame = 0
            player.is_short_hop = False
            return

        # Handle turnaround state
        if player.state == PlayerState.TURNAROUND:
            player.turnaround_frame += 1
            player.vx *= 0.8  # Slow down during turnaround
            if player.turnaround_frame >= self.turnaround_frames:
                player.state = PlayerState.IDLE
            return

        # Handle initial dash state
        if player.state == PlayerState.DASHING:
            player.dash_frame += 1
            if player.dash_frame >= self.initial_dash_frames:
                # Transition to run if still holding direction
                if (player.facing_right and player.input_right) or \
                   (not player.facing_right and player.input_left):
                    player.state = PlayerState.RUNNING
                else:
                    player.state = PlayerState.IDLE
            else:
                # Locked in dash direction
                dash_speed = self.initial_dash_speed * speed_mult
                player.vx = dash_speed if player.facing_right else -dash_speed
            return

        # Handle running state
        if player.state == PlayerState.RUNNING:
            run_speed = self.run_speed * speed_mult
            if player.input_right and not player.input_left:
                if not player.facing_right:
                    # Turnaround from run
                    player.state = PlayerState.TURNAROUND
                    player.turnaround_frame = 0
                    player.facing_right = True
                else:
                    player.vx = run_speed
            elif player.input_left and not player.input_right:
                if player.facing_right:
                    # Turnaround from run
                    player.state = PlayerState.TURNAROUND
                    player.turnaround_frame = 0
                    player.facing_right = False
                else:
                    player.vx = -run_speed
            else:
                # No input, stop running
                player.state = PlayerState.IDLE
            return

        # Idle/Walking state - check for new dash or walk
        want_left = player.input_left and not player.input_right
        want_right = player.input_right and not player.input_left

        if want_right:
            # Check if this is a new direction tap (dash) or held (walk)
            if not player.prev_input_right:
                # New tap - start dash
                player.state = PlayerState.DASHING
                player.dash_frame = 0
                player.facing_right = True
                player.vx = self.initial_dash_speed * speed_mult
            else:
                # Held - walk
                player.state = PlayerState.WALKING
                player.vx = self.walk_speed * speed_mult
        elif want_left:
            if not player.prev_input_left:
                # New tap - start dash
                player.state = PlayerState.DASHING
                player.dash_frame = 0
                player.facing_right = False
                player.vx = -self.initial_dash_speed * speed_mult
            else:
                # Held - walk
                player.state = PlayerState.WALKING
                player.vx = -self.walk_speed * speed_mult
        else:
            # No horizontal input
            if player.state != PlayerState.CROUCHING:
                player.state = PlayerState.IDLE

    def _process_air_movement(self, player: Player, speed_mult: float):
        """Handle air movement: drift, fast fall, air jumps"""
        # Fast fall: tap down at apex or while falling
        if player.input_down and player.vy >= 0 and not player.fast_falling:
            player.fast_falling = True

        # Air drift (accelerate toward input direction, capped at max)
        if player.input_right and not player.input_left:
            player.vx = min(player.vx + self.air_drift_accel * speed_mult,
                           self.air_drift_max * speed_mult)
            player.facing_right = True
        elif player.input_left and not player.input_right:
            player.vx = max(player.vx - self.air_drift_accel * speed_mult,
                           -self.air_drift_max * speed_mult)
            player.facing_right = False

        # Air jump
        if player.input_jump and not player.prev_input_jump:
            if player.air_jumps_used < self.max_air_jumps:
                jump_power = self.jump_velocity * player.stats.jump_power
                player.vy = jump_power
                player.air_jumps_used += 1
                player.fast_falling = False
                player.state = PlayerState.JUMPING

        # Track previous jump input
        player.prev_input_jump = player.input_jump

    def _execute_jump(self, player: Player):
        """Execute the actual jump after jump squat"""
        jump_power = self.jump_velocity * player.stats.jump_power
        if player.is_short_hop:
            jump_power *= self.short_hop_multiplier
        player.vy = jump_power
        player.on_ground = False
        player.state = PlayerState.JUMPING
        player.air_jumps_used = 0
        player.fast_falling = False

    def _process_air_dodge(self, player: Player):
        """Process air dodge movement"""
        player.dodge_frame += 1
        # Move in dodge direction
        player.vx = player.dodge_direction[0] * 8
        player.vy = player.dodge_direction[1] * 8

        if player.dodge_frame >= self.config.AIR_DODGE_FRAMES:
            player.state = PlayerState.FALLING
            player.dodge_frame = 0

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
            player.air_jumps_used = 0
            player.fast_falling = False
            if player.state in [PlayerState.JUMPING, PlayerState.FALLING,
                               PlayerState.AIR_DODGING, PlayerState.TUMBLING]:
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
                    # Allow dropping through passthrough platforms with down input
                    if platform.is_passthrough and player.input_down:
                        continue
                    player.y = platform.rect.top
                    player.vy = 0
                    player.on_ground = True
                    player.air_jumps_used = 0
                    player.fast_falling = False

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

    # ========== PARRY AND DODGE SYSTEM ==========

    def process_dodge_input(self, player: Player) -> bool:
        """Process dodge/parry input. Returns True if dodge started."""
        import time as time_module

        if player.state == PlayerState.DEAD:
            return False

        # Check for dodge input
        if not player.input_dodge:
            return False

        # Refresh stale count after 2 seconds of no dodging
        if time_module.time() - player.last_dodge_time > 2.0:
            player.dodge_stale_count = 0

        player.last_dodge_time = time_module.time()

        if player.on_ground:
            # Ground: Spot dodge or Parry
            return self._start_spot_dodge(player)
        else:
            # Air: Directional air dodge
            return self._start_air_dodge(player)

    def _start_spot_dodge(self, player: Player) -> bool:
        """Start a spot dodge on the ground"""
        if player.state in [PlayerState.ATTACKING, PlayerState.STUNNED,
                           PlayerState.SPOT_DODGING, PlayerState.PARRYING]:
            return False

        player.state = PlayerState.SPOT_DODGING
        player.dodge_frame = 0
        player.parry_frame = 0
        player.parry_success = False
        player.dodge_stale_count = min(player.dodge_stale_count + 1,
                                       self.config.DODGE_STALE_MAX)
        return True

    def _start_air_dodge(self, player: Player) -> bool:
        """Start a directional air dodge"""
        if player.state in [PlayerState.ATTACKING, PlayerState.STUNNED,
                           PlayerState.AIR_DODGING]:
            return False

        # Determine direction (8-way based on input)
        dx = 0
        dy = 0
        if player.input_right and not player.input_left:
            dx = 1
        elif player.input_left and not player.input_right:
            dx = -1
        if player.input_jump:  # Up
            dy = -1
        elif player.input_down:  # Down
            dy = 1

        # Normalize diagonal
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        player.dodge_direction = (dx, dy)
        player.state = PlayerState.AIR_DODGING
        player.dodge_frame = 0
        player.dodge_stale_count = min(player.dodge_stale_count + 1,
                                       self.config.DODGE_STALE_MAX)
        return True

    def update_dodge_state(self, player: Player):
        """Update dodge/parry state each frame"""
        if player.state == PlayerState.SPOT_DODGING:
            player.dodge_frame += 1
            player.parry_frame += 1

            if player.dodge_frame >= self.config.SPOT_DODGE_FRAMES:
                player.state = PlayerState.IDLE
                player.dodge_frame = 0
                player.parry_frame = 0

        elif player.state == PlayerState.AIR_DODGING:
            # Air dodge movement handled in _process_air_dodge
            pass

    def is_invincible(self, player: Player) -> bool:
        """Check if player is currently invincible (i-frames)"""
        import time as time_module

        # Regular invincibility (respawn, power-up)
        if time_module.time() < player.invincible_until:
            return True

        # Spot dodge i-frames (with stale reduction)
        if player.state == PlayerState.SPOT_DODGING:
            iframe_start, iframe_end = self.config.SPOT_DODGE_IFRAMES
            # Apply stale reduction
            stale_reduction = player.dodge_stale_count * self.config.DODGE_STALE_REDUCTION
            effective_end = iframe_end - int(iframe_end * stale_reduction)
            if iframe_start <= player.dodge_frame <= effective_end:
                return True

        # Air dodge i-frames (with stale reduction)
        if player.state == PlayerState.AIR_DODGING:
            iframe_start, iframe_end = self.config.AIR_DODGE_IFRAMES
            stale_reduction = player.dodge_stale_count * self.config.DODGE_STALE_REDUCTION
            effective_end = iframe_end - int(iframe_end * stale_reduction)
            if iframe_start <= player.dodge_frame <= effective_end:
                return True

        return False

    def is_in_parry_window(self, player: Player) -> bool:
        """Check if player is in the frame-perfect parry window"""
        if player.state != PlayerState.SPOT_DODGING:
            return False
        return player.parry_frame <= self.config.PARRY_WINDOW

    def trigger_parry_success(self, player: Player, attacker: Player):
        """Called when a parry successfully blocks an attack"""
        player.parry_success = True
        # Stun the attacker briefly (parry punish window)
        attacker.stun(0.5)  # Half second stun for parry punish

    # ========== LEDGE SYSTEM ==========

    def check_ledge_grab(self, player: Player, platforms: List[Platform]) -> bool:
        """Check if player can grab a ledge"""
        # Can only grab ledge while in air and moving toward it
        if player.on_ground:
            return False
        if player.state in [PlayerState.DEAD, PlayerState.LEDGE_HANG]:
            return False

        # Must be falling or moving downward-ish
        if player.vy < 0:  # Moving up, can't grab
            return False

        player_rect = self.get_player_hitbox(player)

        for platform in platforms:
            # Check left ledge
            left_ledge_x = platform.rect.left
            left_ledge_y = platform.rect.top

            # Check right ledge
            right_ledge_x = platform.rect.right
            right_ledge_y = platform.rect.top

            # Ledge grab zone: within 20px of ledge corner, player must be outside platform
            ledge_grab_range = 25
            vertical_range = 30

            # Check left ledge (player approaching from left)
            if player.facing_right and player.input_right:  # Moving toward ledge
                if (abs(player_rect.right - left_ledge_x) < ledge_grab_range and
                    abs(player_rect.top - left_ledge_y) < vertical_range and
                    player_rect.left < left_ledge_x):  # Player is to the left of platform
                    self._grab_ledge(player, left_ledge_x, left_ledge_y, is_left=True)
                    return True

            # Check right ledge (player approaching from right)
            if not player.facing_right and player.input_left:  # Moving toward ledge
                if (abs(player_rect.left - right_ledge_x) < ledge_grab_range and
                    abs(player_rect.top - right_ledge_y) < vertical_range and
                    player_rect.right > right_ledge_x):  # Player is to the right of platform
                    self._grab_ledge(player, right_ledge_x, right_ledge_y, is_left=False)
                    return True

        return False

    def _grab_ledge(self, player: Player, ledge_x: float, ledge_y: float, is_left: bool):
        """Snap player to ledge"""
        import time as time_module

        # Position player at ledge
        offset = -25 if is_left else 25
        player.x = ledge_x + offset
        player.y = ledge_y + 50  # Hang below ledge

        player.vx = 0
        player.vy = 0
        player.on_ground = False
        player.state = PlayerState.LEDGE_HANG
        player.facing_right = is_left  # Face toward stage

        # Ledge invincibility (60 frames = 1 second)
        player.invincible_until = time_module.time() + 1.0

        # Reset air resources
        player.air_jumps_used = 0
        player.fast_falling = False

    def process_ledge_options(self, player: Player):
        """Handle input while hanging on ledge"""
        if player.state != PlayerState.LEDGE_HANG:
            return

        # Neutral getup (no direction + attack or special)
        if player.input_attack and not player.input_left and not player.input_right:
            self._ledge_getup(player)
            return

        # Roll (toward stage + dodge)
        if player.input_dodge:
            if (player.facing_right and player.input_right) or \
               (not player.facing_right and player.input_left):
                self._ledge_roll(player)
                return

        # Jump (up or jump button)
        if player.input_jump:
            self._ledge_jump(player)
            return

        # Attack (attack button)
        if player.input_attack:
            self._ledge_attack(player)
            return

        # Drop (down or away from stage)
        if player.input_down:
            self._ledge_drop(player)
            return
        if (player.facing_right and player.input_left) or \
           (not player.facing_right and player.input_right):
            self._ledge_drop(player)
            return

    def _ledge_getup(self, player: Player):
        """Normal getup from ledge"""
        # Move onto stage
        offset = 60 if player.facing_right else -60
        player.x += offset
        player.y -= self.player_height
        player.on_ground = True
        player.state = PlayerState.IDLE

    def _ledge_roll(self, player: Player):
        """Roll getup from ledge (invincible)"""
        import time as time_module

        offset = 100 if player.facing_right else -100
        player.x += offset
        player.y -= self.player_height
        player.on_ground = True
        player.state = PlayerState.SPOT_DODGING  # Use dodge state for i-frames
        player.dodge_frame = 0
        player.invincible_until = time_module.time() + 0.3

    def _ledge_jump(self, player: Player):
        """Jump from ledge"""
        player.vy = self.jump_velocity * player.stats.jump_power
        player.on_ground = False
        player.state = PlayerState.JUMPING
        # Move slightly toward stage
        offset = 30 if player.facing_right else -30
        player.x += offset
        player.y -= 20

    def _ledge_attack(self, player: Player):
        """Attack getup from ledge"""
        # Pop up onto stage and start attack
        offset = 50 if player.facing_right else -50
        player.x += offset
        player.y -= self.player_height
        player.on_ground = True
        player.state = PlayerState.IDLE
        player.input_attack = True  # Will trigger attack next frame

    def _ledge_drop(self, player: Player):
        """Drop from ledge"""
        player.state = PlayerState.FALLING
        player.vy = 2  # Small downward velocity
        # Move away from stage slightly
        offset = -20 if player.facing_right else 20
        player.x += offset
