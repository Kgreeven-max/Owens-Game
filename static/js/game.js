/**
 * Arena Brawl - Game Renderer
 * Canvas-based game rendering with SSB-style backgrounds
 */

/**
 * BackgroundRenderer - Handles animated parallax backgrounds per stage theme
 */
class BackgroundRenderer {
    constructor() {
        this.currentTheme = null;
        this.layers = [];
        this.particles = [];
        this.time = 0;

        // Theme configurations
        this.themes = {
            battlefield: {
                skyColors: ['#1a0a2e', '#4a1a6e', '#8b3a9e', '#d4649a'],
                layers: [
                    { type: 'mountains', speed: 0.05, color: '#2a1a3e', yOffset: 0.4 },
                    { type: 'mountains', speed: 0.1, color: '#3a2a4e', yOffset: 0.5 },
                    { type: 'clouds', speed: 0.15, color: 'rgba(255,255,255,0.3)', count: 5 },
                    { type: 'sparkles', speed: 1.0, count: 30 }
                ]
            },
            space: {
                skyColors: ['#0a0a1a', '#1a1a3a', '#0a2a4a'],
                layers: [
                    { type: 'stars', speed: 0.02, count: 100 },
                    { type: 'nebula', speed: 0.05, colors: ['#4a1a6e', '#1a4a6e'] },
                    { type: 'energy_streams', speed: 0.3, color: '#00ffff', count: 3 }
                ]
            },
            volcano: {
                skyColors: ['#1a0a0a', '#4a1a0a', '#8b2a0a', '#d44a0a'],
                layers: [
                    { type: 'volcanic_peaks', speed: 0.05, color: '#2a1a0a', yOffset: 0.3 },
                    { type: 'volcanic_peaks', speed: 0.1, color: '#4a2a1a', yOffset: 0.45 },
                    { type: 'smoke', speed: 0.2, color: 'rgba(50,30,20,0.5)', count: 8 },
                    { type: 'embers', speed: 1.5, count: 40 }
                ]
            },
            sky: {
                skyColors: ['#87CEEB', '#B0E0E6', '#E0F6FF', '#FFFFFF'],
                layers: [
                    { type: 'distant_clouds', speed: 0.08, color: 'rgba(255,255,255,0.6)', count: 6 },
                    { type: 'floating_islands', speed: 0.12, color: '#6a8a5a', count: 3 },
                    { type: 'clouds', speed: 0.2, color: 'rgba(255,255,255,0.8)', count: 4 },
                    { type: 'birds', speed: 0.5, count: 5 }
                ]
            },
            forest: {
                skyColors: ['#0a1a0a', '#1a2a1a', '#2a3a2a', '#1a3a2a'],
                layers: [
                    { type: 'trees', speed: 0.05, color: '#0a1a0a', yOffset: 0.2, scale: 1.5 },
                    { type: 'trees', speed: 0.1, color: '#1a2a1a', yOffset: 0.35, scale: 1.2 },
                    { type: 'trees', speed: 0.15, color: '#2a3a2a', yOffset: 0.5, scale: 1.0 },
                    { type: 'fireflies', speed: 1.0, count: 25 },
                    { type: 'mist', speed: 0.08, color: 'rgba(100,150,100,0.2)' }
                ]
            }
        };

        // Cached background elements
        this.cachedElements = {};
    }

    setTheme(theme) {
        if (this.currentTheme !== theme) {
            this.currentTheme = theme;
            this.particles = [];
            this.initializeParticles();
        }
    }

    initializeParticles() {
        const config = this.themes[this.currentTheme];
        if (!config) return;

        for (const layer of config.layers) {
            if (layer.type === 'sparkles' || layer.type === 'stars') {
                for (let i = 0; i < layer.count; i++) {
                    this.particles.push({
                        type: layer.type,
                        x: Math.random() * 1280,
                        y: Math.random() * 400,
                        size: Math.random() * 2 + 1,
                        twinkle: Math.random() * Math.PI * 2,
                        speed: layer.speed
                    });
                }
            } else if (layer.type === 'embers') {
                for (let i = 0; i < layer.count; i++) {
                    this.particles.push({
                        type: 'ember',
                        x: Math.random() * 1280,
                        y: 720 + Math.random() * 100,
                        vx: (Math.random() - 0.5) * 0.5,
                        vy: -Math.random() * 2 - 1,
                        size: Math.random() * 4 + 2,
                        life: Math.random()
                    });
                }
            } else if (layer.type === 'fireflies') {
                for (let i = 0; i < layer.count; i++) {
                    this.particles.push({
                        type: 'firefly',
                        x: Math.random() * 1280,
                        y: 200 + Math.random() * 400,
                        baseX: Math.random() * 1280,
                        baseY: 200 + Math.random() * 400,
                        phase: Math.random() * Math.PI * 2,
                        glowPhase: Math.random() * Math.PI * 2
                    });
                }
            } else if (layer.type === 'birds') {
                for (let i = 0; i < layer.count; i++) {
                    this.particles.push({
                        type: 'bird',
                        x: Math.random() * 1600 - 160,
                        y: 50 + Math.random() * 200,
                        vx: 0.5 + Math.random() * 0.5,
                        wingPhase: Math.random() * Math.PI * 2
                    });
                }
            }
        }
    }

    update(dt) {
        this.time += dt / 1000;

        // Update particles
        for (const p of this.particles) {
            if (p.type === 'ember') {
                p.x += p.vx;
                p.y += p.vy;
                p.life -= 0.005;
                if (p.life <= 0 || p.y < -10) {
                    p.x = Math.random() * 1280;
                    p.y = 720 + Math.random() * 50;
                    p.life = 1;
                }
            } else if (p.type === 'firefly') {
                p.x = p.baseX + Math.sin(this.time * 0.5 + p.phase) * 30;
                p.y = p.baseY + Math.cos(this.time * 0.3 + p.phase) * 20;
            } else if (p.type === 'bird') {
                p.x += p.vx;
                p.wingPhase += 0.2;
                if (p.x > 1440) {
                    p.x = -80;
                    p.y = 50 + Math.random() * 200;
                }
            }
        }
    }

    render(ctx, width, height) {
        const config = this.themes[this.currentTheme];
        if (!config) {
            ctx.fillStyle = '#2C3E50';
            ctx.fillRect(0, 0, width, height);
            return;
        }

        // Draw sky gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, height);
        const colors = config.skyColors;
        for (let i = 0; i < colors.length; i++) {
            gradient.addColorStop(i / (colors.length - 1), colors[i]);
        }
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);

        // Draw layers
        for (const layer of config.layers) {
            this.renderLayer(ctx, layer, width, height);
        }

        // Draw particles
        this.renderParticles(ctx);
    }

    renderLayer(ctx, layer, width, height) {
        const offset = (this.time * layer.speed * 50) % width;

        switch (layer.type) {
            case 'mountains':
            case 'volcanic_peaks':
                this.drawMountains(ctx, layer, width, height, offset);
                break;
            case 'clouds':
            case 'distant_clouds':
                this.drawClouds(ctx, layer, width, height, offset);
                break;
            case 'trees':
                this.drawTrees(ctx, layer, width, height, offset);
                break;
            case 'nebula':
                this.drawNebula(ctx, layer, width, height);
                break;
            case 'energy_streams':
                this.drawEnergyStreams(ctx, layer, width, height);
                break;
            case 'floating_islands':
                this.drawFloatingIslands(ctx, layer, width, height, offset);
                break;
            case 'smoke':
                this.drawSmoke(ctx, layer, width, height);
                break;
            case 'mist':
                this.drawMist(ctx, layer, width, height);
                break;
        }
    }

    drawMountains(ctx, layer, width, height, offset) {
        const baseY = height * layer.yOffset;
        ctx.fillStyle = layer.color;
        ctx.beginPath();
        ctx.moveTo(0, height);

        const peaks = 8;
        const peakWidth = (width + 200) / peaks;

        for (let i = -1; i <= peaks; i++) {
            const x = i * peakWidth - (offset % peakWidth);
            const peakHeight = 80 + Math.sin(i * 1.5) * 40;
            ctx.lineTo(x, baseY + Math.sin(i * 0.8) * 20);
            ctx.lineTo(x + peakWidth / 2, baseY - peakHeight);
        }

        ctx.lineTo(width, height);
        ctx.closePath();
        ctx.fill();
    }

    drawClouds(ctx, layer, width, height, offset) {
        ctx.fillStyle = layer.color;
        for (let i = 0; i < layer.count; i++) {
            const baseX = (i * (width / layer.count) + offset * (i % 2 === 0 ? 1 : -0.5)) % (width + 200) - 100;
            const baseY = 80 + (i % 3) * 60;
            this.drawCloud(ctx, baseX, baseY, 60 + (i % 2) * 30);
        }
    }

    drawCloud(ctx, x, y, size) {
        ctx.beginPath();
        ctx.arc(x, y, size * 0.5, 0, Math.PI * 2);
        ctx.arc(x + size * 0.4, y - size * 0.1, size * 0.4, 0, Math.PI * 2);
        ctx.arc(x + size * 0.8, y, size * 0.45, 0, Math.PI * 2);
        ctx.arc(x + size * 0.4, y + size * 0.15, size * 0.35, 0, Math.PI * 2);
        ctx.fill();
    }

    drawTrees(ctx, layer, width, height, offset) {
        const baseY = height * layer.yOffset;
        const scale = layer.scale || 1;
        ctx.fillStyle = layer.color;

        for (let i = -1; i < 12; i++) {
            const x = (i * 120 - offset * 0.5) % (width + 120) - 60;
            const treeHeight = (80 + Math.sin(i * 2) * 30) * scale;

            // Tree trunk
            ctx.fillRect(x - 5 * scale, baseY, 10 * scale, treeHeight * 0.3);

            // Tree foliage (triangle)
            ctx.beginPath();
            ctx.moveTo(x, baseY - treeHeight);
            ctx.lineTo(x - 30 * scale, baseY);
            ctx.lineTo(x + 30 * scale, baseY);
            ctx.closePath();
            ctx.fill();
        }
    }

    drawNebula(ctx, layer, width, height) {
        const gradient = ctx.createRadialGradient(
            width * 0.3, height * 0.3, 0,
            width * 0.3, height * 0.3, 300
        );
        gradient.addColorStop(0, layer.colors[0] + '40');
        gradient.addColorStop(1, 'transparent');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);

        const gradient2 = ctx.createRadialGradient(
            width * 0.7, height * 0.5, 0,
            width * 0.7, height * 0.5, 250
        );
        gradient2.addColorStop(0, layer.colors[1] + '30');
        gradient2.addColorStop(1, 'transparent');
        ctx.fillStyle = gradient2;
        ctx.fillRect(0, 0, width, height);
    }

    drawEnergyStreams(ctx, layer, width, height) {
        ctx.strokeStyle = layer.color;
        ctx.lineWidth = 2;
        ctx.globalAlpha = 0.3;

        for (let i = 0; i < layer.count; i++) {
            const y = 100 + i * 150;
            ctx.beginPath();
            for (let x = 0; x < width; x += 10) {
                const wave = Math.sin((x + this.time * 100) * 0.02 + i) * 20;
                if (x === 0) ctx.moveTo(x, y + wave);
                else ctx.lineTo(x, y + wave);
            }
            ctx.stroke();
        }
        ctx.globalAlpha = 1;
    }

    drawFloatingIslands(ctx, layer, width, height, offset) {
        ctx.fillStyle = layer.color;
        for (let i = 0; i < layer.count; i++) {
            const x = (200 + i * 400 - offset) % (width + 200) - 100;
            const y = 150 + Math.sin(this.time * 0.5 + i) * 20 + (i % 2) * 80;
            const size = 60 + (i % 2) * 30;

            // Island shape
            ctx.beginPath();
            ctx.ellipse(x, y + 10, size, size * 0.3, 0, 0, Math.PI * 2);
            ctx.fill();

            // Grass on top
            ctx.fillStyle = '#4a8a3a';
            ctx.beginPath();
            ctx.ellipse(x, y, size * 0.9, size * 0.2, 0, Math.PI, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = layer.color;
        }
    }

    drawSmoke(ctx, layer, width, height) {
        ctx.fillStyle = layer.color;
        for (let i = 0; i < layer.count; i++) {
            const x = 100 + i * 150;
            const baseY = height * 0.6;
            const yOffset = Math.sin(this.time * 0.5 + i * 0.7) * 30;
            const size = 40 + Math.sin(this.time + i) * 15;

            ctx.beginPath();
            ctx.arc(x, baseY + yOffset - size, size, 0, Math.PI * 2);
            ctx.arc(x + size * 0.5, baseY + yOffset - size * 1.5, size * 0.7, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    drawMist(ctx, layer, width, height) {
        const gradient = ctx.createLinearGradient(0, height * 0.6, 0, height);
        gradient.addColorStop(0, 'transparent');
        gradient.addColorStop(0.5, layer.color);
        gradient.addColorStop(1, layer.color);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, height * 0.6, width, height * 0.4);
    }

    renderParticles(ctx) {
        for (const p of this.particles) {
            if (p.type === 'sparkles' || p.type === 'stars') {
                const twinkle = (Math.sin(this.time * 3 + p.twinkle) + 1) / 2;
                ctx.fillStyle = `rgba(255, 255, 255, ${0.3 + twinkle * 0.7})`;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size * (0.5 + twinkle * 0.5), 0, Math.PI * 2);
                ctx.fill();
            } else if (p.type === 'ember') {
                const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size);
                gradient.addColorStop(0, `rgba(255, 200, 50, ${p.life})`);
                gradient.addColorStop(1, `rgba(255, 100, 0, 0)`);
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fill();
            } else if (p.type === 'firefly') {
                const glow = (Math.sin(this.time * 2 + p.glowPhase) + 1) / 2;
                if (glow > 0.3) {
                    ctx.fillStyle = `rgba(200, 255, 100, ${glow * 0.8})`;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, 3 + glow * 3, 0, Math.PI * 2);
                    ctx.fill();
                }
            } else if (p.type === 'bird') {
                ctx.fillStyle = '#333';
                ctx.save();
                ctx.translate(p.x, p.y);
                // Body
                ctx.beginPath();
                ctx.ellipse(0, 0, 8, 4, 0, 0, Math.PI * 2);
                ctx.fill();
                // Wings
                const wingAngle = Math.sin(p.wingPhase) * 0.5;
                ctx.rotate(wingAngle);
                ctx.beginPath();
                ctx.moveTo(-3, 0);
                ctx.lineTo(-12, -8);
                ctx.lineTo(-8, 0);
                ctx.fill();
                ctx.beginPath();
                ctx.moveTo(-3, 0);
                ctx.lineTo(-12, 8);
                ctx.lineTo(-8, 0);
                ctx.fill();
                ctx.restore();
            }
        }
    }
}

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

        // Character colors (fallback for non-sprite rendering)
        this.characterColors = {
            'Blaze': '#FF4500',
            'Tank': '#4169E1',
            'Shadow': '#8A2BE2',
            'Storm': '#FFD700'
        };

        // Effects
        this.effects = [];

        // Particle system
        this.particles = [];

        // Screen shake
        this.screenShake = { intensity: 0, duration: 0, startTime: 0 };

        // Previous player states for detecting changes
        this.previousPlayerStates = {};

        // Initialize sprite system
        this.spritesReady = false;
        this.initSprites();

        // Initialize background renderer
        this.backgroundRenderer = new BackgroundRenderer();

        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    async initSprites() {
        if (typeof spriteManager !== 'undefined') {
            await spriteManager.init();
            this.spritesReady = spriteManager.ready;
            console.log('Sprites initialized:', this.spritesReady);
        }
    }

    // Add screen shake effect
    addScreenShake(intensity, duration) {
        this.screenShake = {
            intensity: intensity,
            duration: duration,
            startTime: performance.now()
        };
    }

    // Spawn dust particles when landing
    spawnLandingDust(x, y) {
        for (let i = 0; i < 8; i++) {
            this.particles.push({
                x: x,
                y: y,
                vx: (Math.random() - 0.5) * 4,
                vy: -Math.random() * 2 - 1,
                size: Math.random() * 6 + 3,
                color: 'rgba(139, 119, 101, 0.7)',
                life: 1,
                decay: 0.02 + Math.random() * 0.02,
                type: 'dust'
            });
        }
    }

    // Spawn hit particles
    spawnHitParticles(x, y, color) {
        for (let i = 0; i < 12; i++) {
            const angle = (Math.PI * 2 * i) / 12;
            const speed = Math.random() * 5 + 3;
            this.particles.push({
                x: x,
                y: y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                size: Math.random() * 8 + 4,
                color: color,
                life: 1,
                decay: 0.03 + Math.random() * 0.02,
                type: 'hit'
            });
        }
    }

    // Spawn motion trail
    spawnMotionTrail(x, y, color) {
        this.particles.push({
            x: x,
            y: y - 40,
            vx: 0,
            vy: 0,
            size: 30,
            color: color,
            life: 0.5,
            decay: 0.05,
            type: 'trail'
        });
    }

    // Update particles
    updateParticles() {
        this.particles = this.particles.filter(p => {
            p.x += p.vx;
            p.y += p.vy;
            p.life -= p.decay;

            if (p.type === 'dust') {
                p.vy += 0.1; // gravity
                p.size *= 0.98;
            } else if (p.type === 'hit') {
                p.vx *= 0.95;
                p.vy *= 0.95;
            }

            return p.life > 0;
        });
    }

    // Draw particles
    drawParticles() {
        this.particles.forEach(p => {
            this.ctx.globalAlpha = p.life;
            this.ctx.fillStyle = p.color;

            if (p.type === 'trail') {
                this.ctx.beginPath();
                this.ctx.ellipse(p.x, p.y, p.size, p.size * 0.6, 0, 0, Math.PI * 2);
                this.ctx.fill();
            } else {
                this.ctx.beginPath();
                this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                this.ctx.fill();
            }
        });
        this.ctx.globalAlpha = 1;
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

        // Update background animation
        this.backgroundRenderer.update(dt);

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Apply scale
        this.ctx.save();
        this.ctx.scale(this.scale, this.scale);

        // Apply screen shake
        const shakeElapsed = performance.now() - this.screenShake.startTime;
        if (shakeElapsed < this.screenShake.duration) {
            const shakeProgress = 1 - (shakeElapsed / this.screenShake.duration);
            const shakeX = (Math.random() - 0.5) * this.screenShake.intensity * shakeProgress;
            const shakeY = (Math.random() - 0.5) * this.screenShake.intensity * shakeProgress;
            this.ctx.translate(shakeX, shakeY);
        }

        // Draw arena background with parallax
        this.drawArena();

        // Draw platforms with themed styling
        if (this.gameState.arena && this.gameState.arena.platforms) {
            this.gameState.arena.platforms.forEach(p => this.drawPlatform(p));
        } else if (this.gameState.arena && this.gameState.arena.obstacles) {
            // Fallback for legacy obstacle format
            this.gameState.arena.obstacles.forEach(obs => this.drawObstacle(obs));
        }

        // Draw hazards (like lava)
        if (this.gameState.arena && this.gameState.arena.has_hazard) {
            this.drawHazard();
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

        // Draw particles (behind players)
        this.drawParticles();

        // Draw players and detect state changes
        if (this.gameState.players) {
            this.gameState.players.forEach(player => {
                this.detectPlayerStateChanges(player);
                this.drawPlayer(player, timestamp);
            });
        }

        // Draw effects
        this.drawEffects();

        this.ctx.restore();

        // Update effects and particles
        this.updateEffects();
        this.updateParticles();
    }

    // Detect player state changes for triggering effects
    detectPlayerStateChanges(player) {
        const prev = this.previousPlayerStates[player.id];
        const color = this.characterColors[player.character] || '#FFFFFF';

        if (prev) {
            // Detect landing (was in air, now on ground)
            if ((prev.animation === 'jump' || prev.animation === 'fall') &&
                (player.animation === 'idle' || player.animation === 'walk')) {
                this.spawnLandingDust(player.x, player.y);
            }

            // Detect getting hit (entering stunned state)
            if (prev.animation !== 'stunned' && player.animation === 'stunned') {
                this.spawnHitParticles(player.x, player.y - 40, color);
                this.addScreenShake(15, 200);
            }

            // Detect heavy attack hit (check for damage dealt)
            if (prev.animation && prev.animation.includes('attack_heavy') && player.animation !== prev.animation) {
                // Add slight screen shake on heavy attack
                this.addScreenShake(8, 150);
            }

            // Detect special ability
            if (prev.animation !== 'special' && player.animation === 'special') {
                this.addScreenShake(12, 300);
            }

            // Motion trails during fast movement/attacks
            if ((player.animation === 'special' || player.animation === 'attack_heavy') &&
                this.animationFrame % 3 === 0) {
                this.spawnMotionTrail(player.x, player.y, color + '40');
            }
        }

        // Store current state
        this.previousPlayerStates[player.id] = {
            x: player.x,
            y: player.y,
            animation: player.animation,
            hp: player.hp
        };
    }

    drawArena() {
        const arena = this.gameState.arena;
        if (!arena) return;

        // Set theme for background renderer based on stage theme
        const themeMap = {
            'battlefield': 'battlefield',
            'space': 'space',
            'volcano': 'volcano',
            'sky': 'sky',
            'forest': 'forest'
        };
        const theme = themeMap[arena.theme] || 'battlefield';
        this.backgroundRenderer.setTheme(theme);

        // Draw animated parallax background
        this.backgroundRenderer.render(this.ctx, this.arenaWidth, this.arenaHeight);
    }

    drawPlatform(platform) {
        const { x, y, width, height, theme, platform_type, is_moving } = platform;

        this.ctx.save();

        // Draw based on theme
        switch (theme) {
            case 'grass':
                this.drawGrassPlatform(x, y, width, height, platform_type === 'solid');
                break;
            case 'tech':
                this.drawTechPlatform(x, y, width, height, platform_type === 'solid');
                break;
            case 'rock':
                this.drawRockPlatform(x, y, width, height, platform_type === 'solid');
                break;
            case 'cloud':
                this.drawCloudPlatform(x, y, width, height, platform_type === 'solid');
                break;
            case 'wood':
                this.drawWoodPlatform(x, y, width, height, platform_type === 'solid');
                break;
            default:
                // Fallback simple platform
                this.ctx.fillStyle = '#666';
                this.ctx.fillRect(x, y, width, height);
        }

        // Moving platform indicator
        if (is_moving) {
            this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
            this.ctx.lineWidth = 2;
            this.ctx.setLineDash([5, 5]);
            this.ctx.strokeRect(x - 2, y - 2, width + 4, height + 4);
            this.ctx.setLineDash([]);
        }

        this.ctx.restore();
    }

    drawGrassPlatform(x, y, width, height, isSolid) {
        // Main platform body
        const gradient = this.ctx.createLinearGradient(x, y, x, y + height);
        gradient.addColorStop(0, '#5a8c2a');
        gradient.addColorStop(0.3, '#4a7c23');
        gradient.addColorStop(1, '#3a6c1a');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(x, y, width, height);

        // Grass tufts on top
        this.ctx.fillStyle = '#6a9c3a';
        for (let i = 0; i < width; i += 8) {
            const tuftHeight = 4 + Math.sin(i * 0.5) * 2;
            this.ctx.beginPath();
            this.ctx.moveTo(x + i, y);
            this.ctx.lineTo(x + i + 3, y - tuftHeight);
            this.ctx.lineTo(x + i + 6, y);
            this.ctx.fill();
        }

        // Edge highlight
        this.ctx.strokeStyle = '#7aac4a';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);
        this.ctx.lineTo(x + width, y);
        this.ctx.stroke();
    }

    drawTechPlatform(x, y, width, height, isSolid) {
        // Metallic body
        const gradient = this.ctx.createLinearGradient(x, y, x, y + height);
        gradient.addColorStop(0, '#4a6a9e');
        gradient.addColorStop(0.5, '#3a5a8e');
        gradient.addColorStop(1, '#2a4a7e');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(x, y, width, height);

        // Glowing edge
        this.ctx.strokeStyle = '#00ffff';
        this.ctx.lineWidth = 2;
        this.ctx.shadowColor = '#00ffff';
        this.ctx.shadowBlur = 10;
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);
        this.ctx.lineTo(x + width, y);
        this.ctx.stroke();
        this.ctx.shadowBlur = 0;

        // Circuit pattern
        this.ctx.strokeStyle = 'rgba(0, 255, 255, 0.3)';
        this.ctx.lineWidth = 1;
        for (let i = 20; i < width; i += 40) {
            this.ctx.beginPath();
            this.ctx.moveTo(x + i, y + 5);
            this.ctx.lineTo(x + i, y + height - 5);
            this.ctx.stroke();
        }
    }

    drawRockPlatform(x, y, width, height, isSolid) {
        // Rocky body with irregular edges
        const gradient = this.ctx.createLinearGradient(x, y, x, y + height);
        gradient.addColorStop(0, '#8b6b4b');
        gradient.addColorStop(0.5, '#6b4423');
        gradient.addColorStop(1, '#4b3413');
        this.ctx.fillStyle = gradient;

        // Draw slightly irregular shape
        this.ctx.beginPath();
        this.ctx.moveTo(x + 5, y);
        this.ctx.lineTo(x + width - 3, y + 2);
        this.ctx.lineTo(x + width, y + height);
        this.ctx.lineTo(x, y + height - 2);
        this.ctx.closePath();
        this.ctx.fill();

        // Lava cracks (glowing lines)
        this.ctx.strokeStyle = '#ff6600';
        this.ctx.lineWidth = 2;
        this.ctx.shadowColor = '#ff3300';
        this.ctx.shadowBlur = 5;
        for (let i = 30; i < width; i += 50) {
            this.ctx.beginPath();
            this.ctx.moveTo(x + i, y + 3);
            this.ctx.lineTo(x + i + 10, y + height / 2);
            this.ctx.lineTo(x + i + 5, y + height - 3);
            this.ctx.stroke();
        }
        this.ctx.shadowBlur = 0;
    }

    drawCloudPlatform(x, y, width, height, isSolid) {
        // Fluffy cloud shape
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        this.ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';
        this.ctx.shadowBlur = 10;
        this.ctx.shadowOffsetY = 5;

        // Draw cloud puffs
        const puffCount = Math.floor(width / 40) + 1;
        for (let i = 0; i < puffCount; i++) {
            const puffX = x + (i * width / puffCount) + (width / puffCount / 2);
            const puffSize = 25 + Math.sin(i * 1.5) * 8;
            this.ctx.beginPath();
            this.ctx.arc(puffX, y + height / 2, puffSize, 0, Math.PI * 2);
            this.ctx.fill();
        }

        // Top flat area
        this.ctx.fillRect(x + 10, y, width - 20, height / 2);

        this.ctx.shadowBlur = 0;
        this.ctx.shadowOffsetY = 0;
    }

    drawWoodPlatform(x, y, width, height, isSolid) {
        // Wood grain body
        const gradient = this.ctx.createLinearGradient(x, y, x, y + height);
        gradient.addColorStop(0, '#a0724a');
        gradient.addColorStop(0.5, '#8b5a2b');
        gradient.addColorStop(1, '#6b4a1b');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(x, y, width, height);

        // Wood grain lines
        this.ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
        this.ctx.lineWidth = 1;
        for (let i = 0; i < height; i += 4) {
            const wave = Math.sin((y + i) * 0.1) * 3;
            this.ctx.beginPath();
            this.ctx.moveTo(x, y + i);
            this.ctx.bezierCurveTo(
                x + width * 0.3, y + i + wave,
                x + width * 0.7, y + i - wave,
                x + width, y + i
            );
            this.ctx.stroke();
        }

        // Moss patches
        this.ctx.fillStyle = 'rgba(80, 120, 60, 0.5)';
        for (let i = 0; i < 3; i++) {
            const mossX = x + (i * width / 3) + Math.random() * 20;
            const mossSize = 8 + Math.random() * 6;
            this.ctx.beginPath();
            this.ctx.arc(mossX, y + 2, mossSize, Math.PI, 0);
            this.ctx.fill();
        }

        // Edge highlight
        this.ctx.strokeStyle = '#b0825a';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(x, y, width, height);
    }

    drawHazard() {
        const arena = this.gameState.arena;
        if (!arena || !arena.has_hazard) return;

        const hazardY = arena.hazard_y || 680;

        if (arena.hazard_type === 'lava') {
            // Lava gradient
            const gradient = this.ctx.createLinearGradient(0, hazardY, 0, this.arenaHeight);
            gradient.addColorStop(0, '#ff4400');
            gradient.addColorStop(0.3, '#ff2200');
            gradient.addColorStop(1, '#aa0000');
            this.ctx.fillStyle = gradient;
            this.ctx.fillRect(0, hazardY, this.arenaWidth, this.arenaHeight - hazardY);

            // Lava glow
            this.ctx.shadowColor = '#ff6600';
            this.ctx.shadowBlur = 30;
            this.ctx.fillRect(0, hazardY, this.arenaWidth, 5);
            this.ctx.shadowBlur = 0;

            // Animated bubbles
            for (let i = 0; i < 8; i++) {
                const bubbleX = (i * 160 + this.animationFrame * 0.5) % this.arenaWidth;
                const bubbleY = hazardY + 10 + Math.sin(this.animationFrame * 0.1 + i) * 5;
                const bubbleSize = 5 + Math.sin(this.animationFrame * 0.2 + i * 0.7) * 3;

                this.ctx.fillStyle = '#ffaa00';
                this.ctx.beginPath();
                this.ctx.arc(bubbleX, bubbleY, bubbleSize, 0, Math.PI * 2);
                this.ctx.fill();
            }
        }
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

    drawPlayer(player, timestamp = performance.now()) {
        const { x, y, character, facing_right, hp, max_hp, state, animation, is_invincible, name, combo_count } = player;

        const color = this.characterColors[character] || '#FFFFFF';
        const isLocal = player.id === this.localPlayerId;

        // Player dimensions (for fallback and health bar positioning)
        const width = 50;
        const height = 80;

        this.ctx.save();

        // Invincibility flash
        if (is_invincible && this.animationFrame % 10 < 5) {
            this.ctx.globalAlpha = 0.5;
        }

        // Dead state
        if (state === 'dead') {
            this.ctx.globalAlpha = 0.3;
        }

        // Try to draw sprite, fall back to shapes if not available
        let spriteDrawn = false;
        if (this.spritesReady && typeof spriteManager !== 'undefined') {
            spriteDrawn = spriteManager.drawSprite(this.ctx, player, timestamp);
        }

        // Fallback to shape-based rendering
        if (!spriteDrawn) {
            this.ctx.save();
            this.ctx.translate(x, y);

            // Flip if facing left
            if (!facing_right) {
                this.ctx.scale(-1, 1);
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

            this.ctx.restore();
        }

        this.ctx.restore();

        // Attack effect overlay (works with both sprite and fallback)
        if (state === 'attacking' || (animation && animation.includes('attack'))) {
            this.ctx.save();
            this.ctx.translate(x, y);
            if (!facing_right) {
                this.ctx.scale(-1, 1);
            }
            this.ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            this.ctx.beginPath();
            this.ctx.arc(width/2 + 20, -height/2, 25, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.restore();
        }

        // Blocking stance effect
        if (state === 'blocking' || animation === 'blocking') {
            this.ctx.strokeStyle = '#4ECDC4';
            this.ctx.lineWidth = 4;
            this.ctx.beginPath();
            this.ctx.arc(x, y - height/2, 45, 0, Math.PI * 2);
            this.ctx.stroke();
        }

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

}

// Global renderer instance
let gameRenderer = null;
