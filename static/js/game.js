/**
 * Arena Brawl - Game Renderer
 * Canvas-based game rendering
 */

class GameRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');

        // Game state
        this.gameState = null;
        this.localPlayerId = null;

        // Arena dimensions
        this.arenaWidth = 1280;
        this.arenaHeight = 720;

        // Camera
        this.camera = { x: 0, y: 0 };
        this.scale = 1;

        // Animation
        this.animationFrame = 0;
        this.lastFrameTime = 0;

        // Character colors
        this.characterColors = {
            'Blaze': '#FF4500',
            'Tank': '#4169E1',
            'Shadow': '#8A2BE2',
            'Storm': '#FFD700'
        };

        // Effects
        this.effects = [];

        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        // Make canvas fill container while maintaining aspect ratio
        const container = this.canvas.parentElement;
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;

        const aspectRatio = this.arenaWidth / this.arenaHeight;
        let width = containerWidth;
        let height = containerWidth / aspectRatio;

        if (height > containerHeight) {
            height = containerHeight;
            width = containerHeight * aspectRatio;
        }

        this.canvas.width = width;
        this.canvas.height = height;
        this.scale = width / this.arenaWidth;
    }

    setLocalPlayerId(playerId) {
        this.localPlayerId = playerId;
    }

    updateState(state) {
        this.gameState = state.state || state;
    }

    addEffect(effect) {
        this.effects.push({
            ...effect,
            startTime: Date.now(),
            duration: effect.duration || 500
        });
    }

    render(timestamp) {
        if (!this.gameState) return;

        const dt = timestamp - this.lastFrameTime;
        this.lastFrameTime = timestamp;
        this.animationFrame++;

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Apply scale
        this.ctx.save();
        this.ctx.scale(this.scale, this.scale);

        // Draw arena background
        this.drawArena();

        // Draw obstacles
        if (this.gameState.arena && this.gameState.arena.obstacles) {
            this.gameState.arena.obstacles.forEach(obs => this.drawObstacle(obs));
        }

        // Draw collectibles
        if (this.gameState.events) {
            if (this.gameState.events.powerups) {
                this.gameState.events.powerups.forEach(p => this.drawPowerup(p));
            }
            if (this.gameState.events.healthboxes) {
                this.gameState.events.healthboxes.forEach(h => this.drawHealthbox(h));
            }
        }

        // Draw players
        if (this.gameState.players) {
            this.gameState.players.forEach(player => this.drawPlayer(player));
        }

        // Draw effects
        this.drawEffects();

        // Draw cop overlay if active
        if (this.gameState.events && this.gameState.events.cop_active) {
            this.drawCopOverlay();
        }

        this.ctx.restore();

        // Update effects
        this.updateEffects();
    }

    drawArena() {
        const arena = this.gameState.arena;
        if (!arena) return;

        // Background
        this.ctx.fillStyle = arena.background_color || '#2C3E50';
        this.ctx.fillRect(0, 0, this.arenaWidth, this.arenaHeight);

        // Ground
        this.ctx.fillStyle = '#34495E';
        this.ctx.fillRect(0, arena.ground_y || 600, this.arenaWidth, this.arenaHeight - (arena.ground_y || 600));

        // Ground line
        this.ctx.strokeStyle = '#5D6D7E';
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.moveTo(0, arena.ground_y || 600);
        this.ctx.lineTo(this.arenaWidth, arena.ground_y || 600);
        this.ctx.stroke();
    }

    drawObstacle(obstacle) {
        if (obstacle.is_destroyed) return;

        const { x, y, width, height, color, type } = obstacle;

        this.ctx.fillStyle = color || '#8B4513';

        if (type === 'platform') {
            // Platform style
            this.ctx.fillRect(x, y, width, height);
            this.ctx.strokeStyle = '#654321';
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(x, y, width, height);
        } else if (type === 'barrel') {
            // Barrel - rounded
            this.ctx.beginPath();
            this.ctx.ellipse(x + width/2, y + height/2, width/2, height/2, 0, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.strokeStyle = '#4A3520';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
        } else {
            // Default crate style
            this.ctx.fillRect(x, y, width, height);
            // Cross pattern
            this.ctx.strokeStyle = '#654321';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.moveTo(x, y);
            this.ctx.lineTo(x + width, y + height);
            this.ctx.moveTo(x + width, y);
            this.ctx.lineTo(x, y + height);
            this.ctx.stroke();
            this.ctx.strokeRect(x, y, width, height);
        }
    }

    drawPlayer(player) {
        const { x, y, character, facing_right, hp, max_hp, state, animation, is_invincible, name, combo_count } = player;

        const color = this.characterColors[character] || '#FFFFFF';
        const isLocal = player.id === this.localPlayerId;

        // Player dimensions
        const width = 50;
        const height = 80;

        this.ctx.save();
        this.ctx.translate(x, y);

        // Flip if facing left
        if (!facing_right) {
            this.ctx.scale(-1, 1);
        }

        // Invincibility flash
        if (is_invincible && this.animationFrame % 10 < 5) {
            this.ctx.globalAlpha = 0.5;
        }

        // Dead state
        if (state === 'dead') {
            this.ctx.globalAlpha = 0.3;
        }

        // Body
        this.ctx.fillStyle = color;
        this.ctx.fillRect(-width/2, -height, width, height);

        // Head (cartoony)
        this.ctx.beginPath();
        this.ctx.arc(0, -height - 15, 20, 0, Math.PI * 2);
        this.ctx.fill();

        // Eyes
        this.ctx.fillStyle = 'white';
        this.ctx.beginPath();
        this.ctx.arc(5, -height - 18, 6, 0, Math.PI * 2);
        this.ctx.fill();

        this.ctx.fillStyle = 'black';
        this.ctx.beginPath();
        this.ctx.arc(7, -height - 18, 3, 0, Math.PI * 2);
        this.ctx.fill();

        // Attack animation
        if (state === 'attacking') {
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
            this.ctx.beginPath();
            this.ctx.arc(width/2 + 20, -height/2, 30, 0, Math.PI * 2);
            this.ctx.fill();
        }

        // Blocking stance
        if (state === 'blocking') {
            this.ctx.strokeStyle = '#4ECDC4';
            this.ctx.lineWidth = 4;
            this.ctx.beginPath();
            this.ctx.arc(0, -height/2, 40, 0, Math.PI * 2);
            this.ctx.stroke();
        }

        this.ctx.restore();

        // Draw health bar above player (always upright)
        const healthPercent = hp / max_hp;
        const barWidth = 60;
        const barHeight = 8;
        const barY = y - height - 50;

        // Background
        this.ctx.fillStyle = '#333';
        this.ctx.fillRect(x - barWidth/2, barY, barWidth, barHeight);

        // Health fill
        this.ctx.fillStyle = healthPercent > 0.3 ? '#4ECDC4' : '#FF6B6B';
        this.ctx.fillRect(x - barWidth/2, barY, barWidth * healthPercent, barHeight);

        // Border
        this.ctx.strokeStyle = isLocal ? '#FFD700' : '#666';
        this.ctx.lineWidth = isLocal ? 2 : 1;
        this.ctx.strokeRect(x - barWidth/2, barY, barWidth, barHeight);

        // Name tag
        this.ctx.fillStyle = 'white';
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(name || 'Player', x, barY - 5);

        // Combo counter
        if (combo_count > 1) {
            this.ctx.fillStyle = '#FFD700';
            this.ctx.font = 'bold 16px Arial';
            this.ctx.fillText(`${combo_count}x COMBO!`, x, barY - 20);
        }
    }

    drawPowerup(powerup) {
        if (!powerup.is_active) return;

        const { x, y, type } = powerup;
        const size = 30;

        // Glow effect
        this.ctx.shadowColor = '#FFD700';
        this.ctx.shadowBlur = 15;

        // Diamond shape
        this.ctx.fillStyle = type === 'speed_boost' ? '#00FF00' :
                            type === 'damage_boost' ? '#FF0000' : '#FFD700';

        this.ctx.beginPath();
        this.ctx.moveTo(x, y - size);
        this.ctx.lineTo(x + size, y);
        this.ctx.lineTo(x, y + size);
        this.ctx.lineTo(x - size, y);
        this.ctx.closePath();
        this.ctx.fill();

        this.ctx.shadowBlur = 0;
    }

    drawHealthbox(healthbox) {
        if (!healthbox.is_active) return;

        const { x, y, tier, color } = healthbox;
        const size = 35;

        // Glow
        this.ctx.shadowColor = color;
        this.ctx.shadowBlur = healthbox.glow * 20 || 10;

        // Box
        this.ctx.fillStyle = color;
        this.ctx.fillRect(x - size/2, y - size/2, size, size);

        // Cross symbol
        this.ctx.fillStyle = 'white';
        this.ctx.fillRect(x - 3, y - 12, 6, 24);
        this.ctx.fillRect(x - 12, y - 3, 24, 6);

        this.ctx.shadowBlur = 0;
    }

    drawEffects() {
        const now = Date.now();

        this.effects.forEach(effect => {
            const elapsed = now - effect.startTime;
            const progress = elapsed / effect.duration;

            if (progress > 1) return;

            this.ctx.globalAlpha = 1 - progress;

            switch (effect.type) {
                case 'hit':
                    this.ctx.fillStyle = '#FF0000';
                    this.ctx.beginPath();
                    this.ctx.arc(effect.x, effect.y, 30 * (1 + progress), 0, Math.PI * 2);
                    this.ctx.fill();
                    break;

                case 'lightning_strike':
                    this.ctx.strokeStyle = '#FFD700';
                    this.ctx.lineWidth = 5;
                    this.ctx.beginPath();
                    this.ctx.arc(effect.x, effect.y, effect.radius * progress, 0, Math.PI * 2);
                    this.ctx.stroke();
                    break;

                case 'teleport':
                    this.ctx.fillStyle = '#8A2BE2';
                    this.ctx.beginPath();
                    this.ctx.arc(effect.from_x, effect.from_y, 20 * (1 - progress), 0, Math.PI * 2);
                    this.ctx.fill();
                    this.ctx.beginPath();
                    this.ctx.arc(effect.to_x, effect.to_y, 20 * progress, 0, Math.PI * 2);
                    this.ctx.fill();
                    break;

                case 'fire_dash':
                    this.ctx.fillStyle = '#FF4500';
                    const dashX = effect.start_x + (effect.end_x - effect.start_x) * progress;
                    for (let i = 0; i < 5; i++) {
                        const fx = dashX - (effect.end_x - effect.start_x) * 0.1 * i;
                        this.ctx.globalAlpha = (1 - progress) * (1 - i * 0.2);
                        this.ctx.beginPath();
                        this.ctx.arc(fx, effect.y || 500, 15, 0, Math.PI * 2);
                        this.ctx.fill();
                    }
                    break;
            }

            this.ctx.globalAlpha = 1;
        });
    }

    drawCopOverlay() {
        // Red tint overlay
        this.ctx.fillStyle = 'rgba(255, 0, 0, 0.1)';
        this.ctx.fillRect(0, 0, this.arenaWidth, this.arenaHeight);

        // Flashing border
        if (this.animationFrame % 20 < 10) {
            this.ctx.strokeStyle = '#FF0000';
            this.ctx.lineWidth = 10;
            this.ctx.strokeRect(5, 5, this.arenaWidth - 10, this.arenaHeight - 10);
        }
    }

    updateEffects() {
        const now = Date.now();
        this.effects = this.effects.filter(effect => {
            return (now - effect.startTime) < effect.duration;
        });
    }

    showCountdown(number) {
        const overlay = document.getElementById('countdown-overlay');
        const numberEl = document.getElementById('countdown-number');

        if (number > 0) {
            overlay.classList.remove('hidden');
            numberEl.textContent = number;
        } else if (number === 0) {
            numberEl.textContent = 'FIGHT!';
            setTimeout(() => {
                overlay.classList.add('hidden');
            }, 500);
        } else {
            overlay.classList.add('hidden');
        }
    }

    showCopWarning(show) {
        const warning = document.getElementById('cop-warning');
        if (warning) {
            if (show) {
                warning.classList.remove('hidden');
            } else {
                warning.classList.add('hidden');
            }
        }
    }
}

// Global renderer instance
let gameRenderer = null;
