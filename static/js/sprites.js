/**
 * Arena Brawl - Sprite Manager
 * SSB-Style detailed character sprite animations
 */

class SpriteManager {
    constructor() {
        this.spriteCache = {};
        this.spriteMetadata = null;
        this.ready = false;
        this.animationStates = {};
        this.generatedSprites = {};
    }

    async init() {
        try {
            const response = await fetch('/assets/sprites/metadata.json');
            this.spriteMetadata = await response.json();
            const characters = Object.keys(this.spriteMetadata);
            await Promise.all(characters.map(char => this.loadCharacterSprites(char)));

            if (Object.keys(this.spriteCache).length === 0) {
                console.log('Generating detailed SSB-style sprites...');
                this.generateProceduralSprites();
            }
            this.ready = true;
        } catch (e) {
            console.log('Generating detailed SSB-style sprites...');
            this.generateProceduralSprites();
            this.ready = true;
        }
    }

    async loadCharacterSprites(character) {
        const meta = this.spriteMetadata[character.toLowerCase()];
        if (!meta) return;

        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                this.spriteCache[character.toLowerCase()] = img;
                resolve();
            };
            img.onerror = () => resolve();
            img.src = `/assets/sprites/${meta.spriteSheet}`;
        });
    }

    generateProceduralSprites() {
        // Detailed character configurations - Full 12 character roster
        const characters = {
            // ==================== ORIGINAL 4 ====================
            blaze: {
                // Fire Fighter - Athletic, aggressive
                skin: '#E8B89A',
                primary: '#FF4500',
                secondary: '#FF6B35',
                accent: '#FFD700',
                effect: '#FF0000',
                hair: '#FF2200',
                outfit: '#333333',
                build: 'athletic',
                features: {
                    hairStyle: 'spiky_flame',
                    expression: 'angry',
                    outfit: 'sleeveless',
                    aura: 'flame'
                }
            },
            tank: {
                // Armored Defender - Heavy, sturdy
                skin: '#D4A574',
                primary: '#4169E1',
                secondary: '#5A7FDB',
                accent: '#87CEEB',
                effect: '#00BFFF',
                hair: '#4A3728',
                outfit: '#2F4F6F',
                build: 'heavy',
                features: {
                    hairStyle: 'helmet',
                    expression: 'determined',
                    outfit: 'armor',
                    aura: 'shield'
                }
            },
            shadow: {
                // Ninja Assassin - Slim, mysterious
                skin: '#C9A882',
                primary: '#8A2BE2',
                secondary: '#9945FF',
                accent: '#DA70D6',
                effect: '#4B0082',
                hair: '#1A1A2E',
                outfit: '#2D1B4E',
                build: 'slim',
                features: {
                    hairStyle: 'hood',
                    expression: 'masked',
                    outfit: 'cloak',
                    aura: 'smoke'
                }
            },
            storm: {
                // Lightning Warrior - Balanced, energetic
                skin: '#E5C9A8',
                primary: '#FFD700',
                secondary: '#FFEC8B',
                accent: '#FFFFFF',
                effect: '#00CED1',
                hair: '#FFFFFF',
                outfit: '#1A1A3A',
                build: 'balanced',
                features: {
                    hairStyle: 'mohawk_electric',
                    expression: 'focused',
                    outfit: 'gi',
                    aura: 'lightning'
                }
            },
            // ==================== NEW 8 CHARACTERS ====================
            frost: {
                // Ice Zoner - Elegant, cool
                skin: '#E8D5E0',
                primary: '#00CED1',
                secondary: '#E0FFFF',
                accent: '#87CEEB',
                effect: '#00FFFF',
                hair: '#B0E0E6',
                outfit: '#1A3A4A',
                build: 'balanced',
                features: {
                    hairStyle: 'flowing_ice',
                    expression: 'calm',
                    outfit: 'robe',
                    aura: 'frost'
                }
            },
            titan: {
                // Grappler - Massive, powerful
                skin: '#C9A882',
                primary: '#8B4513',
                secondary: '#654321',
                accent: '#DAA520',
                effect: '#FF8C00',
                hair: '#2F1810',
                outfit: '#4A3020',
                build: 'huge',
                features: {
                    hairStyle: 'bald',
                    expression: 'fierce',
                    outfit: 'wrestler',
                    aura: 'impact'
                }
            },
            whisper: {
                // Tricky - Mysterious, elusive
                skin: '#E5C9D8',
                primary: '#9932CC',
                secondary: '#DA70D6',
                accent: '#FF69B4',
                effect: '#EE82EE',
                hair: '#4B0082',
                outfit: '#2D1B3E',
                build: 'slim',
                features: {
                    hairStyle: 'twin_tails',
                    expression: 'sly',
                    outfit: 'magic',
                    aura: 'illusion'
                }
            },
            volt: {
                // Speed Demon - Energetic, fast
                skin: '#F5DEB3',
                primary: '#00FF00',
                secondary: '#ADFF2F',
                accent: '#FFFF00',
                effect: '#00FF00',
                hair: '#32CD32',
                outfit: '#1A2A1A',
                build: 'slim',
                features: {
                    hairStyle: 'speed_lines',
                    expression: 'excited',
                    outfit: 'racer',
                    aura: 'electric_speed'
                }
            },
            golem: {
                // Juggernaut - Massive, rocky
                skin: '#808080',
                primary: '#708090',
                secondary: '#2F4F4F',
                accent: '#CD853F',
                effect: '#8B4513',
                hair: '#696969',
                outfit: '#3A3A3A',
                build: 'huge',
                features: {
                    hairStyle: 'rock_crown',
                    expression: 'stoic',
                    outfit: 'stone',
                    aura: 'earth'
                }
            },
            aria: {
                // Aerial - Floaty, graceful
                skin: '#FFE4E1',
                primary: '#87CEEB',
                secondary: '#F0F8FF',
                accent: '#FFFFFF',
                effect: '#E0FFFF',
                hair: '#ADD8E6',
                outfit: '#4A6A8A',
                build: 'slim',
                features: {
                    hairStyle: 'flowing_wind',
                    expression: 'serene',
                    outfit: 'flowing',
                    aura: 'wind'
                }
            },
            fang: {
                // Brawler - Wild, aggressive
                skin: '#D4A574',
                primary: '#DC143C',
                secondary: '#8B0000',
                accent: '#FF4500',
                effect: '#FF0000',
                hair: '#2F1810',
                outfit: '#1A1A1A',
                build: 'athletic',
                features: {
                    hairStyle: 'wild_mane',
                    expression: 'feral',
                    outfit: 'torn',
                    aura: 'rage'
                }
            },
            nova: {
                // Shoto - Classic, disciplined
                skin: '#E8B89A',
                primary: '#FF6347',
                secondary: '#FF4500',
                accent: '#FFFFFF',
                effect: '#FFD700',
                hair: '#1A1A1A',
                outfit: '#FFFFFF',
                build: 'athletic',
                features: {
                    hairStyle: 'spiky_classic',
                    expression: 'focused',
                    outfit: 'gi_classic',
                    aura: 'ki'
                }
            }
        };

        // Full SSB-style animation set
        const animations = {
            // Movement
            idle: { frames: 4, duration: 200, loop: true },
            walk: { frames: 8, duration: 100, loop: true },
            dash: { frames: 4, duration: 50, loop: false },
            run: { frames: 6, duration: 80, loop: true },
            turnaround: { frames: 3, duration: 50, loop: false },
            crouch: { frames: 2, duration: 100, loop: true },

            // Jumping
            jump_squat: { frames: 2, duration: 50, loop: false },
            jump: { frames: 3, duration: 100, loop: false },
            fall: { frames: 2, duration: 150, loop: true },
            fast_fall: { frames: 2, duration: 100, loop: true },
            land: { frames: 2, duration: 50, loop: false },

            // Ground attacks - Jabs
            jab: { frames: 4, duration: 40, loop: false },
            jab2: { frames: 4, duration: 40, loop: false },
            jab3: { frames: 5, duration: 50, loop: false },

            // Ground attacks - Tilts
            ftilt: { frames: 5, duration: 50, loop: false },
            utilt: { frames: 5, duration: 50, loop: false },
            dtilt: { frames: 4, duration: 45, loop: false },
            dash_attack: { frames: 6, duration: 50, loop: false },

            // Ground attacks - Smashes
            fsmash_charge: { frames: 2, duration: 100, loop: true },
            fsmash: { frames: 8, duration: 60, loop: false },
            usmash_charge: { frames: 2, duration: 100, loop: true },
            usmash: { frames: 7, duration: 55, loop: false },
            dsmash_charge: { frames: 2, duration: 100, loop: true },
            dsmash: { frames: 7, duration: 55, loop: false },

            // Aerial attacks
            nair: { frames: 5, duration: 50, loop: false },
            fair: { frames: 5, duration: 50, loop: false },
            bair: { frames: 5, duration: 50, loop: false },
            uair: { frames: 5, duration: 50, loop: false },
            dair: { frames: 6, duration: 55, loop: false },

            // Specials
            neutral_b: { frames: 8, duration: 60, loop: false },
            side_b: { frames: 8, duration: 60, loop: false },
            up_b: { frames: 10, duration: 50, loop: false },
            down_b: { frames: 8, duration: 60, loop: false },

            // Grabs and throws
            grab: { frames: 4, duration: 50, loop: false },
            grab_hold: { frames: 2, duration: 100, loop: true },
            pummel: { frames: 3, duration: 60, loop: false },
            fthrow: { frames: 6, duration: 50, loop: false },
            bthrow: { frames: 6, duration: 50, loop: false },
            uthrow: { frames: 6, duration: 50, loop: false },
            dthrow: { frames: 6, duration: 50, loop: false },

            // Defense
            parry: { frames: 3, duration: 50, loop: false },
            spot_dodge: { frames: 5, duration: 40, loop: false },
            air_dodge: { frames: 6, duration: 40, loop: false },
            blocking: { frames: 2, duration: 150, loop: true },

            // Damage states
            stunned: { frames: 3, duration: 100, loop: true },
            tumble: { frames: 4, duration: 80, loop: true },

            // Ledge
            ledge_hang: { frames: 2, duration: 150, loop: true },
            ledge_getup: { frames: 4, duration: 60, loop: false },
            ledge_roll: { frames: 6, duration: 50, loop: false },
            ledge_jump: { frames: 4, duration: 50, loop: false },
            ledge_attack: { frames: 5, duration: 50, loop: false },

            // Misc
            death: { frames: 6, duration: 120, loop: false },
            spawn: { frames: 4, duration: 100, loop: false },

            // Legacy compatibility
            attack_light_0: { frames: 5, duration: 50, loop: false },
            attack_light_1: { frames: 5, duration: 50, loop: false },
            attack_light_2: { frames: 5, duration: 50, loop: false },
            attack_heavy: { frames: 8, duration: 70, loop: false },
            special: { frames: 10, duration: 60, loop: false }
        };

        this.spriteMetadata = {};

        for (const [charName, config] of Object.entries(characters)) {
            this.spriteMetadata[charName] = {
                frameWidth: 128,
                frameHeight: 128,
                animations: {}
            };

            const totalFrames = Object.values(animations).reduce((sum, a) => sum + a.frames, 0);
            const canvas = document.createElement('canvas');
            const framesPerRow = 10;
            const rows = Math.ceil(totalFrames / framesPerRow);
            canvas.width = 128 * framesPerRow;
            canvas.height = 128 * rows;
            const ctx = canvas.getContext('2d');

            let frameIndex = 0;
            for (const [animName, animData] of Object.entries(animations)) {
                const startFrame = frameIndex;

                for (let f = 0; f < animData.frames; f++) {
                    const col = frameIndex % framesPerRow;
                    const row = Math.floor(frameIndex / framesPerRow);
                    const x = col * 128;
                    const y = row * 128;

                    this.drawDetailedCharacterFrame(ctx, x, y, 128, 128, charName, config, animName, f, animData.frames);
                    frameIndex++;
                }

                this.spriteMetadata[charName].animations[animName] = {
                    startFrame,
                    frames: animData.frames,
                    duration: animData.duration,
                    loop: animData.loop
                };
            }

            this.generatedSprites[charName] = canvas;
        }
    }

    drawDetailedCharacterFrame(ctx, x, y, width, height, character, config, animation, frame, totalFrames) {
        ctx.save();
        ctx.translate(x + width / 2, y + height - 10);

        const scale = 1.8;
        ctx.scale(scale, scale);

        const phase = frame / Math.max(1, totalFrames - 1);
        const cyclePhase = (frame % 4) / 4;

        // Build-specific dimensions - Expanded for all character types
        const builds = {
            athletic: { bodyWidth: 22, bodyHeight: 28, shoulderWidth: 28, legWidth: 7, armWidth: 6 },
            heavy: { bodyWidth: 28, bodyHeight: 30, shoulderWidth: 36, legWidth: 9, armWidth: 8 },
            slim: { bodyWidth: 18, bodyHeight: 26, shoulderWidth: 24, legWidth: 6, armWidth: 5 },
            balanced: { bodyWidth: 22, bodyHeight: 28, shoulderWidth: 28, legWidth: 7, armWidth: 6 },
            huge: { bodyWidth: 34, bodyHeight: 34, shoulderWidth: 42, legWidth: 11, armWidth: 10 }
        };
        const dims = builds[config.build] || builds.balanced;

        // Animation state
        let pose = this.calculatePose(animation, phase, cyclePhase, character);

        ctx.globalAlpha = pose.alpha;
        ctx.rotate(pose.bodyRotation);
        ctx.scale(pose.squash, pose.stretch);

        // Draw shadow
        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.beginPath();
        ctx.ellipse(0, 0, dims.bodyWidth * 0.6, 4, 0, 0, Math.PI * 2);
        ctx.fill();

        // Draw character aura (behind)
        this.drawAura(ctx, config, animation, phase, dims);

        // Draw legs
        this.drawDetailedLeg(ctx, -dims.legWidth, -16, dims.legWidth, 16, config, pose.leftLegAngle, 'left');
        this.drawDetailedLeg(ctx, dims.legWidth, -16, dims.legWidth, 16, config, pose.rightLegAngle, 'right');

        // Draw body/torso
        this.drawDetailedTorso(ctx, dims, config, pose.bodyOffsetY);

        // Draw arms
        this.drawDetailedArm(ctx, -dims.shoulderWidth/2 - dims.armWidth/2, -16 - dims.bodyHeight + 6 + pose.bodyOffsetY, dims.armWidth, 18, config, pose.leftArmAngle, 'left', animation, phase);
        this.drawDetailedArm(ctx, dims.shoulderWidth/2 + dims.armWidth/2, -16 - dims.bodyHeight + 6 + pose.bodyOffsetY, dims.armWidth, 18, config, pose.rightArmAngle, 'right', animation, phase);

        // Draw head
        this.drawDetailedHead(ctx, 0, -16 - dims.bodyHeight - 10 + pose.bodyOffsetY + pose.headBob, config, animation, phase, cyclePhase);

        // Draw attack effects
        if (animation.includes('attack') && phase > 0.3 && phase < 0.8) {
            this.drawAttackEffect(ctx, config, animation, phase, dims);
        }

        // Draw character-specific effects (in front)
        this.drawCharacterEffects(ctx, config, animation, phase, dims);

        ctx.restore();
    }

    calculatePose(animation, phase, cyclePhase, character) {
        let pose = {
            bodyOffsetY: 0,
            leftLegAngle: 0,
            rightLegAngle: 0,
            leftArmAngle: 0.1,
            rightArmAngle: -0.1,
            bodyRotation: 0,
            headBob: 0,
            squash: 1,
            stretch: 1,
            alpha: 1
        };

        switch (animation) {
            // ==================== MOVEMENT ====================
            case 'idle':
                pose.bodyOffsetY = Math.sin(cyclePhase * Math.PI * 2) * 1.5;
                pose.headBob = Math.sin(cyclePhase * Math.PI * 2) * 0.5;
                pose.leftArmAngle = 0.1 + Math.sin(cyclePhase * Math.PI * 2) * 0.05;
                pose.rightArmAngle = -0.1 - Math.sin(cyclePhase * Math.PI * 2) * 0.05;
                break;

            case 'walk':
                const walkCycle = (phase) * Math.PI * 2;
                pose.leftLegAngle = Math.sin(walkCycle) * 0.4;
                pose.rightLegAngle = Math.sin(walkCycle + Math.PI) * 0.4;
                pose.leftArmAngle = Math.sin(walkCycle + Math.PI) * 0.25;
                pose.rightArmAngle = Math.sin(walkCycle) * 0.25;
                pose.bodyOffsetY = Math.abs(Math.sin(walkCycle * 2)) * 2;
                pose.headBob = Math.abs(Math.sin(walkCycle * 2)) * 0.8;
                break;

            case 'dash':
                pose.bodyRotation = 0.15;
                pose.stretch = 1.1;
                pose.leftLegAngle = -0.4;
                pose.rightLegAngle = 0.5;
                pose.leftArmAngle = 0.6;
                pose.rightArmAngle = -0.8;
                break;

            case 'run':
                const runCycle = phase * Math.PI * 2;
                pose.leftLegAngle = Math.sin(runCycle) * 0.6;
                pose.rightLegAngle = Math.sin(runCycle + Math.PI) * 0.6;
                pose.leftArmAngle = Math.sin(runCycle + Math.PI) * 0.5;
                pose.rightArmAngle = Math.sin(runCycle) * 0.5;
                pose.bodyOffsetY = Math.abs(Math.sin(runCycle * 2)) * 3;
                pose.bodyRotation = 0.08;
                break;

            case 'turnaround':
                pose.bodyRotation = phase * Math.PI * 0.5;
                pose.squash = 0.9;
                break;

            case 'crouch':
                pose.bodyOffsetY = 8;
                pose.squash = 1.15;
                pose.stretch = 0.85;
                pose.leftLegAngle = 0.3;
                pose.rightLegAngle = -0.3;
                break;

            // ==================== JUMPING ====================
            case 'jump_squat':
                pose.squash = 1.2;
                pose.stretch = 0.85;
                pose.bodyOffsetY = 4;
                break;

            case 'jump':
                if (phase < 0.3) {
                    pose.squash = 1 + (1 - phase / 0.3) * 0.15;
                    pose.stretch = 1 - (1 - phase / 0.3) * 0.08;
                } else {
                    pose.stretch = 1 + (phase - 0.3) * 0.15;
                    pose.squash = 1 - (phase - 0.3) * 0.08;
                }
                pose.leftArmAngle = -0.6 - phase * 0.4;
                pose.rightArmAngle = -0.6 - phase * 0.4;
                pose.leftLegAngle = -0.25;
                pose.rightLegAngle = 0.15;
                break;

            case 'fall':
                pose.stretch = 1.08;
                pose.squash = 0.96;
                pose.leftArmAngle = -0.7 + cyclePhase * 0.15;
                pose.rightArmAngle = 0.7 - cyclePhase * 0.15;
                pose.leftLegAngle = 0.15;
                pose.rightLegAngle = -0.08;
                break;

            case 'fast_fall':
                pose.stretch = 1.15;
                pose.squash = 0.9;
                pose.leftArmAngle = -0.9;
                pose.rightArmAngle = 0.9;
                pose.leftLegAngle = 0.1;
                pose.rightLegAngle = -0.1;
                break;

            case 'land':
                pose.squash = 1.2;
                pose.stretch = 0.85;
                pose.bodyOffsetY = 5;
                break;

            // ==================== GROUND ATTACKS ====================
            case 'jab':
            case 'attack_light_0':
                pose.rightArmAngle = -1.2 + phase * 2.8;
                if (phase > 0.4 && phase < 0.7) pose.rightArmAngle = 1.5;
                pose.bodyRotation = phase < 0.5 ? phase * 0.1 : (1 - phase) * 0.1;
                pose.leftArmAngle = -0.3;
                break;

            case 'jab2':
            case 'attack_light_1':
                pose.leftArmAngle = -1.2 + phase * 2.8;
                if (phase > 0.4 && phase < 0.7) pose.leftArmAngle = 1.5;
                pose.bodyRotation = phase < 0.5 ? -phase * 0.1 : -(1 - phase) * 0.1;
                pose.rightArmAngle = 0.2;
                break;

            case 'jab3':
            case 'attack_light_2':
                pose.rightArmAngle = -1.5 + phase * 3.2;
                if (phase > 0.35 && phase < 0.65) pose.rightArmAngle = 1.7;
                pose.bodyRotation = phase < 0.5 ? phase * 0.15 : (1 - phase) * 0.15;
                pose.leftArmAngle = -0.4;
                pose.stretch = 1 + (phase > 0.3 && phase < 0.7 ? 0.1 : 0);
                break;

            case 'ftilt':
                pose.rightArmAngle = -0.8 + phase * 2.4;
                pose.bodyRotation = phase * 0.12;
                pose.leftLegAngle = -0.2;
                pose.rightLegAngle = 0.3;
                break;

            case 'utilt':
                pose.rightArmAngle = -1.8 + phase * 0.6;
                pose.leftArmAngle = -1.6 + phase * 0.4;
                pose.bodyOffsetY = -phase * 5;
                pose.stretch = 1 + phase * 0.1;
                break;

            case 'dtilt':
                pose.bodyOffsetY = 6;
                pose.squash = 1.1;
                pose.rightLegAngle = 0.5 + phase * 0.4;
                pose.bodyRotation = phase * 0.1;
                break;

            case 'dash_attack':
                pose.bodyRotation = 0.2;
                pose.stretch = 1.15;
                pose.rightArmAngle = -0.5 + phase * 2.0;
                pose.leftLegAngle = -0.5;
                pose.rightLegAngle = 0.6;
                break;

            // ==================== SMASH ATTACKS ====================
            case 'fsmash_charge':
                pose.rightArmAngle = -1.8;
                pose.bodyRotation = -0.15;
                pose.bodyOffsetY = -3;
                pose.squash = 1.05 + Math.sin(cyclePhase * Math.PI * 4) * 0.03;
                break;

            case 'fsmash':
            case 'attack_heavy':
                if (phase < 0.35) {
                    pose.rightArmAngle = -1.8 * (phase / 0.35);
                    pose.bodyRotation = -0.15 * (phase / 0.35);
                    pose.bodyOffsetY = -phase * 4;
                } else if (phase < 0.55) {
                    pose.rightArmAngle = -1.8 + 3.8 * ((phase - 0.35) / 0.2);
                    pose.bodyRotation = -0.15 + 0.35 * ((phase - 0.35) / 0.2);
                    pose.bodyOffsetY = -4 + 8 * ((phase - 0.35) / 0.2);
                } else {
                    pose.rightArmAngle = 2.0 - 2.0 * ((phase - 0.55) / 0.45);
                    pose.bodyRotation = 0.2 * (1 - (phase - 0.55) / 0.45);
                    pose.bodyOffsetY = 4 * (1 - (phase - 0.55) / 0.45);
                }
                pose.leftArmAngle = -0.5;
                pose.stretch = phase > 0.3 && phase < 0.6 ? 1.1 : 1.0;
                break;

            case 'usmash_charge':
                pose.leftArmAngle = -1.6;
                pose.rightArmAngle = -1.6;
                pose.squash = 1.1;
                pose.bodyOffsetY = 4;
                break;

            case 'usmash':
                pose.leftArmAngle = -1.6 + phase * 3.4;
                pose.rightArmAngle = -1.6 + phase * 3.4;
                if (phase > 0.4 && phase < 0.7) {
                    pose.leftArmAngle = -3.2;
                    pose.rightArmAngle = -3.2;
                }
                pose.stretch = 1 + phase * 0.15;
                pose.bodyOffsetY = -phase * 8;
                break;

            case 'dsmash_charge':
                pose.squash = 1.15;
                pose.bodyOffsetY = 5;
                pose.leftArmAngle = 0.3;
                pose.rightArmAngle = -0.3;
                break;

            case 'dsmash':
                pose.squash = 1.1;
                pose.bodyOffsetY = 6;
                pose.leftArmAngle = 0.8 + Math.sin(phase * Math.PI * 2) * 0.6;
                pose.rightArmAngle = -0.8 - Math.sin(phase * Math.PI * 2) * 0.6;
                pose.leftLegAngle = 0.6;
                pose.rightLegAngle = -0.6;
                break;

            // ==================== AERIAL ATTACKS ====================
            case 'nair':
                pose.bodyRotation = phase * Math.PI * 1.5;
                pose.leftArmAngle = 0.5;
                pose.rightArmAngle = -0.5;
                pose.leftLegAngle = 0.4;
                pose.rightLegAngle = -0.4;
                break;

            case 'fair':
                pose.rightArmAngle = -1.0 + phase * 2.5;
                pose.bodyRotation = phase * 0.2;
                pose.leftLegAngle = 0.3;
                pose.rightLegAngle = -0.2;
                break;

            case 'bair':
                pose.leftArmAngle = -1.0 + phase * 2.5;
                pose.bodyRotation = -phase * 0.2;
                pose.leftLegAngle = -0.2;
                pose.rightLegAngle = 0.3;
                break;

            case 'uair':
                pose.leftArmAngle = -1.8;
                pose.rightArmAngle = -1.8;
                pose.stretch = 1.1;
                pose.leftLegAngle = 0.2;
                pose.rightLegAngle = -0.2;
                break;

            case 'dair':
                pose.leftLegAngle = 0.8 + phase * 0.5;
                pose.rightLegAngle = 0.8 + phase * 0.5;
                pose.leftArmAngle = -0.8;
                pose.rightArmAngle = 0.8;
                pose.stretch = 1.1;
                break;

            // ==================== SPECIALS ====================
            case 'neutral_b':
            case 'special':
                const specialPhase = phase * Math.PI * 2;
                if (character === 'blaze' || character === 'nova') {
                    // Hadouken/Fire dash pose
                    pose.bodyRotation = Math.sin(specialPhase * 2) * 0.15;
                    pose.stretch = 1.1;
                    pose.leftArmAngle = 0.5;
                    pose.rightArmAngle = 1.2;
                } else if (character === 'tank' || character === 'golem') {
                    pose.squash = 1.2 - phase * 0.2;
                    pose.bodyOffsetY = -phase * 8;
                    pose.leftArmAngle = -1.2;
                    pose.rightArmAngle = -1.2;
                } else if (character === 'shadow' || character === 'whisper') {
                    pose.alpha = phase < 0.5 ? (1 - phase * 1.5) : ((phase - 0.5) * 2);
                    pose.leftArmAngle = phase < 0.5 ? -0.5 : -1.0;
                    pose.rightArmAngle = phase < 0.5 ? -0.5 : -1.0;
                } else if (character === 'storm' || character === 'volt') {
                    pose.bodyRotation = specialPhase * 0.8;
                    pose.leftArmAngle = -1.2 + Math.sin(specialPhase * 2) * 0.3;
                    pose.rightArmAngle = 1.2 + Math.cos(specialPhase * 2) * 0.3;
                } else if (character === 'frost') {
                    pose.rightArmAngle = 1.3;
                    pose.leftArmAngle = 0.2;
                    pose.stretch = 1.05;
                } else if (character === 'titan') {
                    pose.squash = 1.15;
                    pose.rightArmAngle = 1.5;
                    pose.leftArmAngle = 1.5;
                } else if (character === 'aria') {
                    pose.stretch = 1.1;
                    pose.leftArmAngle = -0.8;
                    pose.rightArmAngle = 0.8;
                    pose.bodyOffsetY = -phase * 10;
                } else if (character === 'fang') {
                    pose.squash = 1.1;
                    pose.bodyRotation = Math.sin(specialPhase) * 0.1;
                    pose.rightArmAngle = -1.0 + Math.sin(specialPhase) * 0.5;
                }
                break;

            case 'side_b':
                pose.bodyRotation = 0.2;
                pose.stretch = 1.1;
                pose.rightArmAngle = 1.3;
                pose.leftLegAngle = -0.4;
                pose.rightLegAngle = 0.5;
                break;

            case 'up_b':
                pose.stretch = 1.2;
                pose.leftArmAngle = -1.8;
                pose.rightArmAngle = -1.8;
                pose.bodyOffsetY = -phase * 12;
                break;

            case 'down_b':
                pose.squash = 1.15;
                pose.bodyOffsetY = 5;
                pose.leftArmAngle = -0.8;
                pose.rightArmAngle = -0.8;
                break;

            // ==================== GRABS ====================
            case 'grab':
                pose.rightArmAngle = 0.8 + phase * 0.6;
                pose.leftArmAngle = 0.8 + phase * 0.6;
                pose.bodyRotation = phase * 0.1;
                break;

            case 'grab_hold':
                pose.rightArmAngle = 1.0;
                pose.leftArmAngle = 1.0;
                pose.squash = 1.05;
                break;

            case 'pummel':
                pose.rightArmAngle = 1.0 + phase * 0.5;
                pose.leftArmAngle = 1.0;
                break;

            case 'fthrow':
                pose.rightArmAngle = 0.5 + phase * 1.5;
                pose.bodyRotation = phase * 0.3;
                pose.leftLegAngle = -0.3;
                break;

            case 'bthrow':
                pose.bodyRotation = phase * -0.5;
                pose.rightArmAngle = 1.0 - phase * 2.5;
                break;

            case 'uthrow':
                pose.rightArmAngle = -1.6 - phase * 0.5;
                pose.leftArmAngle = -1.6 - phase * 0.5;
                pose.stretch = 1 + phase * 0.1;
                break;

            case 'dthrow':
                pose.squash = 1.1;
                pose.bodyOffsetY = 5;
                pose.rightArmAngle = 1.5 + phase * 0.5;
                break;

            // ==================== DEFENSE ====================
            case 'parry':
                pose.leftArmAngle = -1.2;
                pose.rightArmAngle = -1.0;
                pose.squash = 1.1;
                pose.bodyOffsetY = 2;
                if (phase > 0.3 && phase < 0.6) {
                    pose.stretch = 1.15;
                }
                break;

            case 'spot_dodge':
                pose.alpha = phase > 0.2 && phase < 0.8 ? 0.5 : 1.0;
                pose.squash = 1.15;
                pose.bodyOffsetY = 6;
                pose.bodyRotation = Math.sin(phase * Math.PI) * 0.2;
                break;

            case 'air_dodge':
                pose.alpha = phase > 0.15 && phase < 0.75 ? 0.4 : 1.0;
                pose.stretch = 1.1;
                pose.bodyRotation = phase * 0.5;
                break;

            case 'blocking':
                pose.leftArmAngle = -1.0;
                pose.rightArmAngle = -0.9;
                pose.squash = 1.08;
                pose.bodyOffsetY = 1.5;
                pose.leftLegAngle = -0.1;
                pose.rightLegAngle = 0.1;
                break;

            // ==================== DAMAGE STATES ====================
            case 'stunned':
                pose.bodyRotation = Math.sin(cyclePhase * Math.PI * 4) * 0.12;
                pose.headBob = Math.sin(cyclePhase * Math.PI * 4) * 2;
                pose.leftArmAngle = 0.3;
                pose.rightArmAngle = -0.3;
                break;

            case 'tumble':
                pose.bodyRotation = phase * Math.PI * 2;
                pose.leftArmAngle = 0.5;
                pose.rightArmAngle = -0.5;
                pose.leftLegAngle = 0.3;
                pose.rightLegAngle = -0.3;
                break;

            // ==================== LEDGE ====================
            case 'ledge_hang':
                pose.leftArmAngle = -1.8;
                pose.rightArmAngle = -1.8;
                pose.stretch = 1.1;
                pose.leftLegAngle = 0.1;
                pose.rightLegAngle = -0.1;
                break;

            case 'ledge_getup':
                pose.leftArmAngle = -1.5 + phase * 1.6;
                pose.rightArmAngle = -1.5 + phase * 1.6;
                pose.bodyOffsetY = phase * -10;
                break;

            case 'ledge_roll':
                pose.bodyRotation = phase * Math.PI;
                pose.alpha = phase > 0.2 && phase < 0.8 ? 0.5 : 1.0;
                break;

            case 'ledge_jump':
                pose.stretch = 1.15;
                pose.leftArmAngle = -0.8;
                pose.rightArmAngle = -0.8;
                pose.bodyOffsetY = -phase * 15;
                break;

            case 'ledge_attack':
                pose.rightArmAngle = -1.2 + phase * 2.8;
                pose.bodyOffsetY = phase * -8;
                break;

            // ==================== MISC ====================
            case 'death':
                pose.bodyRotation = phase * 1.3;
                pose.alpha = 1 - phase * 0.4;
                pose.bodyOffsetY = phase * 15;
                break;

            case 'spawn':
                pose.alpha = phase;
                pose.stretch = 1.8 - phase * 0.8;
                pose.squash = 0.6 + phase * 0.4;
                break;
        }

        return pose;
    }

    drawDetailedTorso(ctx, dims, config, offsetY) {
        const torsoY = -16 - dims.bodyHeight + offsetY;

        // Draw body shape based on build
        ctx.fillStyle = config.outfit;

        if (config.build === 'heavy') {
            // Armor plating
            ctx.beginPath();
            ctx.moveTo(-dims.shoulderWidth/2, torsoY + 4);
            ctx.lineTo(-dims.bodyWidth/2, torsoY + dims.bodyHeight);
            ctx.lineTo(dims.bodyWidth/2, torsoY + dims.bodyHeight);
            ctx.lineTo(dims.shoulderWidth/2, torsoY + 4);
            ctx.closePath();
            ctx.fill();

            // Shoulder pads
            ctx.fillStyle = config.secondary;
            ctx.beginPath();
            ctx.ellipse(-dims.shoulderWidth/2 + 2, torsoY + 6, 8, 5, -0.3, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(dims.shoulderWidth/2 - 2, torsoY + 6, 8, 5, 0.3, 0, Math.PI * 2);
            ctx.fill();

            // Chest plate
            ctx.fillStyle = config.primary;
            ctx.beginPath();
            ctx.moveTo(-dims.bodyWidth/2 + 4, torsoY + 8);
            ctx.lineTo(-dims.bodyWidth/2 + 4, torsoY + dims.bodyHeight - 4);
            ctx.lineTo(dims.bodyWidth/2 - 4, torsoY + dims.bodyHeight - 4);
            ctx.lineTo(dims.bodyWidth/2 - 4, torsoY + 8);
            ctx.closePath();
            ctx.fill();
        } else if (config.features.outfit === 'sleeveless') {
            // Athletic sleeveless top
            ctx.beginPath();
            ctx.moveTo(-dims.bodyWidth/2 + 2, torsoY);
            ctx.lineTo(-dims.bodyWidth/2, torsoY + dims.bodyHeight);
            ctx.lineTo(dims.bodyWidth/2, torsoY + dims.bodyHeight);
            ctx.lineTo(dims.bodyWidth/2 - 2, torsoY);
            ctx.closePath();
            ctx.fill();

            // Muscle definition
            ctx.strokeStyle = 'rgba(0,0,0,0.2)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(0, torsoY + 4);
            ctx.lineTo(0, torsoY + dims.bodyHeight - 6);
            ctx.stroke();
        } else if (config.features.outfit === 'cloak') {
            // Ninja cloak/wrap
            ctx.beginPath();
            ctx.moveTo(-dims.shoulderWidth/2, torsoY);
            ctx.lineTo(-dims.bodyWidth/2 - 3, torsoY + dims.bodyHeight + 4);
            ctx.lineTo(dims.bodyWidth/2 + 3, torsoY + dims.bodyHeight + 4);
            ctx.lineTo(dims.shoulderWidth/2, torsoY);
            ctx.closePath();
            ctx.fill();

            // Wrap details
            ctx.strokeStyle = config.secondary;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(-dims.bodyWidth/2, torsoY + 8);
            ctx.lineTo(dims.bodyWidth/2, torsoY + 12);
            ctx.stroke();
        } else if (config.features.outfit === 'gi') {
            // Martial arts gi
            ctx.beginPath();
            ctx.moveTo(-dims.bodyWidth/2, torsoY);
            ctx.lineTo(-dims.bodyWidth/2, torsoY + dims.bodyHeight);
            ctx.lineTo(dims.bodyWidth/2, torsoY + dims.bodyHeight);
            ctx.lineTo(dims.bodyWidth/2, torsoY);
            ctx.closePath();
            ctx.fill();

            // Gi lapels
            ctx.fillStyle = config.secondary;
            ctx.beginPath();
            ctx.moveTo(-3, torsoY);
            ctx.lineTo(-dims.bodyWidth/2 + 3, torsoY + 15);
            ctx.lineTo(-dims.bodyWidth/2 + 3, torsoY + dims.bodyHeight - 4);
            ctx.lineTo(dims.bodyWidth/2 - 3, torsoY + dims.bodyHeight - 4);
            ctx.lineTo(dims.bodyWidth/2 - 3, torsoY + 15);
            ctx.lineTo(3, torsoY);
            ctx.closePath();
            ctx.fill();

            // Belt
            ctx.fillStyle = config.primary;
            ctx.fillRect(-dims.bodyWidth/2 - 1, torsoY + dims.bodyHeight - 6, dims.bodyWidth + 2, 4);
        } else {
            // Default outfit
            ctx.fillRect(-dims.bodyWidth/2, torsoY, dims.bodyWidth, dims.bodyHeight);
            ctx.fillStyle = config.secondary;
            ctx.fillRect(-dims.bodyWidth/2 + 2, torsoY + 2, dims.bodyWidth/3, dims.bodyHeight - 4);
        }
    }

    drawDetailedHead(ctx, x, y, config, animation, phase, cyclePhase) {
        // Head shape
        const headWidth = 18;
        const headHeight = 20;

        // Draw hair/helmet first (behind head for some styles)
        if (config.features.hairStyle === 'hood') {
            ctx.fillStyle = config.outfit;
            ctx.beginPath();
            ctx.ellipse(x, y - 2, headWidth/2 + 4, headHeight/2 + 4, 0, Math.PI, 0);
            ctx.fill();
            // Hood shadows
            ctx.fillStyle = 'rgba(0,0,0,0.3)';
            ctx.beginPath();
            ctx.ellipse(x, y, headWidth/2 + 2, headHeight/2 + 2, 0, Math.PI * 0.8, Math.PI * 0.2);
            ctx.fill();
        }

        // Face/head base
        ctx.fillStyle = config.skin;
        ctx.beginPath();
        ctx.ellipse(x, y, headWidth/2, headHeight/2, 0, 0, Math.PI * 2);
        ctx.fill();

        // Draw facial features based on expression
        this.drawFace(ctx, x, y, config, animation, phase, cyclePhase);

        // Draw hair on top
        this.drawHair(ctx, x, y - headHeight/2 + 2, config, animation, phase);
    }

    drawFace(ctx, x, y, config, animation, phase, cyclePhase) {
        const expression = config.features.expression;

        if (expression === 'masked') {
            // Ninja mask - only eyes visible
            ctx.fillStyle = config.outfit;
            ctx.fillRect(x - 9, y - 2, 18, 12);

            // Eyes (intense)
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.ellipse(x - 4, y, 4, 2.5, 0, 0, Math.PI * 2);
            ctx.ellipse(x + 4, y, 4, 2.5, 0, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = config.effect;
            ctx.beginPath();
            ctx.arc(x - 4, y, 2, 0, Math.PI * 2);
            ctx.arc(x + 4, y, 2, 0, Math.PI * 2);
            ctx.fill();
        } else {
            // Regular face
            // Eyes
            const eyeY = y - 2;
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.ellipse(x - 4, eyeY, 4, 3, 0, 0, Math.PI * 2);
            ctx.ellipse(x + 4, eyeY, 4, 3, 0, 0, Math.PI * 2);
            ctx.fill();

            // Pupils - look direction based on animation
            let pupilOffsetX = 0.5;
            if (animation.includes('attack')) pupilOffsetX = 1.5;
            ctx.fillStyle = 'black';
            ctx.beginPath();
            ctx.arc(x - 4 + pupilOffsetX, eyeY, 2, 0, Math.PI * 2);
            ctx.arc(x + 4 + pupilOffsetX, eyeY, 2, 0, Math.PI * 2);
            ctx.fill();

            // Eyebrows based on expression
            ctx.strokeStyle = config.hair;
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';

            if (expression === 'angry') {
                ctx.beginPath();
                ctx.moveTo(x - 7, eyeY - 5);
                ctx.lineTo(x - 2, eyeY - 3);
                ctx.moveTo(x + 2, eyeY - 3);
                ctx.lineTo(x + 7, eyeY - 5);
                ctx.stroke();
            } else if (expression === 'determined') {
                ctx.beginPath();
                ctx.moveTo(x - 7, eyeY - 4);
                ctx.lineTo(x - 1, eyeY - 4);
                ctx.moveTo(x + 1, eyeY - 4);
                ctx.lineTo(x + 7, eyeY - 4);
                ctx.stroke();
            } else {
                ctx.beginPath();
                ctx.moveTo(x - 6, eyeY - 4);
                ctx.lineTo(x - 1, eyeY - 5);
                ctx.moveTo(x + 1, eyeY - 5);
                ctx.lineTo(x + 6, eyeY - 4);
                ctx.stroke();
            }

            // Mouth
            ctx.strokeStyle = '#8B4513';
            ctx.lineWidth = 1.5;
            if (expression === 'angry' || animation.includes('attack')) {
                // Gritting teeth
                ctx.beginPath();
                ctx.moveTo(x - 4, y + 5);
                ctx.lineTo(x + 4, y + 5);
                ctx.stroke();
                ctx.strokeStyle = 'white';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(x - 3, y + 5);
                ctx.lineTo(x + 3, y + 5);
                ctx.stroke();
            } else if (animation === 'stunned') {
                // Dizzy spiral mouth
                ctx.beginPath();
                ctx.arc(x, y + 5, 3, 0, Math.PI);
                ctx.stroke();
            } else {
                // Normal mouth
                ctx.beginPath();
                ctx.moveTo(x - 3, y + 4);
                ctx.quadraticCurveTo(x, y + 6, x + 3, y + 4);
                ctx.stroke();
            }
        }
    }

    drawHair(ctx, x, y, config, animation, phase) {
        const style = config.features.hairStyle;

        if (style === 'spiky_flame') {
            // Spiky flame hair
            ctx.fillStyle = config.hair;
            for (let i = -2; i <= 2; i++) {
                const spikeX = x + i * 4;
                const spikeHeight = 12 + Math.abs(i) * 2;
                const wobble = Math.sin(phase * Math.PI * 4 + i) * 2;

                ctx.beginPath();
                ctx.moveTo(spikeX - 3, y + 4);
                ctx.lineTo(spikeX + wobble, y - spikeHeight);
                ctx.lineTo(spikeX + 3, y + 4);
                ctx.closePath();
                ctx.fill();
            }

            // Inner flame color
            ctx.fillStyle = config.secondary;
            for (let i = -1; i <= 1; i++) {
                const spikeX = x + i * 4;
                const spikeHeight = 8 + Math.abs(i) * 1.5;

                ctx.beginPath();
                ctx.moveTo(spikeX - 2, y + 2);
                ctx.lineTo(spikeX, y - spikeHeight);
                ctx.lineTo(spikeX + 2, y + 2);
                ctx.closePath();
                ctx.fill();
            }
        } else if (style === 'helmet') {
            // Armored helmet
            ctx.fillStyle = config.secondary;
            ctx.beginPath();
            ctx.ellipse(x, y + 2, 12, 10, 0, Math.PI, 0);
            ctx.fill();

            // Visor
            ctx.fillStyle = config.accent;
            ctx.fillRect(x - 8, y + 4, 16, 3);

            // Helmet crest
            ctx.fillStyle = config.primary;
            ctx.beginPath();
            ctx.moveTo(x, y - 8);
            ctx.lineTo(x - 3, y + 2);
            ctx.lineTo(x + 3, y + 2);
            ctx.closePath();
            ctx.fill();
        } else if (style === 'mohawk_electric') {
            // Electric mohawk
            ctx.fillStyle = config.hair;
            for (let i = -4; i <= 4; i++) {
                const spikeX = x + i * 2;
                const spikeHeight = 10 - Math.abs(i) * 0.8;

                ctx.beginPath();
                ctx.moveTo(spikeX - 1.5, y + 3);
                ctx.lineTo(spikeX, y - spikeHeight);
                ctx.lineTo(spikeX + 1.5, y + 3);
                ctx.closePath();
                ctx.fill();
            }

            // Electric effect on hair
            if (animation === 'special' || animation.includes('attack')) {
                ctx.strokeStyle = config.effect;
                ctx.lineWidth = 1;
                for (let i = 0; i < 3; i++) {
                    const sparkX = x - 6 + i * 6;
                    ctx.beginPath();
                    ctx.moveTo(sparkX, y - 6);
                    ctx.lineTo(sparkX + 2, y - 10);
                    ctx.lineTo(sparkX, y - 8);
                    ctx.lineTo(sparkX + 3, y - 14);
                    ctx.stroke();
                }
            }
        }
        // Hood style is drawn in drawDetailedHead
    }

    drawDetailedArm(ctx, x, y, width, height, config, angle, side, animation, phase) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(angle);

        // Upper arm
        ctx.fillStyle = config.features.outfit === 'sleeveless' ? config.skin : config.outfit;
        ctx.fillRect(-width/2, 0, width, height * 0.55);

        // Forearm
        ctx.fillStyle = config.skin;
        ctx.fillRect(-width/2, height * 0.55, width, height * 0.35);

        // Hand/fist
        ctx.beginPath();
        ctx.arc(0, height * 0.9 + 2, width * 0.7, 0, Math.PI * 2);
        ctx.fill();

        // Glove/gauntlet for certain characters
        if (config.build === 'heavy') {
            ctx.fillStyle = config.secondary;
            ctx.beginPath();
            ctx.arc(0, height * 0.9 + 2, width * 0.8, 0, Math.PI * 2);
            ctx.fill();
        }

        // Attack fist glow
        if (side === 'right' && animation.includes('attack') && phase > 0.3 && phase < 0.7) {
            ctx.fillStyle = config.effect;
            ctx.globalAlpha = 0.5;
            ctx.beginPath();
            ctx.arc(0, height + 4, width * 1.2, 0, Math.PI * 2);
            ctx.fill();
            ctx.globalAlpha = 1;
        }

        ctx.restore();
    }

    drawDetailedLeg(ctx, x, y, width, height, config, angle, side) {
        ctx.save();
        ctx.translate(x, y);
        ctx.rotate(angle);

        // Thigh
        ctx.fillStyle = config.outfit;
        ctx.fillRect(-width/2, 0, width, height * 0.55);

        // Calf
        ctx.fillRect(-width/2, height * 0.55, width, height * 0.35);

        // Foot/shoe
        ctx.fillStyle = config.build === 'heavy' ? config.secondary : '#333';
        ctx.beginPath();
        ctx.ellipse(width * 0.2, height * 0.9 + 3, width * 0.7, 4, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();
    }

    drawAura(ctx, config, animation, phase, dims) {
        const auraType = config.features.aura;

        ctx.globalAlpha = 0.3;

        if (auraType === 'flame' && (animation === 'special' || animation.includes('attack'))) {
            ctx.fillStyle = config.effect;
            for (let i = 0; i < 6; i++) {
                const flameX = -15 + i * 6;
                const flameY = -30 - Math.sin(phase * Math.PI * 4 + i) * 8;
                ctx.beginPath();
                ctx.ellipse(flameX, flameY, 4, 8, 0, 0, Math.PI * 2);
                ctx.fill();
            }
        } else if (auraType === 'shield' && animation === 'blocking') {
            ctx.strokeStyle = config.effect;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(0, -30, 25, 0, Math.PI * 2);
            ctx.stroke();
        } else if (auraType === 'smoke') {
            ctx.fillStyle = config.effect;
            for (let i = 0; i < 4; i++) {
                const smokeX = -12 + i * 8 + Math.sin(phase * Math.PI * 2 + i) * 3;
                const smokeY = -20 - i * 5;
                ctx.beginPath();
                ctx.arc(smokeX, smokeY, 5 - i, 0, Math.PI * 2);
                ctx.fill();
            }
        } else if (auraType === 'lightning' && animation === 'special') {
            ctx.strokeStyle = config.effect;
            ctx.lineWidth = 2;
            for (let i = 0; i < 4; i++) {
                const angle = (phase * Math.PI * 4 + i * Math.PI / 2);
                const boltX = Math.cos(angle) * 20;
                const boltY = -30 + Math.sin(angle) * 10;
                ctx.beginPath();
                ctx.moveTo(boltX - 3, boltY);
                ctx.lineTo(boltX + 2, boltY - 8);
                ctx.lineTo(boltX - 1, boltY - 5);
                ctx.lineTo(boltX + 4, boltY - 12);
                ctx.stroke();
            }
        }

        ctx.globalAlpha = 1;
    }

    drawAttackEffect(ctx, config, animation, phase, dims) {
        ctx.fillStyle = config.effect;
        ctx.globalAlpha = 0.6 * (1 - Math.abs(phase - 0.55) * 3);

        if (animation === 'attack_heavy') {
            // Large impact effect
            ctx.beginPath();
            ctx.arc(dims.shoulderWidth/2 + 18, -30, 15 + (1 - Math.abs(phase - 0.5)) * 8, 0, Math.PI * 2);
            ctx.fill();

            // Speed lines
            ctx.strokeStyle = 'white';
            ctx.lineWidth = 2;
            for (let i = 0; i < 5; i++) {
                const lineY = -40 + i * 8;
                ctx.beginPath();
                ctx.moveTo(dims.shoulderWidth/2 + 10, lineY);
                ctx.lineTo(dims.shoulderWidth/2 + 30 + Math.random() * 10, lineY);
                ctx.stroke();
            }
        } else {
            // Standard punch effect
            ctx.beginPath();
            ctx.arc(dims.shoulderWidth/2 + 15, -28, 10, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.globalAlpha = 1;
    }

    drawCharacterEffects(ctx, config, animation, phase, dims) {
        if (config.features.aura === 'flame' && animation === 'special') {
            // Fire trail
            ctx.fillStyle = config.effect;
            ctx.globalAlpha = 0.7;
            for (let i = 0; i < 8; i++) {
                const trailX = -30 - i * 6;
                const trailY = -20 + Math.sin(phase * Math.PI * 6 + i) * 5;
                const trailSize = 8 - i * 0.8;
                ctx.beginPath();
                ctx.arc(trailX, trailY, trailSize, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.globalAlpha = 1;
        } else if (config.features.aura === 'lightning' && animation === 'special') {
            // Electric aura
            ctx.strokeStyle = config.effect;
            ctx.lineWidth = 2;
            ctx.globalAlpha = 0.8;
            for (let i = 0; i < 6; i++) {
                const angle = phase * Math.PI * 6 + i;
                const radius = 30 + Math.sin(angle * 2) * 5;
                const x = Math.cos(angle) * radius;
                const y = -30 + Math.sin(angle) * radius * 0.5;

                ctx.beginPath();
                ctx.arc(x, y, 3, 0, Math.PI * 2);
                ctx.stroke();
            }
            ctx.globalAlpha = 1;
        }
    }

    getAnimationFrame(playerId, character, animation, timestamp) {
        const charLower = character.toLowerCase();
        const meta = this.spriteMetadata[charLower];
        if (!meta || !meta.animations[animation]) {
            if (meta && meta.animations.idle) animation = 'idle';
            else return null;
        }

        const animMeta = meta.animations[animation];

        if (!this.animationStates[playerId]) {
            this.animationStates[playerId] = {};
        }

        const state = this.animationStates[playerId];
        if (state.animation !== animation) {
            state.animation = animation;
            state.startTime = timestamp;
        }

        const elapsed = timestamp - state.startTime;
        const frameDuration = animMeta.duration;
        const totalDuration = frameDuration * animMeta.frames;

        let frameIndex;
        if (animMeta.loop) {
            frameIndex = Math.floor((elapsed % totalDuration) / frameDuration);
        } else {
            frameIndex = Math.min(Math.floor(elapsed / frameDuration), animMeta.frames - 1);
        }

        return {
            frame: animMeta.startFrame + frameIndex,
            frameWidth: meta.frameWidth,
            frameHeight: meta.frameHeight
        };
    }

    drawSprite(ctx, player, timestamp) {
        if (!this.ready) return false;

        const { id, x, y, character, facing_right, animation } = player;
        const charLower = character.toLowerCase();

        const frameInfo = this.getAnimationFrame(id, character, animation || 'idle', timestamp);
        if (!frameInfo) return false;

        const spriteSource = this.generatedSprites[charLower] || this.spriteCache[charLower];
        if (!spriteSource) return false;

        const { frame, frameWidth, frameHeight } = frameInfo;
        const framesPerRow = 10;
        const srcCol = frame % framesPerRow;
        const srcRow = Math.floor(frame / framesPerRow);
        const srcX = srcCol * frameWidth;
        const srcY = srcRow * frameHeight;

        const destWidth = 100;
        const destHeight = 100;

        ctx.save();
        ctx.translate(x, y);

        if (!facing_right) {
            ctx.scale(-1, 1);
        }

        ctx.drawImage(
            spriteSource,
            srcX, srcY, frameWidth, frameHeight,
            -destWidth / 2, -destHeight, destWidth, destHeight
        );

        ctx.restore();
        return true;
    }

    resetAnimation(playerId) {
        if (this.animationStates[playerId]) {
            this.animationStates[playerId].startTime = performance.now();
        }
    }

    removePlayer(playerId) {
        delete this.animationStates[playerId];
    }
}

const spriteManager = new SpriteManager();
