/**
 * Arena Brawl - UI Manager
 * Handles all UI updates and screen transitions
 */

class UIManager {
    constructor() {
        this.currentScreen = 'menu';
        this.playerName = '';
        this.selectedCharacter = 'Storm';
        this.currentRoom = null;
        this.isHost = false;
        this.isReady = false;

        // Character info for display
        this.characterInfo = {
            'Blaze': { color: '#FF4500', style: 'Aggressive', special: 'Fire Dash' },
            'Tank': { color: '#4169E1', style: 'Defensive', special: 'Shield Block' },
            'Shadow': { color: '#8A2BE2', style: 'Evasive', special: 'Teleport' },
            'Storm': { color: '#FFD700', style: 'Balanced', special: 'Lightning Strike' }
        };
    }

    init() {
        this.setupMenuEvents();
        this.setupLobbyEvents();
    }

    setupMenuEvents() {
        // Quick Match
        document.getElementById('btn-quick-match')?.addEventListener('click', () => {
            this.playerName = document.getElementById('player-name').value || 'Player';
            network.quickMatch(this.playerName);
        });

        // Create Room
        document.getElementById('btn-create-room')?.addEventListener('click', () => {
            this.showScreen('create');
        });

        // Browse Rooms
        document.getElementById('btn-browse-rooms')?.addEventListener('click', () => {
            this.playerName = document.getElementById('player-name').value || 'Player';
            network.joinLobby(this.playerName);
            this.showScreen('browser');
        });

        // Practice vs AI
        document.getElementById('btn-practice')?.addEventListener('click', () => {
            this.playerName = document.getElementById('player-name').value || 'Player';
            network.createRoom(this.playerName, 'Practice', 'street');
            // Will add bots after joining
        });

        // Back buttons
        document.getElementById('btn-back-menu')?.addEventListener('click', () => {
            this.showScreen('menu');
        });

        document.getElementById('btn-back-create')?.addEventListener('click', () => {
            this.showScreen('menu');
        });

        // Confirm create room
        document.getElementById('btn-confirm-create')?.addEventListener('click', () => {
            this.playerName = document.getElementById('player-name').value || 'Player';
            const roomName = document.getElementById('room-name').value || `${this.playerName}'s Room`;
            const arena = document.getElementById('arena-select').value;
            network.createRoom(this.playerName, roomName, arena);
        });
    }

    setupLobbyEvents() {
        // Ready button
        document.getElementById('btn-ready')?.addEventListener('click', () => {
            this.isReady = !this.isReady;
            network.setReady(this.isReady);
            this.updateReadyButton();
        });

        // Add Bot
        document.getElementById('btn-add-bot')?.addEventListener('click', () => {
            network.addBot('medium');
        });

        // Start Game (host only)
        document.getElementById('btn-start')?.addEventListener('click', () => {
            network.startGame();
        });

        // Leave Lobby
        document.getElementById('btn-leave-lobby')?.addEventListener('click', () => {
            network.leaveRoom();
            this.showScreen('menu');
        });

        // Results buttons
        document.getElementById('btn-rematch')?.addEventListener('click', () => {
            this.isReady = false;
            this.updateReadyButton();
            this.showScreen('lobby');
        });

        document.getElementById('btn-back-lobby')?.addEventListener('click', () => {
            this.isReady = false;
            this.updateReadyButton();
            this.showScreen('lobby');
        });
    }

    showScreen(screenName) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });

        // Show target screen
        const screen = document.getElementById(`${screenName}-screen`);
        if (screen) {
            screen.classList.add('active');
            this.currentScreen = screenName;
        }
    }

    updateRoomList(rooms) {
        const container = document.getElementById('room-list');
        if (!container) return;

        if (rooms.length === 0) {
            container.innerHTML = '<p class="no-rooms">No rooms available. Create one!</p>';
            return;
        }

        container.innerHTML = rooms.map(room => `
            <div class="room-item" data-room-id="${room.room_id}">
                <div class="room-info">
                    <div class="room-name">${this.escapeHtml(room.name)}</div>
                    <div class="room-players">${room.player_count}/${room.max_players} players - ${room.arena}</div>
                </div>
                <button class="menu-btn" onclick="ui.joinRoom('${room.room_id}')">Join</button>
            </div>
        `).join('');
    }

    joinRoom(roomId) {
        this.playerName = document.getElementById('player-name').value || 'Player';
        network.joinRoom(roomId, this.playerName);
    }

    updateLobby(roomData) {
        this.currentRoom = roomData;
        this.isHost = roomData.host_id === network.getPlayerId();

        // Update title
        const title = document.getElementById('lobby-title');
        if (title) {
            title.textContent = roomData.name;
        }

        // Update players list
        const playersContainer = document.getElementById('lobby-players');
        if (playersContainer) {
            playersContainer.innerHTML = roomData.players.map(player => `
                <div class="lobby-player ${player.is_ready ? 'ready' : ''} ${player.is_host ? 'host' : ''}">
                    <div class="player-avatar" style="background: ${this.characterInfo[player.character]?.color || '#666'}"></div>
                    <div class="player-name">${this.escapeHtml(player.name)}</div>
                    <div class="player-character">${player.character}</div>
                    ${player.is_ready ? '<div class="ready-badge">READY</div>' : ''}
                </div>
            `).join('');
        }

        // Update character selection
        this.updateCharacterGrid(roomData);

        // Show/hide host controls
        const startBtn = document.getElementById('btn-start');
        const addBotBtn = document.getElementById('btn-add-bot');
        if (startBtn) {
            startBtn.style.display = this.isHost ? 'block' : 'none';
        }
        if (addBotBtn) {
            addBotBtn.style.display = this.isHost ? 'block' : 'none';
        }
    }

    updateCharacterGrid(roomData) {
        const grid = document.getElementById('character-grid');
        if (!grid) return;

        const myPlayer = roomData.players.find(p => p.id === network.getPlayerId());
        const myCharacter = myPlayer?.character || this.selectedCharacter;

        grid.innerHTML = Object.entries(this.characterInfo).map(([name, info]) => `
            <div class="character-card ${myCharacter === name ? 'selected' : ''}"
                 data-character="${name}"
                 onclick="ui.selectCharacter('${name}')">
                <div class="character-icon" style="background: ${info.color}"></div>
                <div class="character-name">${name}</div>
                <div class="character-style">${info.style}</div>
            </div>
        `).join('');
    }

    selectCharacter(character) {
        this.selectedCharacter = character;
        network.selectCharacter(character);

        // Update UI
        document.querySelectorAll('.character-card').forEach(card => {
            card.classList.toggle('selected', card.dataset.character === character);
        });
    }

    updateReadyButton() {
        const btn = document.getElementById('btn-ready');
        if (btn) {
            btn.textContent = this.isReady ? 'Not Ready' : 'Ready';
            btn.classList.toggle('primary', !this.isReady);
        }
    }

    updateHealthBars(players) {
        const container = document.getElementById('player-health-bars');
        if (!container) return;

        container.innerHTML = players.map(player => {
            const healthPercent = (player.hp / player.max_hp) * 100;
            const isLow = healthPercent < 30;

            return `
                <div class="health-bar-container">
                    <div class="health-bar-name">${this.escapeHtml(player.name)}</div>
                    <div class="health-bar">
                        <div class="health-bar-fill ${isLow ? 'low' : ''}"
                             style="width: ${healthPercent}%"></div>
                    </div>
                    <div class="lives-display">${'❤️'.repeat(player.lives)}</div>
                </div>
            `;
        }).join('');
    }

    updateGameTimer(seconds) {
        const timer = document.getElementById('game-timer');
        if (timer) {
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            timer.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
        }
    }

    showResults(result) {
        const title = document.getElementById('result-title');
        const winnerDisplay = document.getElementById('winner-display');
        const statsContainer = document.getElementById('match-stats');

        if (title) {
            title.textContent = result.winner_id ? 'Match Over!' : 'Draw!';
        }

        if (winnerDisplay) {
            if (result.winner_name) {
                document.getElementById('winner-name').textContent = result.winner_name;
                winnerDisplay.style.display = 'block';
            } else {
                winnerDisplay.style.display = 'none';
            }
        }

        if (statsContainer && result.stats) {
            statsContainer.innerHTML = Object.entries(result.stats).map(([playerId, stats]) => `
                <div class="stat-row">
                    <span>Damage Dealt</span>
                    <span>${stats.damage_dealt}</span>
                </div>
                <div class="stat-row">
                    <span>Damage Taken</span>
                    <span>${stats.damage_taken}</span>
                </div>
            `).join('');
        }

        this.showScreen('results');
    }

    showNotification(message, type = 'info') {
        // Could add a notification system here
        console.log(`[${type}] ${message}`);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global UI instance
const ui = new UIManager();
