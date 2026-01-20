/**
 * Arena Brawl - Network Module
 * Handles SocketIO client communication
 */

class NetworkManager {
    constructor() {
        this.socket = null;
        this.playerId = null;
        this.connected = false;

        // Callbacks
        this.onConnected = null;
        this.onDisconnected = null;
        this.onRoomList = null;
        this.onRoomJoined = null;
        this.onRoomUpdate = null;
        this.onMatchStart = null;
        this.onGameState = null;
        this.onGameEvent = null;
        this.onMatchEnd = null;
        this.onError = null;

        // Input state for sending
        this.lastInputSent = 0;
        this.inputInterval = 1000 / 60; // 60 Hz
    }

    connect(serverUrl = null) {
        // Default to current host
        const url = serverUrl || window.location.origin;

        this.socket = io(url, {
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000
        });

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Connection events
        this.socket.on('connect', () => {
            console.log('Socket connected');
            this.updateConnectionStatus('connected');
        });

        this.socket.on('disconnect', () => {
            console.log('Socket disconnected');
            this.connected = false;
            this.updateConnectionStatus('disconnected');
            if (this.onDisconnected) this.onDisconnected();
        });

        this.socket.on('connected', (data) => {
            this.playerId = data.player_id;
            this.connected = true;
            console.log('Player ID:', this.playerId);
            if (this.onConnected) this.onConnected(data);
        });

        // Lobby events
        this.socket.on('room_list', (data) => {
            if (this.onRoomList) this.onRoomList(data.rooms);
        });

        this.socket.on('game_info', (data) => {
            if (this.onGameInfo) this.onGameInfo(data);
        });

        this.socket.on('room_joined', (data) => {
            if (this.onRoomJoined) this.onRoomJoined(data);
        });

        this.socket.on('room_update', (data) => {
            if (this.onRoomUpdate) this.onRoomUpdate(data);
        });

        this.socket.on('room_closed', (data) => {
            if (this.onRoomClosed) this.onRoomClosed(data);
        });

        this.socket.on('player_left', (data) => {
            if (this.onPlayerLeft) this.onPlayerLeft(data);
        });

        // Game events
        this.socket.on('match_start', (data) => {
            if (this.onMatchStart) this.onMatchStart(data);
        });

        this.socket.on('state', (data) => {
            if (this.onGameState) this.onGameState(data);
        });

        this.socket.on('game_event', (data) => {
            if (this.onGameEvent) this.onGameEvent(data);
        });

        this.socket.on('player_eliminated', (data) => {
            if (this.onPlayerEliminated) this.onPlayerEliminated(data);
        });

        this.socket.on('match_end', (data) => {
            if (this.onMatchEnd) this.onMatchEnd(data);
        });

        // Chat
        this.socket.on('chat', (data) => {
            if (this.onChat) this.onChat(data);
        });

        // Errors
        this.socket.on('error', (data) => {
            console.error('Server error:', data.message);
            if (this.onError) this.onError(data.message);
        });
    }

    updateConnectionStatus(status) {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            statusEl.className = 'connection-status ' + status;
            const textEl = statusEl.querySelector('.status-text');
            if (textEl) {
                textEl.textContent = status === 'connected' ? 'Connected' :
                                    status === 'disconnected' ? 'Disconnected' : 'Connecting...';
            }
        }
    }

    // Lobby actions
    joinLobby(playerName) {
        this.socket.emit('join_lobby', { player_name: playerName });
    }

    createRoom(playerName, roomName, arena, isPrivate = false, password = null) {
        this.socket.emit('create_room', {
            player_name: playerName,
            room_name: roomName,
            arena: arena,
            is_private: isPrivate,
            password: password
        });
    }

    joinRoom(roomId, playerName, password = null) {
        this.socket.emit('join_room', {
            room_id: roomId,
            player_name: playerName,
            password: password
        });
    }

    quickMatch(playerName) {
        this.socket.emit('quick_match', { player_name: playerName });
    }

    leaveRoom() {
        this.socket.emit('leave_room');
    }

    selectCharacter(character) {
        this.socket.emit('select_character', { character: character });
    }

    setReady(ready = true) {
        this.socket.emit('ready', { ready: ready });
    }

    addBot(difficulty = 'medium') {
        this.socket.emit('add_bot', { difficulty: difficulty });
    }

    startGame() {
        this.socket.emit('start_game');
    }

    // Game actions
    sendInput(inputState) {
        const now = Date.now();
        if (now - this.lastInputSent < this.inputInterval) {
            return; // Throttle input sending
        }

        this.socket.emit('input', {
            move: inputState.move,
            action: inputState.action,
            jump: inputState.jump,
            hide: inputState.hide,
            timestamp: now
        });

        this.lastInputSent = now;
    }

    sendChat(message) {
        this.socket.emit('chat', { message: message });
    }

    // Utilities
    getPlayerId() {
        return this.playerId;
    }

    isConnected() {
        return this.connected;
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Global network instance
const network = new NetworkManager();
