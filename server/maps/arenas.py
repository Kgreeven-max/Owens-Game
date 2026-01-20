"""
Arena Brawl - Arena Definitions
Map layouts with obstacles and spawn points
"""
from dataclasses import dataclass, field
from typing import List, Tuple
from server.entities.obstacle import Obstacle, create_obstacle


@dataclass
class Arena:
    """Defines an arena/map"""
    name: str
    display_name: str
    width: int
    height: int
    ground_y: int
    background_color: str
    obstacles: List[Obstacle] = field(default_factory=list)
    spawn_points: List[Tuple[float, float]] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize for network"""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'width': self.width,
            'height': self.height,
            'ground_y': self.ground_y,
            'background_color': self.background_color,
            'obstacles': [o.to_dict() for o in self.obstacles if not o.is_destroyed],
            'spawn_points': self.spawn_points
        }


def create_street_arena() -> Arena:
    """Create the Street arena - urban fighting"""
    arena = Arena(
        name="street",
        display_name="Street Fight",
        width=1280,
        height=720,
        ground_y=600,
        background_color="#2C3E50",
        spawn_points=[
            (200, 600),
            (1080, 600),
            (400, 600),
            (880, 600)
        ]
    )

    # Add obstacles
    arena.obstacles = [
        # Left side crates
        create_obstacle("obs_1", 150, 540, "crate"),
        create_obstacle("obs_2", 210, 540, "crate"),
        create_obstacle("obs_3", 180, 480, "crate"),

        # Center platform
        create_obstacle("obs_4", 540, 450, "platform"),

        # Right side barrels
        create_obstacle("obs_5", 1000, 550, "barrel"),
        create_obstacle("obs_6", 1050, 550, "barrel"),
        create_obstacle("obs_7", 1100, 550, "barrel"),

        # Dividing wall
        create_obstacle("obs_8", 630, 450, "wall"),
    ]

    return arena


def create_rooftop_arena() -> Arena:
    """Create the Rooftop arena - elevated fighting"""
    arena = Arena(
        name="rooftop",
        display_name="Rooftop Rumble",
        width=1280,
        height=720,
        ground_y=600,
        background_color="#1a1a2e",
        spawn_points=[
            (150, 600),
            (1130, 600),
            (350, 400),
            (930, 400)
        ]
    )

    arena.obstacles = [
        # Lower platforms
        create_obstacle("obs_1", 100, 500, "platform"),
        create_obstacle("obs_2", 980, 500, "platform"),

        # Upper platforms
        create_obstacle("obs_3", 300, 350, "platform"),
        create_obstacle("obs_4", 780, 350, "platform"),

        # Center obstacle
        create_obstacle("obs_5", 600, 450, "crate"),
        create_obstacle("obs_6", 660, 450, "crate"),

        # Cover walls
        create_obstacle("obs_7", 250, 450, "wall"),
        create_obstacle("obs_8", 1010, 450, "wall"),
    ]

    return arena


def create_warehouse_arena() -> Arena:
    """Create the Warehouse arena - indoor fighting"""
    arena = Arena(
        name="warehouse",
        display_name="Warehouse Brawl",
        width=1280,
        height=720,
        ground_y=600,
        background_color="#3d3d3d",
        spawn_points=[
            (100, 600),
            (1180, 600),
            (640, 400),
            (640, 600)
        ]
    )

    arena.obstacles = [
        # Stacked crates left
        create_obstacle("obs_1", 80, 540, "crate"),
        create_obstacle("obs_2", 140, 540, "crate"),
        create_obstacle("obs_3", 110, 480, "crate"),

        # Stacked crates right
        create_obstacle("obs_4", 1080, 540, "crate"),
        create_obstacle("obs_5", 1140, 540, "crate"),
        create_obstacle("obs_6", 1110, 480, "crate"),

        # Center platforms
        create_obstacle("obs_7", 440, 450, "platform"),
        create_obstacle("obs_8", 640, 450, "platform"),

        # Barrels for cover
        create_obstacle("obs_9", 350, 550, "barrel"),
        create_obstacle("obs_10", 900, 550, "barrel"),
    ]

    return arena


def create_park_arena() -> Arena:
    """Create the Park arena - outdoor fighting"""
    arena = Arena(
        name="park",
        display_name="Park Showdown",
        width=1280,
        height=720,
        ground_y=600,
        background_color="#228B22",
        spawn_points=[
            (200, 600),
            (1080, 600),
            (500, 350),
            (780, 350)
        ]
    )

    arena.obstacles = [
        # Tree stumps (like barrels)
        create_obstacle("obs_1", 200, 550, "barrel"),
        create_obstacle("obs_2", 1040, 550, "barrel"),

        # Bench platforms
        create_obstacle("obs_3", 350, 520, "platform"),
        create_obstacle("obs_4", 730, 520, "platform"),

        # Elevated platform (tree branch)
        create_obstacle("obs_5", 490, 320, "platform"),

        # Rock walls
        create_obstacle("obs_6", 550, 450, "wall"),
        create_obstacle("obs_7", 710, 450, "wall"),
    ]

    return arena


# All available arenas
ARENAS = {
    "street": create_street_arena,
    "rooftop": create_rooftop_arena,
    "warehouse": create_warehouse_arena,
    "park": create_park_arena
}


def get_arena(name: str) -> Arena:
    """Get an arena by name"""
    creator = ARENAS.get(name, create_street_arena)
    return creator()


def get_random_arena() -> Arena:
    """Get a random arena"""
    import random
    name = random.choice(list(ARENAS.keys()))
    return get_arena(name)


def get_arena_names() -> List[str]:
    """Get list of arena names"""
    return list(ARENAS.keys())
