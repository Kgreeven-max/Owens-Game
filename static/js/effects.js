/**
 * Arena Brawl - Visual Effects System
 * Hit sparks, screen shake, freeze frames, knockback trails, and particles
 */

class EffectsManager {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Active effects
        this.particles = [];
        this.hitSparks = [];
        this.trails = [];
        this.screenShake = { x: 0, y: 0, duration: 0, intensity: 0 };
        this.freezeFrames = 0;
        this.flashEffect = { active: false, color: 'white', alpha: 0 };

        // Effect pools for performance
        this.particlePool = [];
        this.maxParticles = 200;

        // Camera offset for screen shake
        this.cameraOffset = { x: 0, y: 0 };
    }

    /**
     * Update all effects
     */
    update(dt) {
        // Handle freeze frames
        if (this.freezeFrames > 0) {
            this.freezeFrames--;
            return true; // Signal game to pause
        }

        // Update screen shake
        this.updateScreenShake(dt);

        // Update particles
        this.updateParticles(dt);

        // Update hit sparks
        this.updateHitSparks(dt);

        // Update trails
        this.updateTrails(dt);

        // Update flash effect
        this.updateFlash(dt);

        return false; // Game continues normally
    }

    /**
     * Render all effects
     */
    render(ctx) {
        // Apply screen shake offset
        ctx.save();
        ctx.translate(this.cameraOffset.x, this.cameraOffset.y);

        // Render trails (behind everything)
        this.renderTrails(ctx);

        // Render particles
        this.renderParticles(ctx);

        // Render hit sparks
        this.renderHitSparks(ctx);

        ctx.restore();

        // Render flash effect (on top of everything)
        this.renderFlash(ctx);
    }

    // ============================================
    // HIT EFFECTS
    // ============================================

    /**
     * Create hit spark effect at position
     */
    createHitSpark(x, y, damage, angle = 0, type = 'normal') {
        const spark = {
            x, y,
            angle: angle * (Math.PI / 180), // Convert to radians
            scale: Math.min(1 + damage * 0.03, 2.5),
            frame: 0,
            maxFrames: 12,
            type, // 'normal', 'critical', 'electric', 'fire', 'ice'
            rotation: Math.random() * Math.PI * 2
        };

        this.hitSparks.push(spark);

        // Add particles based on damage
        const particleCount = Math.min(5 + Math.floor(damage / 5), 20);
        this.createHitParticles(x, y, angle, particleCount, type);

        // Screen shake based on damage
        const shakeIntensity = Math.min(3 + damage * 0.15, 15);
        const shakeDuration = Math.min(100 + damage * 2, 300);
        this.addScreenShake(shakeIntensity, shakeDuration);

        // Freeze frames for impactful hits
        if (damage >= 15) {
            this.freezeFrames = Math.min(2 + Math.floor(damage / 10), 6);
        }
    }

    /**
     * Create particles from hit
     */
    createHitParticles(x, y, angle, count, type) {
        const colors = this.getParticleColors(type);
        const angleRad = angle * (Math.PI / 180);

        for (let i = 0; i < count; i++) {
            // Spread particles in hit direction
            const spreadAngle = angleRad + (Math.random() - 0.5) * Math.PI * 0.5;
            const speed = 3 + Math.random() * 5;

            const particle = this.getParticle();
            particle.x = x;
            particle.y = y;
            particle.vx = Math.cos(spreadAngle) * speed;
            particle.vy = Math.sin(spreadAngle) * speed - 2; // Slight upward bias
            particle.size = 2 + Math.random() * 4;
            particle.color = colors[Math.floor(Math.random() * colors.length)];
            particle.life = 1.0;
            particle.decay = 0.02 + Math.random() * 0.02;
            particle.gravity = 0.15;
            particle.type = 'hit';

            this.particles.push(particle);
        }
    }

    /**
     * Get particle colors based on effect type
     */
    getParticleColors(type) {
        const colorSets = {
            normal: ['#ffffff', '#ffff00', '#ff8800', '#ff4400'],
            critical: ['#ff0000', '#ff4400', '#ff8800', '#ffffff'],
            electric: ['#00ffff', '#00aaff', '#ffffff', '#88ffff'],
            fire: ['#ff4400', '#ff8800', '#ffcc00', '#ff0000'],
            ice: ['#88ffff', '#aaffff', '#ffffff', '#44ccff']
        };
        return colorSets[type] || colorSets.normal;
    }

    updateHitSparks(dt) {
        for (let i = this.hitSparks.length - 1; i >= 0; i--) {
            const spark = this.hitSparks[i];
            spark.frame++;

            if (spark.frame >= spark.maxFrames) {
                this.hitSparks.splice(i, 1);
            }
        }
    }

    renderHitSparks(ctx) {
        for (const spark of this.hitSparks) {
            this.drawHitSpark(ctx, spark);
        }
    }

    drawHitSpark(ctx, spark) {
        const progress = spark.frame / spark.maxFrames;
        const alpha = 1 - progress;
        const scale = spark.scale * (1 + progress * 0.5);

        ctx.save();
        ctx.translate(spark.x, spark.y);
        ctx.rotate(spark.rotation);
        ctx.scale(scale, scale);
        ctx.globalAlpha = alpha;

        // Draw spark based on type
        switch (spark.type) {
            case 'electric':
                this.drawElectricSpark(ctx, progress);
                break;
            case 'fire':
                this.drawFireSpark(ctx, progress);
                break;
            case 'ice':
                this.drawIceSpark(ctx, progress);
                break;
            case 'critical':
                this.drawCriticalSpark(ctx, progress);
                break;
            default:
                this.drawNormalSpark(ctx, progress);
        }

        ctx.restore();
    }

    drawNormalSpark(ctx, progress) {
        // Starburst effect
        const rays = 8;
        const innerRadius = 5 * (1 - progress);
        const outerRadius = 25 + 15 * progress;

        ctx.beginPath();
        for (let i = 0; i < rays; i++) {
            const angle = (i / rays) * Math.PI * 2;
            const nextAngle = ((i + 0.5) / rays) * Math.PI * 2;

            ctx.lineTo(
                Math.cos(angle) * outerRadius,
                Math.sin(angle) * outerRadius
            );
            ctx.lineTo(
                Math.cos(nextAngle) * innerRadius,
                Math.sin(nextAngle) * innerRadius
            );
        }
        ctx.closePath();

        // Gradient fill
        const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, outerRadius);
        gradient.addColorStop(0, '#ffffff');
        gradient.addColorStop(0.3, '#ffff00');
        gradient.addColorStop(0.7, '#ff8800');
        gradient.addColorStop(1, 'rgba(255,68,0,0)');

        ctx.fillStyle = gradient;
        ctx.fill();
    }

    drawElectricSpark(ctx, progress) {
        // Lightning bolts
        const bolts = 6;
        const maxLength = 30 + 20 * progress;

        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 2;
        ctx.shadowColor = '#00ffff';
        ctx.shadowBlur = 10;

        for (let i = 0; i < bolts; i++) {
            const angle = (i / bolts) * Math.PI * 2 + progress * 0.5;
            ctx.beginPath();
            ctx.moveTo(0, 0);

            let x = 0, y = 0;
            const segments = 4;
            for (let j = 0; j < segments; j++) {
                const segLen = maxLength / segments;
                x += Math.cos(angle) * segLen + (Math.random() - 0.5) * 10;
                y += Math.sin(angle) * segLen + (Math.random() - 0.5) * 10;
                ctx.lineTo(x, y);
            }
            ctx.stroke();
        }

        ctx.shadowBlur = 0;
    }

    drawFireSpark(ctx, progress) {
        // Flame burst
        const flames = 10;

        for (let i = 0; i < flames; i++) {
            const angle = (i / flames) * Math.PI * 2;
            const length = 20 + Math.random() * 15 + progress * 10;

            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.quadraticCurveTo(
                Math.cos(angle) * length * 0.5 + (Math.random() - 0.5) * 10,
                Math.sin(angle) * length * 0.5 + (Math.random() - 0.5) * 10,
                Math.cos(angle) * length,
                Math.sin(angle) * length
            );

            const gradient = ctx.createLinearGradient(0, 0,
                Math.cos(angle) * length, Math.sin(angle) * length);
            gradient.addColorStop(0, '#ffffff');
            gradient.addColorStop(0.3, '#ffcc00');
            gradient.addColorStop(0.6, '#ff4400');
            gradient.addColorStop(1, 'rgba(255,0,0,0)');

            ctx.strokeStyle = gradient;
            ctx.lineWidth = 4;
            ctx.stroke();
        }
    }

    drawIceSpark(ctx, progress) {
        // Ice crystal shatter
        const shards = 8;

        ctx.fillStyle = '#88ffff';
        ctx.shadowColor = '#00ffff';
        ctx.shadowBlur = 5;

        for (let i = 0; i < shards; i++) {
            const angle = (i / shards) * Math.PI * 2;
            const dist = 15 + progress * 20;

            ctx.save();
            ctx.translate(Math.cos(angle) * dist, Math.sin(angle) * dist);
            ctx.rotate(angle + progress);

            // Diamond shape
            ctx.beginPath();
            ctx.moveTo(0, -8);
            ctx.lineTo(4, 0);
            ctx.lineTo(0, 8);
            ctx.lineTo(-4, 0);
            ctx.closePath();
            ctx.fill();

            ctx.restore();
        }

        ctx.shadowBlur = 0;
    }

    drawCriticalSpark(ctx, progress) {
        // Big dramatic spark
        const rays = 12;
        const outerRadius = 40 + 25 * progress;

        // Outer glow
        const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, outerRadius);
        gradient.addColorStop(0, 'rgba(255,255,255,1)');
        gradient.addColorStop(0.2, 'rgba(255,0,0,0.8)');
        gradient.addColorStop(0.5, 'rgba(255,68,0,0.4)');
        gradient.addColorStop(1, 'rgba(255,0,0,0)');

        ctx.beginPath();
        ctx.arc(0, 0, outerRadius, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();

        // Sharp rays
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 3;

        for (let i = 0; i < rays; i++) {
            const angle = (i / rays) * Math.PI * 2;
            const length = outerRadius * (0.8 + Math.random() * 0.4);

            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(Math.cos(angle) * length, Math.sin(angle) * length);
            ctx.stroke();
        }
    }

    // ============================================
    // SCREEN SHAKE
    // ============================================

    addScreenShake(intensity, duration) {
        // Don't reduce existing shake, only increase
        if (intensity > this.screenShake.intensity) {
            this.screenShake.intensity = intensity;
        }
        if (duration > this.screenShake.duration) {
            this.screenShake.duration = duration;
        }
    }

    updateScreenShake(dt) {
        if (this.screenShake.duration > 0) {
            this.screenShake.duration -= dt * 1000;

            const progress = Math.max(0, this.screenShake.duration / 300);
            const currentIntensity = this.screenShake.intensity * progress;

            this.cameraOffset.x = (Math.random() - 0.5) * 2 * currentIntensity;
            this.cameraOffset.y = (Math.random() - 0.5) * 2 * currentIntensity;
        } else {
            this.cameraOffset.x = 0;
            this.cameraOffset.y = 0;
            this.screenShake.intensity = 0;
        }
    }

    // ============================================
    // PARTICLES
    // ============================================

    getParticle() {
        if (this.particlePool.length > 0) {
            return this.particlePool.pop();
        }
        return {};
    }

    returnParticle(particle) {
        if (this.particlePool.length < 50) {
            this.particlePool.push(particle);
        }
    }

    updateParticles(dt) {
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];

            // Physics
            p.x += p.vx;
            p.y += p.vy;
            p.vy += p.gravity || 0;
            p.vx *= 0.98; // Air resistance

            // Decay
            p.life -= p.decay;

            if (p.life <= 0) {
                this.returnParticle(this.particles.splice(i, 1)[0]);
            }
        }
    }

    renderParticles(ctx) {
        for (const p of this.particles) {
            ctx.globalAlpha = p.life;
            ctx.fillStyle = p.color;

            if (p.type === 'hit') {
                // Glowing particle
                ctx.shadowColor = p.color;
                ctx.shadowBlur = 5;
            }

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
            ctx.fill();

            ctx.shadowBlur = 0;
        }
        ctx.globalAlpha = 1;
    }

    // ============================================
    // TRAILS
    // ============================================

    /**
     * Create knockback trail for player
     */
    createKnockbackTrail(player, intensity) {
        const trail = {
            points: [{ x: player.x, y: player.y }],
            color: this.getCharacterColor(player.character),
            width: 4 + intensity * 0.5,
            life: 1.0,
            decay: 0.05,
            playerId: player.id
        };

        this.trails.push(trail);
        return trail;
    }

    /**
     * Add point to existing trail
     */
    addTrailPoint(trail, x, y) {
        trail.points.push({ x, y });
        if (trail.points.length > 20) {
            trail.points.shift();
        }
    }

    getCharacterColor(character) {
        const colors = {
            'Blaze': '#ff4400',
            'Tank': '#888888',
            'Shadow': '#440088',
            'Storm': '#00aaff',
            'Frost': '#88ffff',
            'Titan': '#8b4513',
            'Whisper': '#ff00ff',
            'Volt': '#ffff00',
            'Golem': '#666666',
            'Aria': '#aaffaa',
            'Fang': '#884400',
            'Nova': '#ff8800'
        };
        return colors[character] || '#ffffff';
    }

    updateTrails(dt) {
        for (let i = this.trails.length - 1; i >= 0; i--) {
            const trail = this.trails[i];
            trail.life -= trail.decay;

            if (trail.life <= 0) {
                this.trails.splice(i, 1);
            }
        }
    }

    renderTrails(ctx) {
        for (const trail of this.trails) {
            if (trail.points.length < 2) continue;

            ctx.globalAlpha = trail.life * 0.6;
            ctx.strokeStyle = trail.color;
            ctx.lineWidth = trail.width * trail.life;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';

            ctx.beginPath();
            ctx.moveTo(trail.points[0].x, trail.points[0].y);

            for (let i = 1; i < trail.points.length; i++) {
                ctx.lineTo(trail.points[i].x, trail.points[i].y);
            }

            ctx.stroke();
        }
        ctx.globalAlpha = 1;
    }

    // ============================================
    // FLASH EFFECT
    // ============================================

    /**
     * Flash screen (for big KOs, etc.)
     */
    flashScreen(color = 'white', duration = 100) {
        this.flashEffect.active = true;
        this.flashEffect.color = color;
        this.flashEffect.alpha = 0.8;
        this.flashEffect.duration = duration;
    }

    updateFlash(dt) {
        if (this.flashEffect.active) {
            this.flashEffect.alpha -= dt * 5;
            if (this.flashEffect.alpha <= 0) {
                this.flashEffect.active = false;
                this.flashEffect.alpha = 0;
            }
        }
    }

    renderFlash(ctx) {
        if (this.flashEffect.active && this.flashEffect.alpha > 0) {
            ctx.fillStyle = this.flashEffect.color;
            ctx.globalAlpha = this.flashEffect.alpha;
            ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            ctx.globalAlpha = 1;
        }
    }

    // ============================================
    // SPECIAL EFFECTS
    // ============================================

    /**
     * Create KO blast effect
     */
    createKOBlast(x, y, direction) {
        // Big flash
        this.flashScreen('#ff4400', 150);

        // Intense shake
        this.addScreenShake(20, 400);

        // Freeze frames
        this.freezeFrames = 8;

        // Explosion particles
        const colors = ['#ff4400', '#ff8800', '#ffcc00', '#ffffff'];
        for (let i = 0; i < 40; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = 5 + Math.random() * 10;

            const particle = this.getParticle();
            particle.x = x;
            particle.y = y;
            particle.vx = Math.cos(angle) * speed;
            particle.vy = Math.sin(angle) * speed;
            particle.size = 3 + Math.random() * 6;
            particle.color = colors[Math.floor(Math.random() * colors.length)];
            particle.life = 1.0;
            particle.decay = 0.015;
            particle.gravity = 0.1;
            particle.type = 'ko';

            this.particles.push(particle);
        }
    }

    /**
     * Create parry flash effect
     */
    createParryEffect(x, y) {
        // White flash at position
        this.createHitSpark(x, y, 5, 0, 'normal');

        // Brief freeze
        this.freezeFrames = 4;

        // Small shake
        this.addScreenShake(8, 100);

        // Ring effect
        this.createRingEffect(x, y, '#ffffff', 60);
    }

    /**
     * Create expanding ring effect
     */
    createRingEffect(x, y, color, maxRadius) {
        const ring = {
            x, y,
            radius: 10,
            maxRadius,
            color,
            life: 1.0
        };

        // Add to particles with special type
        const particle = this.getParticle();
        particle.x = x;
        particle.y = y;
        particle.ring = ring;
        particle.type = 'ring';
        particle.life = 1.0;
        particle.decay = 0.04;

        this.particles.push(particle);
    }

    /**
     * Create spawn/respawn effect
     */
    createSpawnEffect(x, y) {
        // Sparkle particles rising
        for (let i = 0; i < 20; i++) {
            const particle = this.getParticle();
            particle.x = x + (Math.random() - 0.5) * 40;
            particle.y = y;
            particle.vx = (Math.random() - 0.5) * 2;
            particle.vy = -2 - Math.random() * 3;
            particle.size = 2 + Math.random() * 3;
            particle.color = '#ffffff';
            particle.life = 1.0;
            particle.decay = 0.02;
            particle.gravity = -0.05; // Float up
            particle.type = 'spawn';

            this.particles.push(particle);
        }

        this.createRingEffect(x, y, '#88ff88', 50);
    }

    /**
     * Clear all effects
     */
    clear() {
        this.particles = [];
        this.hitSparks = [];
        this.trails = [];
        this.screenShake = { x: 0, y: 0, duration: 0, intensity: 0 };
        this.freezeFrames = 0;
        this.flashEffect.active = false;
        this.cameraOffset = { x: 0, y: 0 };
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EffectsManager;
}
