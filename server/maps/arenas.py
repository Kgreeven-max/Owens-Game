"""
Arena Brawl - SSB-Style Stage Definitions
5 unique themed stages with floating platforms
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import math
import time


@dataclass
class Platform:
    """A platform in the stage"""
    id: str
    x: float
    y: float
    width: float
    height: float = 20.0
    platform_type: str = "solid"  # solid, passthrough, moving
    theme: str = "grass"  # grass, tech, rock, cloud, wood
    move_pattern: Optional[str] = None  # horizontal, vertical, circular
    move_range: float = 0.0
    move_speed: float = 0.0
    # Runtime state for moving platforms
    _initial_x: float = field(default=0.0, repr=False)
    _initial_y: float = field(default=0.0, repr=False)
    _move_offset: float = field(default=0.0, repr=False)

    def __post_init__(self):
        self._initial_x = self.x
        self._initial_y = self.y

    def update(self, current_time: float):
        """Update moving platform position"""
        if self.move_pattern and self.move_speed > 0:
            cycle = math.sin(current_time * self.move_speed)

            if self.move_pattern == "horizontal":
                self.x = self._initial_x + cycle * self.move_range
            elif self.move_pattern == "vertical":
                self.y = self._initial_y + cycle * self.move_range
            elif self.move_pattern == "circular":
                self.x = self._initial_x + math.cos(current_time * self.move_speed) * self.move_range
                self.y = self._initial_y + math.sin(current_time * self.move_speed) * self.move_range

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'platform_type': self.platform_type,
            'theme': self.theme,
            'move_pattern': self.move_pattern,
            'is_moving': self.move_pattern is not None
        }


@dataclass
class LegacyObstacle:
    """Legacy obstacle wrapper for physics compatibility"""
    id: str
    x: float
    y: float
    width: float
    height: float
    obstacle_type: str = "platform"
    color: str = "#666666"
    is_destroyed: bool = False
    is_destructible: bool = False
    hp: int = 100
    provides_cover: bool = False

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'type': self.obstacle_type,
            'color': self.color,
            'is_destroyed': self.is_destroyed,
            'is_destructible': self.is_destructible,
            'provides_cover': self.provides_cover
        }


@dataclass
class BlastZones:
    """Defines the KO boundaries for a stage"""
    top: float = -200       # Above stage - die when Y < this
    bottom: float = 920     # Below stage - die when Y > this
    left: float = -300      # Left of stage - die when X < this
    right: float = 1580     # Right of stage - die when X > this

    def is_player_out(self, x: float, y: float) -> Optional[str]:
        """Check if a player position is in a blast zone, return direction or None"""
        if y < self.top:
            return "top"
        if y > self.bottom:
            return "bottom"
        if x < self.left:
            return "left"
        if x > self.right:
            return "right"
        return None

    def to_dict(self) -> dict:
        return {
            'top': self.top,
            'bottom': self.bottom,
            'left': self.left,
            'right': self.right
        }


@dataclass
class Stage:
    """Defines an SSB-style stage"""
    name: str
    display_name: str
    width: int
    height: int
    theme: str  # battlefield, space, volcano, sky, forest
    background_colors: List[str]  # Gradient colors for sky
    platforms: List[Platform] = field(default_factory=list)
    spawn_points: List[Tuple[float, float]] = field(default_factory=list)
    # Blast zones for KO boundaries
    blast_zones: BlastZones = field(default_factory=BlastZones)
    # Stage-specific properties
    has_hazard: bool = False
    hazard_type: Optional[str] = None  # lava, void, wind, lightning, ice
    hazard_y: float = 720  # Y position of hazard
    hazards_enabled: bool = True  # Toggle for competitive mode
    # Stage category
    is_competitive: bool = True  # Legal in competitive play
    # Music track
    music: str = "battle_theme"
    # Legacy compatibility cache
    _obstacles_cache: List[LegacyObstacle] = field(default_factory=list, repr=False)

    @property
    def obstacles(self) -> List[LegacyObstacle]:
        """Legacy obstacles property for physics engine compatibility"""
        # Update obstacle positions from platforms (for moving platforms)
        if not self._obstacles_cache or len(self._obstacles_cache) != len(self.platforms):
            self._obstacles_cache = []
            colors = {
                'grass': '#4A7C23',
                'tech': '#2E4A6E',
                'rock': '#6B4423',
                'cloud': '#FFFFFF',
                'wood': '#8B5A2B'
            }
            for p in self.platforms:
                self._obstacles_cache.append(LegacyObstacle(
                    id=p.id,
                    x=p.x,
                    y=p.y,
                    width=p.width,
                    height=p.height,
                    obstacle_type='platform',
                    color=colors.get(p.theme, '#666666')
                ))
        else:
            # Update positions for moving platforms
            for i, p in enumerate(self.platforms):
                self._obstacles_cache[i].x = p.x
                self._obstacles_cache[i].y = p.y
        return self._obstacles_cache

    def update(self, current_time: float):
        """Update all moving platforms"""
        for platform in self.platforms:
            platform.update(current_time)

    def to_dict(self) -> dict:
        """Serialize for network"""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'width': self.width,
            'height': self.height,
            'theme': self.theme,
            'background_colors': self.background_colors,
            'platforms': [p.to_dict() for p in self.platforms],
            'spawn_points': self.spawn_points,
            'blast_zones': self.blast_zones.to_dict(),
            'has_hazard': self.has_hazard,
            'hazard_type': self.hazard_type,
            'hazard_y': self.hazard_y,
            'hazards_enabled': self.hazards_enabled,
            'is_competitive': self.is_competitive,
            'music': self.music,
            # Legacy compatibility
            'ground_y': 720,
            'background_color': self.background_colors[0] if self.background_colors else '#2C3E50',
            'obstacles': [self._platform_to_obstacle(p) for p in self.platforms]
        }

    def _platform_to_obstacle(self, platform: Platform) -> dict:
        """Convert platform to legacy obstacle format for physics"""
        return {
            'id': platform.id,
            'x': platform.x,
            'y': platform.y,
            'width': platform.width,
            'height': platform.height,
            'type': 'platform',
            'color': self._get_platform_color(platform.theme),
            'is_destroyed': False,
            'is_destructible': False,
            'provides_cover': False
        }

    def _get_platform_color(self, theme: str) -> str:
        colors = {
            'grass': '#4A7C23',
            'tech': '#2E4A6E',
            'rock': '#6B4423',
            'cloud': '#FFFFFF',
            'wood': '#8B5A2B'
        }
        return colors.get(theme, '#666666')


def create_battlefield_stage() -> Stage:
    """Battlefield - Balanced stage with 3 floating platforms (Competitive)"""
    stage = Stage(
        name="battlefield",
        display_name="Battlefield",
        width=1280,
        height=720,
        theme="battlefield",
        background_colors=["#1a0a2e", "#4a1a6e", "#8b3a9e", "#d4649a"],  # Purple sunset
        spawn_points=[
            (320, 520),
            (960, 520),
            (480, 520),
            (800, 520)
        ],
        blast_zones=BlastZones(top=-200, bottom=920, left=-300, right=1580),
        is_competitive=True,
        music="battlefield_theme"
    )

    # Main platform (880px wide, centered)
    main_x = (1280 - 880) / 2  # 200
    stage.platforms = [
        Platform(
            id="main",
            x=main_x,
            y=540,
            width=880,
            height=40,
            platform_type="solid",
            theme="grass"
        ),
        # Left floating platform
        Platform(
            id="float_left",
            x=280,
            y=380,
            width=180,
            height=20,
            platform_type="passthrough",
            theme="grass"
        ),
        # Right floating platform
        Platform(
            id="float_right",
            x=820,
            y=380,
            width=180,
            height=20,
            platform_type="passthrough",
            theme="grass"
        ),
        # Top center platform
        Platform(
            id="float_top",
            x=550,
            y=260,
            width=180,
            height=20,
            platform_type="passthrough",
            theme="grass"
        )
    ]

    return stage


def create_final_destination_stage() -> Stage:
    """Final Destination - Competitive stage with single platform (Competitive)"""
    stage = Stage(
        name="final_destination",
        display_name="Final Destination",
        width=1280,
        height=720,
        theme="space",
        background_colors=["#0a0a1a", "#1a1a3a", "#0a2a4a"],  # Deep space
        spawn_points=[
            (280, 480),
            (1000, 480),
            (440, 480),
            (840, 480)
        ],
        blast_zones=BlastZones(top=-250, bottom=920, left=-350, right=1630),
        is_competitive=True,
        music="final_destination_theme"
    )

    # Single main platform (920px wide, centered)
    main_x = (1280 - 920) / 2  # 180
    stage.platforms = [
        Platform(
            id="main",
            x=main_x,
            y=500,
            width=920,
            height=50,
            platform_type="solid",
            theme="tech"
        )
    ]

    return stage


def create_volcanic_fury_stage() -> Stage:
    """Volcanic Fury - Hazard stage with lava (Hazard Stage)"""
    stage = Stage(
        name="volcanic_fury",
        display_name="Volcanic Fury",
        width=1280,
        height=720,
        theme="volcano",
        background_colors=["#1a0a0a", "#4a1a0a", "#8b2a0a", "#d44a0a"],  # Orange/red
        spawn_points=[
            (340, 480),
            (940, 480),
            (500, 480),
            (780, 480)
        ],
        blast_zones=BlastZones(top=-180, bottom=750, left=-280, right=1560),  # Lower bottom for lava
        has_hazard=True,
        hazard_type="lava",
        hazard_y=680,
        hazards_enabled=True,
        is_competitive=False,  # Hazard stage
        music="volcanic_fury_theme"
    )

    # Main platform (780px wide, centered)
    main_x = (1280 - 780) / 2  # 250
    stage.platforms = [
        Platform(
            id="main",
            x=main_x,
            y=500,
            width=780,
            height=40,
            platform_type="solid",
            theme="rock"
        ),
        # Left moving platform (vertical)
        Platform(
            id="float_left",
            x=180,
            y=400,
            width=140,
            height=20,
            platform_type="moving",
            theme="rock",
            move_pattern="vertical",
            move_range=80,
            move_speed=1.2
        ),
        # Right moving platform (vertical)
        Platform(
            id="float_right",
            x=960,
            y=380,
            width=140,
            height=20,
            platform_type="moving",
            theme="rock",
            move_pattern="vertical",
            move_range=80,
            move_speed=1.0
        ),
        # Center high platform (static)
        Platform(
            id="float_center",
            x=550,
            y=300,
            width=180,
            height=20,
            platform_type="passthrough",
            theme="rock"
        )
    ]

    return stage


def create_sky_citadel_stage() -> Stage:
    """Sky Citadel - Aerial stage with many platforms (Competitive)"""
    stage = Stage(
        name="sky_citadel",
        display_name="Sky Citadel",
        width=1280,
        height=720,
        theme="sky",
        background_colors=["#87CEEB", "#B0E0E6", "#E0F6FF", "#FFFFFF"],  # Bright blue sky
        spawn_points=[
            (400, 520),
            (880, 520),
            (540, 520),
            (740, 520)
        ],
        blast_zones=BlastZones(top=-220, bottom=950, left=-320, right=1600),
        is_competitive=True,
        music="sky_citadel_theme"
    )

    # Smaller main platform (680px wide, centered)
    main_x = (1280 - 680) / 2  # 300
    stage.platforms = [
        Platform(
            id="main",
            x=main_x,
            y=540,
            width=680,
            height=35,
            platform_type="solid",
            theme="cloud"
        ),
        # Lower left cloud
        Platform(
            id="float_lower_left",
            x=120,
            y=460,
            width=160,
            height=20,
            platform_type="passthrough",
            theme="cloud"
        ),
        # Lower right cloud
        Platform(
            id="float_lower_right",
            x=1000,
            y=460,
            width=160,
            height=20,
            platform_type="passthrough",
            theme="cloud"
        ),
        # Mid left moving platform (horizontal)
        Platform(
            id="float_mid_left",
            x=200,
            y=340,
            width=140,
            height=20,
            platform_type="moving",
            theme="cloud",
            move_pattern="horizontal",
            move_range=100,
            move_speed=0.8
        ),
        # Mid right moving platform (horizontal)
        Platform(
            id="float_mid_right",
            x=940,
            y=340,
            width=140,
            height=20,
            platform_type="moving",
            theme="cloud",
            move_pattern="horizontal",
            move_range=100,
            move_speed=0.9
        ),
        # Top center platform (highest)
        Platform(
            id="float_top",
            x=540,
            y=200,
            width=200,
            height=20,
            platform_type="passthrough",
            theme="cloud"
        )
    ]

    return stage


def create_whisperwood_stage() -> Stage:
    """Whisperwood - Technical forest stage (Competitive)"""
    stage = Stage(
        name="whisperwood",
        display_name="Whisperwood",
        width=1280,
        height=720,
        theme="forest",
        background_colors=["#0a1a0a", "#1a2a1a", "#2a3a2a", "#1a3a2a"],  # Dark green
        spawn_points=[
            (300, 520),
            (980, 520),
            (480, 520),
            (800, 520)
        ],
        blast_zones=BlastZones(top=-200, bottom=920, left=-300, right=1580),
        is_competitive=True,
        music="whisperwood_theme"
    )

    # Main platform (840px wide, centered)
    main_x = (1280 - 840) / 2  # 220
    stage.platforms = [
        Platform(
            id="main",
            x=main_x,
            y=540,
            width=840,
            height=40,
            platform_type="solid",
            theme="wood"
        ),
        # Left branch
        Platform(
            id="branch_left",
            x=140,
            y=420,
            width=160,
            height=18,
            platform_type="passthrough",
            theme="wood"
        ),
        # Right branch
        Platform(
            id="branch_right",
            x=980,
            y=420,
            width=160,
            height=18,
            platform_type="passthrough",
            theme="wood"
        ),
        # Central tree trunk platforms (stacked)
        Platform(
            id="tree_mid",
            x=560,
            y=380,
            width=160,
            height=20,
            platform_type="passthrough",
            theme="wood"
        ),
        Platform(
            id="tree_top",
            x=540,
            y=250,
            width=200,
            height=20,
            platform_type="passthrough",
            theme="wood"
        ),
        # Lower side platforms
        Platform(
            id="moss_left",
            x=320,
            y=460,
            width=120,
            height=16,
            platform_type="passthrough",
            theme="wood"
        ),
        Platform(
            id="moss_right",
            x=840,
            y=460,
            width=120,
            height=16,
            platform_type="passthrough",
            theme="wood"
        )
    ]

    return stage


# ==================== NEW STAGES ====================

def create_dojo_stage() -> Stage:
    """Dojo - Traditional Japanese temple (Competitive)"""
    stage = Stage(
        name="dojo",
        display_name="Dojo",
        width=1280,
        height=720,
        theme="dojo",
        background_colors=["#2a1a0a", "#4a2a1a", "#6a3a2a", "#8a4a3a"],  # Warm wood tones
        spawn_points=[
            (350, 520),
            (930, 520),
            (500, 520),
            (780, 520)
        ],
        blast_zones=BlastZones(top=-200, bottom=920, left=-280, right=1560),
        is_competitive=True,
        music="dojo_theme"
    )

    # Main platform (900px wide, centered)
    main_x = (1280 - 900) / 2  # 190
    stage.platforms = [
        Platform(
            id="main",
            x=main_x,
            y=540,
            width=900,
            height=35,
            platform_type="solid",
            theme="wood"
        ),
        # Single center platform (like Smashville)
        Platform(
            id="center",
            x=540,
            y=380,
            width=200,
            height=20,
            platform_type="passthrough",
            theme="wood"
        )
    ]

    return stage


def create_thunderstorm_stage() -> Stage:
    """Thunderstorm - Hazard stage with lightning strikes (Hazard Stage)"""
    stage = Stage(
        name="thunderstorm",
        display_name="Thunderstorm",
        width=1280,
        height=720,
        theme="storm",
        background_colors=["#1a1a2a", "#2a2a4a", "#3a3a5a", "#4a4a6a"],  # Dark stormy
        spawn_points=[
            (320, 520),
            (960, 520),
            (480, 520),
            (800, 520)
        ],
        blast_zones=BlastZones(top=-200, bottom=920, left=-300, right=1580),
        has_hazard=True,
        hazard_type="lightning",  # Random lightning strikes
        hazard_y=0,  # Lightning strikes from top
        hazards_enabled=True,
        is_competitive=False,
        music="thunderstorm_theme"
    )

    # Main platform
    main_x = (1280 - 850) / 2
    stage.platforms = [
        Platform(
            id="main",
            x=main_x,
            y=540,
            width=850,
            height=40,
            platform_type="solid",
            theme="rock"
        ),
        # Moving platforms that act as lightning rods
        Platform(
            id="lightning_rod_left",
            x=250,
            y=350,
            width=150,
            height=20,
            platform_type="moving",
            theme="rock",
            move_pattern="horizontal",
            move_range=80,
            move_speed=0.7
        ),
        Platform(
            id="lightning_rod_right",
            x=880,
            y=350,
            width=150,
            height=20,
            platform_type="moving",
            theme="rock",
            move_pattern="horizontal",
            move_range=80,
            move_speed=0.9
        ),
        # High center platform
        Platform(
            id="high_center",
            x=540,
            y=240,
            width=200,
            height=20,
            platform_type="passthrough",
            theme="rock"
        )
    ]

    return stage


def create_frozen_lake_stage() -> Stage:
    """Frozen Lake - Hazard stage with ice (Hazard Stage)"""
    stage = Stage(
        name="frozen_lake",
        display_name="Frozen Lake",
        width=1280,
        height=720,
        theme="ice",
        background_colors=["#e0f0ff", "#c0e0ff", "#a0d0ff", "#80c0ff"],  # Icy blue
        spawn_points=[
            (350, 480),
            (930, 480),
            (500, 480),
            (780, 480)
        ],
        blast_zones=BlastZones(top=-200, bottom=850, left=-300, right=1580),  # Ice breaks at bottom
        has_hazard=True,
        hazard_type="ice",  # Slippery ground, ice can break
        hazard_y=700,
        hazards_enabled=True,
        is_competitive=False,
        music="frozen_lake_theme"
    )

    # Slippery main platform (the frozen lake)
    main_x = (1280 - 950) / 2
    stage.platforms = [
        Platform(
            id="main",
            x=main_x,
            y=500,
            width=950,
            height=30,
            platform_type="solid",
            theme="cloud"  # White/icy appearance
        ),
        # Ice platforms that can break
        Platform(
            id="ice_left",
            x=200,
            y=380,
            width=140,
            height=18,
            platform_type="passthrough",
            theme="cloud"
        ),
        Platform(
            id="ice_right",
            x=940,
            y=380,
            width=140,
            height=18,
            platform_type="passthrough",
            theme="cloud"
        ),
        Platform(
            id="ice_center",
            x=560,
            y=300,
            width=160,
            height=18,
            platform_type="passthrough",
            theme="cloud"
        )
    ]

    return stage


def create_windmill_stage() -> Stage:
    """Windmill - Hazard stage with rotating platforms (Hazard Stage)"""
    stage = Stage(
        name="windmill",
        display_name="Windmill",
        width=1280,
        height=720,
        theme="windmill",
        background_colors=["#4a7a3a", "#6a9a5a", "#8aba7a", "#aada9a"],  # Green countryside
        spawn_points=[
            (300, 520),
            (980, 520),
            (450, 520),
            (830, 520)
        ],
        blast_zones=BlastZones(top=-220, bottom=920, left=-350, right=1630),
        has_hazard=True,
        hazard_type="wind",  # Wind gusts alter knockback
        hazard_y=0,
        hazards_enabled=True,
        is_competitive=False,
        music="windmill_theme"
    )

    # Main grassy platform
    main_x = (1280 - 800) / 2
    stage.platforms = [
        Platform(
            id="main",
            x=main_x,
            y=540,
            width=800,
            height=40,
            platform_type="solid",
            theme="grass"
        ),
        # Rotating windmill blade platforms
        Platform(
            id="blade_1",
            x=400,
            y=340,
            width=120,
            height=20,
            platform_type="moving",
            theme="wood",
            move_pattern="circular",
            move_range=100,
            move_speed=0.5
        ),
        Platform(
            id="blade_2",
            x=760,
            y=340,
            width=120,
            height=20,
            platform_type="moving",
            theme="wood",
            move_pattern="circular",
            move_range=100,
            move_speed=-0.5  # Opposite direction
        ),
        # Static high platform
        Platform(
            id="top",
            x=540,
            y=200,
            width=200,
            height=20,
            platform_type="passthrough",
            theme="wood"
        )
    ]

    return stage


def create_training_room_stage() -> Stage:
    """Training Room - Practice stage with no hazards"""
    stage = Stage(
        name="training_room",
        display_name="Training Room",
        width=1280,
        height=720,
        theme="training",
        background_colors=["#2a2a2a", "#3a3a3a", "#4a4a4a", "#5a5a5a"],  # Grid background
        spawn_points=[
            (400, 520),
            (880, 520),
            (540, 520),
            (740, 520)
        ],
        blast_zones=BlastZones(top=-300, bottom=1000, left=-400, right=1680),  # Extended for practice
        has_hazard=False,
        is_competitive=True,
        music="training_theme"
    )

    # Simple flat platform for training
    main_x = (1280 - 1000) / 2
    stage.platforms = [
        Platform(
            id="main",
            x=main_x,
            y=540,
            width=1000,
            height=40,
            platform_type="solid",
            theme="tech"
        ),
        # Three floating platforms for combo practice
        Platform(
            id="train_left",
            x=250,
            y=380,
            width=180,
            height=20,
            platform_type="passthrough",
            theme="tech"
        ),
        Platform(
            id="train_center",
            x=550,
            y=280,
            width=180,
            height=20,
            platform_type="passthrough",
            theme="tech"
        ),
        Platform(
            id="train_right",
            x=850,
            y=380,
            width=180,
            height=20,
            platform_type="passthrough",
            theme="tech"
        )
    ]

    return stage


# All available stages (10 total)
STAGES = {
    # Competitive Stages (4)
    "battlefield": create_battlefield_stage,
    "final_destination": create_final_destination_stage,
    "sky_citadel": create_sky_citadel_stage,
    "whisperwood": create_whisperwood_stage,
    "dojo": create_dojo_stage,
    "training_room": create_training_room_stage,
    # Hazard Stages (4)
    "volcanic_fury": create_volcanic_fury_stage,
    "thunderstorm": create_thunderstorm_stage,
    "frozen_lake": create_frozen_lake_stage,
    "windmill": create_windmill_stage
}

# Legacy alias - map old arena names to new stages
ARENA_ALIASES = {
    "street": "battlefield",
    "rooftop": "sky_citadel",
    "warehouse": "final_destination",
    "park": "whisperwood"
}


def get_arena(name: str) -> Stage:
    """Get a stage by name (supports legacy arena names)"""
    # Check for legacy alias
    if name in ARENA_ALIASES:
        name = ARENA_ALIASES[name]

    creator = STAGES.get(name, create_battlefield_stage)
    return creator()


def get_stage(name: str) -> Stage:
    """Get a stage by name"""
    creator = STAGES.get(name, create_battlefield_stage)
    return creator()


def get_random_arena() -> Stage:
    """Get a random stage"""
    import random
    name = random.choice(list(STAGES.keys()))
    return get_stage(name)


def get_arena_names() -> List[str]:
    """Get list of stage names"""
    return list(STAGES.keys())


def get_stage_names() -> List[str]:
    """Get list of stage names"""
    return list(STAGES.keys())


def get_competitive_stages() -> List[str]:
    """Get list of competitive stage names (no hazards)"""
    return [name for name, creator in STAGES.items() if creator().is_competitive]


def get_hazard_stages() -> List[str]:
    """Get list of hazard stage names"""
    return [name for name, creator in STAGES.items() if not creator().is_competitive]


def get_stages_by_category() -> dict:
    """Get stages organized by category"""
    competitive = []
    hazard = []
    for name, creator in STAGES.items():
        stage = creator()
        if stage.is_competitive:
            competitive.append({
                'name': name,
                'display_name': stage.display_name,
                'theme': stage.theme
            })
        else:
            hazard.append({
                'name': name,
                'display_name': stage.display_name,
                'theme': stage.theme,
                'hazard_type': stage.hazard_type
            })
    return {
        'competitive': competitive,
        'hazard': hazard
    }


# Legacy alias for backward compatibility
Arena = Stage
