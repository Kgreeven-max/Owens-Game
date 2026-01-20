"""
Arena Brawl - Server Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

    # Game settings
    TICK_RATE = 60  # Server tick rate (FPS)
    MAX_PLAYERS_PER_ROOM = 4
    MAX_ROOMS = 10

    # Arena dimensions
    ARENA_WIDTH = 1280
    ARENA_HEIGHT = 720

    # Physics
    GRAVITY = 0.8
    GROUND_Y = 600  # Ground level Y position
    FRICTION = 0.85

    # Match settings
    MATCH_TIME = 180  # 3 minutes in seconds
    LIVES_PER_PLAYER = 3
    RESPAWN_INVINCIBILITY = 2.0  # seconds

    # Movement settings - SSB-style feel
    WALK_SPEED = 3.0           # Slow precise movement
    RUN_SPEED = 7.0            # Full speed after dash
    INITIAL_DASH_SPEED = 9.0   # Quick burst on direction tap
    INITIAL_DASH_FRAMES = 12   # Frames locked in initial dash
    TURNAROUND_FRAMES = 4      # Frames for turn animation
    AIR_DRIFT_ACCEL = 0.4      # Air control acceleration
    AIR_DRIFT_MAX = 5.0        # Max air speed from drift
    FAST_FALL_MULTIPLIER = 1.6 # Fast fall speed multiplier
    JUMP_SQUAT_FRAMES = 3      # Pre-jump frames
    SHORT_HOP_MULTIPLIER = 0.6 # Short hop = 60% height
    MAX_AIR_JUMPS = 2          # Double jump default

    # Dodge/Parry settings
    SPOT_DODGE_FRAMES = 20     # Total spot dodge duration
    SPOT_DODGE_IFRAMES = (3, 15)  # Invincible from frame 3-15
    AIR_DODGE_FRAMES = 24      # Total air dodge duration
    AIR_DODGE_IFRAMES = (4, 18)   # Invincible from frame 4-18
    AIR_DODGE_DISTANCE = 100   # Distance traveled in directional dodge
    PARRY_WINDOW = 3           # Frame-perfect parry window
    DODGE_STALE_REDUCTION = 0.15  # Each dodge reduces i-frames by 15%
    DODGE_STALE_MAX = 5        # Max stale count before refresh

    # Combat settings - SSB-style feel
    LIGHT_ATTACK_DAMAGE = 8
    HEAVY_ATTACK_DAMAGE = 20
    BLOCK_REDUCTION = 0.5  # 50% damage reduction
    KNOCKBACK_BASE = 5
    KNOCKBACK_SCALING = 0.15  # More knockback at higher damage %
    COMBO_WINDOW = 0.4  # Seconds to chain attacks
    HITSTUN_DURATION = 0.3  # Stagger time after being hit

    # Power-up settings
    POWERUP_SPAWN_INTERVAL = (10, 20)  # seconds range
    HEALTH_BOX_TIERS = {
        'common': {'color': 'brown', 'heal': 15, 'speed_boost': 1.1},
        'rare': {'color': 'silver', 'heal': 35, 'damage_boost': 1.25},
        'epic': {'color': 'gold', 'heal': 100, 'invincibility': 3.0}
    }

    # AI settings
    AI_DIFFICULTY_LEVELS = ['easy', 'medium', 'hard']
    AI_REACTION_TIME = {
        'easy': 0.5,
        'medium': 0.3,
        'hard': 0.1
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


# Select config based on environment
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

def get_config():
    """Get the appropriate config based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)()
