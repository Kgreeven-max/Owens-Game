/**
 * Arena Brawl - Main Entry Point
 * Initializes and coordinates all game systems
 */

class Game {
    constructor() {
        this.isPlaying = false;
        this.gameLoopId = null;
    }

    init() {
        console.log('Initializing Arena Brawl...');

        // Initialize UI
        ui.init();

        // Initialize renderer
        gameRenderer = new GameRenderer('game-canvas');

        // Set up network callbacks
        this.setupNetworkCallbacks();

        // Connect to server
        network.connect();

        console.log('Game initialized!');
    }

    setupNetworkCallbacks() {
        network.onConnected = (data) => {
            console.log('Connected to server');
            gameRenderer.setLocalPlayerId(data.player_id);
        };

        network.onDisconnected = () => {
            this.stopGameLoop();
            ui.showScreen('menu');
            ui.showNotification('Disconnected from server', 'error');
        };

        network.onRoomList = (rooms) => {
            ui.updateRoomList(rooms);
        };

        network.onGameInfo = (data) => {
            console.log('Game info:', data);
        };

        network.onRoomJoined = (roomData) => {
            ui.updateLobby(roomData);
            ui.showScreen('lobby');
        };

        network.onRoomUpdate = (roomData) => {
            ui.updateLobby(roomData);
        };

        network.onRoomClosed = () => {
            ui.showScreen('menu');
            ui.showNotification('Room was closed', 'info');
        };

        network.onMatchStart = (data) => {
            console.log('Match starting!', data);
            this.startGame(data);
        };

        network.onGameState = (data) => {
            if (gameRenderer) {
                gameRenderer.updateState(data);

                // Update HUD
                if (data.state && data.state.players) {
                    ui.updateHealthBars(data.state.players);
                }
                if (data.state && data.state.time_remaining !== undefined) {
                    ui.updateGameTimer(data.state.time_remaining);
                }

                // Handle countdown
                if (data.state && data.state.countdown > 0) {
                    gameRenderer.showCountdown(Math.ceil(data.state.countdown));
                } else if (data.state && data.state.state === 'playing') {
                    gameRenderer.showCountdown(-1);
                }
            }
        };

        network.onGameEvent = (event) => {
            console.log('Game event:', event);
            this.handleGameEvent(event);
        };

        network.onPlayerEliminated = (data) => {
            ui.showNotification(`${data.player_name} eliminated!`, 'info');
        };

        network.onMatchEnd = (result) => {
            console.log('Match ended:', result);
            this.stopGameLoop();
            input.disable();
            ui.showResults(result);
        };

        network.onError = (message) => {
            ui.showNotification(message, 'error');
        };
    }

    startGame(matchData) {
        this.isPlaying = true;

        // Show game screen
        ui.showScreen('game');

        // Resize canvas now that the game screen is visible
        if (gameRenderer) {
            gameRenderer.resize();
        }

        // Enable input
        input.enable();

        // Start game loop
        this.startGameLoop();
    }

    startGameLoop() {
        const loop = (timestamp) => {
            if (!this.isPlaying) return;

            // Send input to server
            if (input.enabled) {
                const inputState = input.getInputState();
                network.sendInput(inputState);
            }

            // Render game
            if (gameRenderer && gameRenderer.gameState) {
                gameRenderer.render(timestamp);
            }

            this.gameLoopId = requestAnimationFrame(loop);
        };

        this.gameLoopId = requestAnimationFrame(loop);
    }

    stopGameLoop() {
        this.isPlaying = false;
        if (this.gameLoopId) {
            cancelAnimationFrame(this.gameLoopId);
            this.gameLoopId = null;
        }
    }

    handleGameEvent(event) {
        switch (event.type) {
            case 'powerup_spawn':
            case 'healthbox_spawn':
                // Handled by state update
                break;

            case 'powerup_collected':
            case 'healthbox_collected':
                // Could show floating text effect
                break;

            case 'lightning_strike':
                gameRenderer.addEffect({
                    type: 'lightning_strike',
                    x: event.x,
                    y: event.y,
                    radius: event.radius,
                    duration: 500
                });
                break;

            case 'teleport':
                gameRenderer.addEffect({
                    type: 'teleport',
                    from_x: event.from_x,
                    from_y: event.from_y,
                    to_x: event.to_x,
                    to_y: event.to_y,
                    duration: 300
                });
                break;

            case 'fire_dash':
                gameRenderer.addEffect({
                    type: 'fire_dash',
                    start_x: event.start_x,
                    end_x: event.end_x,
                    y: 500,
                    duration: 400
                });
                break;
        }
    }
}

// Initialize game when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const game = new Game();
    game.init();
});
