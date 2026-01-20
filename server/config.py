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

    # Combat settings
    LIGHT_ATTACK_DAMAGE = 8
    HEAVY_ATTACK_DAMAGE = 20
    BLOCK_REDUCTION = 0.5  # 50% damage reduction
    KNOCKBACK_BASE = 5
    COMBO_WINDOW = 0.5  # seconds to chain combos

    # Power-up settings
    POWERUP_SPAWN_INTERVAL = (10, 20)  # seconds range
    HEALTH_BOX_TIERS = {
        'common': {'color': 'brown', 'heal': 15, 'speed_boost': 1.1},
        'rare': {'color': 'silver', 'heal': 35, 'damage_boost': 1.25},
        'epic': {'color': 'gold', 'heal': 100, 'invincibility': 3.0}
    }

    # Cop mechanic
    COP_SPAWN_INTERVAL = (30, 60)  # seconds range
    COP_WARNING_TIME = 3  # seconds before cop arrives
    COP_DAMAGE = 25  # % of max HP
    COP_DURATION = 5  # seconds cop is active

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
