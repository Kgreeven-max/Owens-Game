"""
Arena Brawl - Flask Application Entry Point
Main server with Flask + SocketIO for real-time multiplayer
"""
import time
import uuid
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

from server.config import get_config
from server.network.lobby import LobbyManager, Room, RoomState
from server.network.sync import StateSynchronizer
from server.network.matchmaking import Matchmaker
from server.game.engine import GameEngine, MatchState
from server.ai.bot import BotManager
from server.entities.character import get_character_names
from server.maps.arenas import get_arena_names


# Initialize Flask app
app = Flask(__name__, static_folder='../static', template_folder='../static')
config = get_config()
app.config['SECRET_KEY'] = config.SECRET_KEY

# Enable CORS
CORS(app)

# Initialize SocketIO with eventlet
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Game managers
lobby_manager = LobbyManager(config)
matchmaker = Matchmaker(lobby_manager, config)
synchronizers = {}  # room_id -> StateSynchronizer
bot_managers = {}   # room_id -> BotManager

# Player session tracking
player_sessions = {}  # socket_id -> player_id


# ============== Routes ==============

@app.route('/')
def index():
    """Serve the main game page"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory(app.static_folder, filename)


# ============== Socket Events ==============

@socketio.on('connect')
def handle_connect():
    """Handle new client connection"""
    player_id = str(uuid.uuid4())[:12]
    player_sessions[request.sid] = player_id
    emit('connected', {'player_id': player_id})
    print(f"Player connected: {player_id}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    player_id = player_sessions.pop(request.sid, None)
    if player_id:
        # Leave current room
        room = lobby_manager.get_player_room(player_id)
        if room:
            _handle_player_leave(player_id, room)
        print(f"Player disconnected: {player_id}")


@socketio.on('join_lobby')
def handle_join_lobby(data):
    """Player joins the main lobby"""
    player_id = player_sessions.get(request.sid)
    if not player_id:
        return

    player_name = data.get('player_name', f'Player_{player_id[:4]}')

    # Send available rooms
    emit('room_list', {'rooms': lobby_manager.get_room_list()})

    # Send available characters and arenas
    emit('game_info', {
        'characters': get_character_names(),
        'arenas': get_arena_names()
    })


@socketio.on('create_room')
def handle_create_room(data):
    """Create a new game room"""
    player_id = player_sessions.get(request.sid)
    if not player_id:
        return

    room = lobby_manager.create_room(
        host_id=player_id,
        host_socket=request.sid,
        host_name=data.get('player_name', f'Player_{player_id[:4]}'),
        room_name=data.get('room_name'),
        arena=data.get('arena', 'street'),
        is_private=data.get('is_private', False),
        password=data.get('password')
    )

    if room:
        join_room(room.room_id)
        emit('room_joined', room.to_dict())
        socketio.emit('room_list', {'rooms': lobby_manager.get_room_list()})
    else:
        emit('error', {'message': 'Failed to create room'})


@socketio.on('join_room')
def handle_join_room(data):
    """Join an existing room"""
    player_id = player_sessions.get(request.sid)
    if not player_id:
        return

    room = lobby_manager.join_room(
        room_id=data.get('room_id'),
        player_id=player_id,
        socket_id=request.sid,
        player_name=data.get('player_name', f'Player_{player_id[:4]}'),
        password=data.get('password')
    )

    if room:
        join_room(room.room_id)
        emit('room_joined', room.to_dict())
        socketio.emit('room_update', room.to_dict(), room=room.room_id)
    else:
        emit('error', {'message': 'Failed to join room'})


@socketio.on('quick_match')
def handle_quick_match(data):
    """Quick matchmaking"""
    player_id = player_sessions.get(request.sid)
    if not player_id:
        return

    room = lobby_manager.quick_match(
        player_id=player_id,
        socket_id=request.sid,
        player_name=data.get('player_name', f'Player_{player_id[:4]}')
    )

    if room:
        join_room(room.room_id)
        emit('room_joined', room.to_dict())
        socketio.emit('room_update', room.to_dict(), room=room.room_id)


@socketio.on('leave_room')
def handle_leave_room():
    """Leave current room"""
    player_id = player_sessions.get(request.sid)
    if not player_id:
        return

    room = lobby_manager.get_player_room(player_id)
    if room:
        _handle_player_leave(player_id, room)


def _handle_player_leave(player_id, room):
    """Handle a player leaving a room"""
    room_id = room.room_id
    leave_room(room_id)

    updated_room = lobby_manager.leave_room(player_id)

    if updated_room:
        socketio.emit('room_update', updated_room.to_dict(), room=room_id)
        socketio.emit('player_left', {'player_id': player_id}, room=room_id)
    else:
        # Room was deleted
        socketio.emit('room_closed', {'room_id': room_id}, room=room_id)

    socketio.emit('room_list', {'rooms': lobby_manager.get_room_list()})


@socketio.on('select_character')
def handle_select_character(data):
    """Select character in lobby"""
    player_id = player_sessions.get(request.sid)
    if not player_id:
        return

    room = lobby_manager.get_player_room(player_id)
    if room and room.set_player_character(player_id, data.get('character', 'Storm')):
        socketio.emit('room_update', room.to_dict(), room=room.room_id)


@socketio.on('ready')
def handle_ready(data):
    """Toggle ready status"""
    player_id = player_sessions.get(request.sid)
    if not player_id:
        return

    room = lobby_manager.get_player_room(player_id)
    if room:
        is_ready = data.get('ready', True)
        room.set_player_ready(player_id, is_ready)
        socketio.emit('room_update', room.to_dict(), room=room.room_id)

        # Check if game can start
        if room.can_start():
            _start_game(room)


@socketio.on('add_bot')
def handle_add_bot(data):
    """Add an AI bot to the room (host only)"""
    player_id = player_sessions.get(request.sid)
    if not player_id:
        return

    room = lobby_manager.get_player_room(player_id)
    if not room or room.host_id != player_id:
        emit('error', {'message': 'Only host can add bots'})
        return

    if len(room.players) >= room.max_players:
        emit('error', {'message': 'Room is full'})
        return

    # Create bot manager for this room if needed
    if room.room_id not in bot_managers:
        bot_managers[room.room_id] = BotManager(config)

    difficulty = data.get('difficulty', 'medium')
    bot_manager = bot_managers[room.room_id]
    bot_player = bot_manager.create_bot(difficulty)

    # Add bot to room
    room.add_player(bot_player.id, 'bot', bot_player.name)
    room.set_player_character(bot_player.id, bot_player.character)
    room.set_player_ready(bot_player.id, True)

    socketio.emit('room_update', room.to_dict(), room=room.room_id)


@socketio.on('start_game')
def handle_start_game():
    """Force start game (host only)"""
    player_id = player_sessions.get(request.sid)
    if not player_id:
        return

    room = lobby_manager.get_player_room(player_id)
    if not room or room.host_id != player_id:
        emit('error', {'message': 'Only host can start game'})
        return

    if len(room.players) < 2:
        emit('error', {'message': 'Need at least 2 players'})
        return

    _start_game(room)


def _start_game(room):
    """Start a game in a room"""
    game = room.start_game(config)

    # Set up synchronizer
    sync = StateSynchronizer(config.TICK_RATE)
    for player_id in room.players:
        sync.register_player(player_id)
    synchronizers[room.room_id] = sync

    # Set up callbacks
    game.on_event = lambda event: socketio.emit('game_event', event, room=room.room_id)
    game.on_player_eliminated = lambda pid, name: socketio.emit(
        'player_eliminated', {'player_id': pid, 'player_name': name}, room=room.room_id
    )
    game.on_match_end = lambda result: _handle_match_end(room.room_id, result)

    socketio.emit('match_start', {
        'arena': room.arena,
        'players': [p.to_dict() for p in game.players.values()]
    }, room=room.room_id)

    # Start game loop
    eventlet.spawn(_game_loop, room.room_id)


def _game_loop(room_id):
    """Main game loop running at 60 FPS"""
    room = lobby_manager.get_room(room_id)
    if not room or not room.game:
        return

    game = room.game
    sync = synchronizers.get(room_id)
    bot_manager = bot_managers.get(room_id)

    tick_interval = 1.0 / config.TICK_RATE

    while room.state == RoomState.IN_GAME and game.state in [MatchState.COUNTDOWN, MatchState.PLAYING]:
        start_time = time.time()

        # Process inputs from synchronizer
        if sync:
            for player_id in list(game.players.keys()):
                input_data = sync.get_latest_input(player_id)
                if input_data:
                    game.process_input(player_id, input_data)

        # Update bots
        if bot_manager:
            bot_manager.update_all(game.players, game._get_state(), time.time())

        # Update game
        state = game.update()

        # Broadcast state
        if sync and sync.should_sync():
            update = sync.create_state_update(state)
            socketio.emit('state', update, room=room_id)

        # Sleep to maintain tick rate
        elapsed = time.time() - start_time
        if elapsed < tick_interval:
            eventlet.sleep(tick_interval - elapsed)

    # Clean up
    if room_id in synchronizers:
        del synchronizers[room_id]


def _handle_match_end(room_id, result):
    """Handle match ending"""
    socketio.emit('match_end', {
        'winner_id': result.winner_id,
        'winner_name': result.winner_name,
        'duration': result.match_duration,
        'stats': result.player_stats
    }, room=room_id)

    room = lobby_manager.get_room(room_id)
    if room:
        room.state = RoomState.OPEN
        room.game = None
        # Reset ready status
        for player in room.players.values():
            player.is_ready = False
        socketio.emit('room_update', room.to_dict(), room=room_id)


@socketio.on('input')
def handle_input(data):
    """Handle player input during game"""
    player_id = player_sessions.get(request.sid)
    if not player_id:
        return

    room = lobby_manager.get_player_room(player_id)
    if not room or not room.game:
        return

    # Add to synchronizer buffer
    sync = synchronizers.get(room.room_id)
    if sync:
        sync.receive_input(player_id, data)


@socketio.on('chat')
def handle_chat(data):
    """Handle chat message"""
    player_id = player_sessions.get(request.sid)
    if not player_id:
        return

    room = lobby_manager.get_player_room(player_id)
    if room:
        player = room.players.get(player_id)
        if player:
            socketio.emit('chat', {
                'player_id': player_id,
                'player_name': player.name,
                'message': data.get('message', '')[:200]  # Limit message length
            }, room=room.room_id)


# Need to import request for socket handlers
from flask import request


# ============== Main ==============

if __name__ == '__main__':
    print(f"Starting Arena Brawl server on {config.HOST}:{config.PORT}")
    socketio.run(app, host=config.HOST, port=config.PORT, debug=config.DEBUG)
