/**
 * Arena Brawl - Gamepad Support
 * Full controller support with customizable bindings
 */

class GamepadManager {
    constructor() {
        // Connected gamepads
        this.gamepads = new Map();

        // Default button mappings (Standard Gamepad layout)
        this.defaultMapping = {
            // Movement
            leftStickX: 0,      // Axis 0: Left stick horizontal
            leftStickY: 1,      // Axis 1: Left stick vertical
            rightStickX: 2,     // Axis 2: Right stick horizontal (C-stick)
            rightStickY: 3,     // Axis 3: Right stick vertical

            // Face buttons
            buttonA: 0,         // A / Cross - Jump
            buttonB: 1,         // B / Circle - Special
            buttonX: 2,         // X / Square - Attack
            buttonY: 3,         // Y / Triangle - Jump (alt)

            // Shoulder buttons
            buttonLB: 4,        // Left bumper - Grab
            buttonRB: 5,        // Right bumper - Parry/Dodge
            buttonLT: 6,        // Left trigger - Parry (alt)
            buttonRT: 7,        // Right trigger - Smash modifier

            // Other buttons
            buttonBack: 8,      // Back/Select
            buttonStart: 9,     // Start/Options
            buttonL3: 10,       // Left stick click
            buttonR3: 11,       // Right stick click
            dpadUp: 12,         // D-pad up
            dpadDown: 13,       // D-pad down
            dpadLeft: 14,       // D-pad left
            dpadRight: 15       // D-pad right
        };

        // Action bindings (which button does what)
        this.actionBindings = {
            jump: ['buttonA', 'buttonY', 'dpadUp'],
            attack: ['buttonX'],
            special: ['buttonB'],
            grab: ['buttonLB'],
            parry: ['buttonRB', 'buttonLT'],
            smashModifier: ['buttonRT'],
            taunt: ['dpadDown'],
            pause: ['buttonStart']
        };

        // Thresholds
        this.deadzone = 0.15;
        this.smashThreshold = 0.8;    // Stick speed for smash attacks
        this.walkThreshold = 0.3;      // Below this = walk, above = run

        // Previous state for edge detection
        this.previousStates = new Map();

        // Input buffer
        this.inputBuffer = [];
        this.bufferSize = 6; // Frames of buffer

        // C-stick mode
        this.cStickMode = 'smash'; // 'smash' or 'tilt'

        // Rumble support
        this.rumbleEnabled = true;

        // Callbacks
        this.onInput = null;
        this.onConnect = null;
        this.onDisconnect = null;

        // Initialize
        this.setupEventListeners();
    }

    /**
     * Set up gamepad connection events
     */
    setupEventListeners() {
        window.addEventListener('gamepadconnected', (e) => {
            this.handleGamepadConnected(e.gamepad);
        });

        window.addEventListener('gamepaddisconnected', (e) => {
            this.handleGamepadDisconnected(e.gamepad);
        });
    }

    /**
     * Handle gamepad connection
     */
    handleGamepadConnected(gamepad) {
        console.log(`Gamepad connected: ${gamepad.id} (index: ${gamepad.index})`);

        this.gamepads.set(gamepad.index, {
            id: gamepad.id,
            index: gamepad.index,
            mapping: { ...this.defaultMapping },
            bindings: { ...this.actionBindings }
        });

        this.previousStates.set(gamepad.index, {
            buttons: new Array(gamepad.buttons.length).fill(false),
            axes: new Array(gamepad.axes.length).fill(0),
            stickSpeed: { left: 0, right: 0 }
        });

        if (this.onConnect) {
            this.onConnect(gamepad.index, gamepad.id);
        }
    }

    /**
     * Handle gamepad disconnection
     */
    handleGamepadDisconnected(gamepad) {
        console.log(`Gamepad disconnected: ${gamepad.id}`);

        this.gamepads.delete(gamepad.index);
        this.previousStates.delete(gamepad.index);

        if (this.onDisconnect) {
            this.onDisconnect(gamepad.index);
        }
    }

    /**
     * Poll all connected gamepads
     */
    poll() {
        const gamepads = navigator.getGamepads();
        const inputs = new Map();

        for (const gamepad of gamepads) {
            if (!gamepad) continue;
            if (!this.gamepads.has(gamepad.index)) continue;

            const input = this.processGamepad(gamepad);
            inputs.set(gamepad.index, input);
        }

        return inputs;
    }

    /**
     * Process a single gamepad's input
     */
    processGamepad(gamepad) {
        const config = this.gamepads.get(gamepad.index);
        const prevState = this.previousStates.get(gamepad.index);
        const mapping = config.mapping;

        // Read stick values with deadzone
        const leftX = this.applyDeadzone(gamepad.axes[mapping.leftStickX]);
        const leftY = this.applyDeadzone(gamepad.axes[mapping.leftStickY]);
        const rightX = this.applyDeadzone(gamepad.axes[mapping.rightStickX]);
        const rightY = this.applyDeadzone(gamepad.axes[mapping.rightStickY]);

        // Calculate stick speed for smash detection
        const leftSpeed = this.calculateStickSpeed(
            leftX, leftY,
            prevState.axes[mapping.leftStickX],
            prevState.axes[mapping.leftStickY]
        );

        // Read buttons
        const buttons = {};
        for (const [name, index] of Object.entries(mapping)) {
            if (name.startsWith('button') || name.startsWith('dpad')) {
                const button = gamepad.buttons[index];
                if (button) {
                    buttons[name] = {
                        pressed: button.pressed,
                        value: button.value,
                        justPressed: button.pressed && !prevState.buttons[index],
                        justReleased: !button.pressed && prevState.buttons[index]
                    };
                }
            }
        }

        // Build input state
        const input = {
            // Movement
            move: this.getMovementDirection(leftX, leftY),
            moveX: leftX,
            moveY: leftY,
            isRunning: Math.abs(leftX) > this.walkThreshold,
            isSmashInput: leftSpeed > this.smashThreshold,

            // Directional inputs
            up: leftY < -0.5 || buttons.dpadUp?.pressed,
            down: leftY > 0.5 || buttons.dpadDown?.pressed,
            left: leftX < -0.5 || buttons.dpadLeft?.pressed,
            right: leftX > 0.5 || buttons.dpadRight?.pressed,

            // Actions (check bindings)
            jump: this.isActionPressed(buttons, config.bindings.jump),
            jumpJustPressed: this.isActionJustPressed(buttons, config.bindings.jump),
            attack: this.isActionPressed(buttons, config.bindings.attack),
            attackJustPressed: this.isActionJustPressed(buttons, config.bindings.attack),
            special: this.isActionPressed(buttons, config.bindings.special),
            specialJustPressed: this.isActionJustPressed(buttons, config.bindings.special),
            grab: this.isActionPressed(buttons, config.bindings.grab),
            grabJustPressed: this.isActionJustPressed(buttons, config.bindings.grab),
            parry: this.isActionPressed(buttons, config.bindings.parry),
            parryJustPressed: this.isActionJustPressed(buttons, config.bindings.parry),
            smashModifier: this.isActionPressed(buttons, config.bindings.smashModifier),

            // C-stick (attack stick)
            cStickX: rightX,
            cStickY: rightY,
            cStickActive: Math.abs(rightX) > 0.5 || Math.abs(rightY) > 0.5,
            cStickDirection: this.getCStickDirection(rightX, rightY),

            // Raw button states for custom handling
            buttons,

            // Metadata
            gamepadIndex: gamepad.index,
            timestamp: performance.now()
        };

        // Process C-stick attacks
        if (input.cStickActive) {
            input.cStickAttack = this.processCStick(rightX, rightY);
        }

        // Update previous state
        prevState.axes = [...gamepad.axes];
        prevState.buttons = gamepad.buttons.map(b => b.pressed);
        prevState.stickSpeed.left = leftSpeed;

        return input;
    }

    /**
     * Apply deadzone to axis value
     */
    applyDeadzone(value) {
        if (Math.abs(value) < this.deadzone) {
            return 0;
        }
        // Scale remaining range to 0-1
        const sign = Math.sign(value);
        const magnitude = (Math.abs(value) - this.deadzone) / (1 - this.deadzone);
        return sign * magnitude;
    }

    /**
     * Calculate stick movement speed
     */
    calculateStickSpeed(x1, y1, x2, y2) {
        const dx = x1 - (x2 || 0);
        const dy = y1 - (y2 || 0);
        return Math.sqrt(dx * dx + dy * dy);
    }

    /**
     * Get movement direction from stick
     */
    getMovementDirection(x, y) {
        if (Math.abs(x) < this.deadzone && Math.abs(y) < this.deadzone) {
            return 'none';
        }

        // 8-way direction
        const angle = Math.atan2(y, x) * (180 / Math.PI);

        if (angle >= -22.5 && angle < 22.5) return 'right';
        if (angle >= 22.5 && angle < 67.5) return 'down-right';
        if (angle >= 67.5 && angle < 112.5) return 'down';
        if (angle >= 112.5 && angle < 157.5) return 'down-left';
        if (angle >= 157.5 || angle < -157.5) return 'left';
        if (angle >= -157.5 && angle < -112.5) return 'up-left';
        if (angle >= -112.5 && angle < -67.5) return 'up';
        if (angle >= -67.5 && angle < -22.5) return 'up-right';

        return 'none';
    }

    /**
     * Get C-stick direction
     */
    getCStickDirection(x, y) {
        if (Math.abs(x) < 0.5 && Math.abs(y) < 0.5) {
            return null;
        }

        // 4-way for attacks
        if (Math.abs(x) > Math.abs(y)) {
            return x > 0 ? 'right' : 'left';
        } else {
            return y > 0 ? 'down' : 'up';
        }
    }

    /**
     * Process C-stick for attacks
     */
    processCStick(x, y) {
        const direction = this.getCStickDirection(x, y);
        if (!direction) return null;

        const isSmash = this.cStickMode === 'smash';

        const attacks = {
            'up': isSmash ? 'usmash' : 'utilt',
            'down': isSmash ? 'dsmash' : 'dtilt',
            'left': isSmash ? 'fsmash' : 'ftilt',
            'right': isSmash ? 'fsmash' : 'ftilt'
        };

        return {
            type: attacks[direction],
            direction,
            isSmash
        };
    }

    /**
     * Check if any button in binding array is pressed
     */
    isActionPressed(buttons, bindings) {
        return bindings.some(binding => buttons[binding]?.pressed);
    }

    /**
     * Check if any button in binding array was just pressed
     */
    isActionJustPressed(buttons, bindings) {
        return bindings.some(binding => buttons[binding]?.justPressed);
    }

    /**
     * Convert gamepad input to game input format
     */
    toGameInput(input) {
        // Convert to the format expected by the game
        const gameInput = {
            move: 'none',
            action: 'none',
            up: input.up,
            down: input.down,
            jump: input.jumpJustPressed,
            heavy: input.smashModifier || input.isSmashInput,
            dodge: input.parryJustPressed,
            grab: input.grabJustPressed
        };

        // Movement
        if (input.left) gameInput.move = 'left';
        else if (input.right) gameInput.move = 'right';

        // Actions (priority order)
        if (input.grabJustPressed) {
            gameInput.action = 'grab';
        } else if (input.parryJustPressed) {
            gameInput.action = 'dodge';
        } else if (input.specialJustPressed) {
            gameInput.action = 'special';
        } else if (input.attackJustPressed || input.cStickActive) {
            gameInput.action = 'attack';
        }

        // C-stick attack override
        if (input.cStickAttack) {
            gameInput.action = 'attack';
            gameInput.cStickAttack = input.cStickAttack;
        }

        return gameInput;
    }

    /**
     * Trigger rumble/vibration
     */
    rumble(gamepadIndex, intensity = 1.0, duration = 100) {
        if (!this.rumbleEnabled) return;

        const gamepads = navigator.getGamepads();
        const gamepad = gamepads[gamepadIndex];

        if (gamepad?.vibrationActuator) {
            gamepad.vibrationActuator.playEffect('dual-rumble', {
                startDelay: 0,
                duration: duration,
                weakMagnitude: intensity * 0.5,
                strongMagnitude: intensity
            }).catch(() => {
                // Rumble not supported or failed
            });
        }
    }

    /**
     * Short impact rumble
     */
    rumbleImpact(gamepadIndex, intensity = 0.5) {
        this.rumble(gamepadIndex, intensity, 50);
    }

    /**
     * Rumble for taking damage
     */
    rumbleDamage(gamepadIndex, damage) {
        const intensity = Math.min(0.3 + damage * 0.02, 1.0);
        const duration = Math.min(50 + damage * 2, 200);
        this.rumble(gamepadIndex, intensity, duration);
    }

    /**
     * Rumble for KO
     */
    rumbleKO(gamepadIndex) {
        this.rumble(gamepadIndex, 1.0, 300);
    }

    /**
     * Set custom button binding
     */
    setBinding(gamepadIndex, action, buttons) {
        const config = this.gamepads.get(gamepadIndex);
        if (config && this.actionBindings[action]) {
            config.bindings[action] = buttons;
        }
    }

    /**
     * Get current bindings for a gamepad
     */
    getBindings(gamepadIndex) {
        const config = this.gamepads.get(gamepadIndex);
        return config ? { ...config.bindings } : null;
    }

    /**
     * Reset bindings to default
     */
    resetBindings(gamepadIndex) {
        const config = this.gamepads.get(gamepadIndex);
        if (config) {
            config.bindings = { ...this.actionBindings };
        }
    }

    /**
     * Check if any gamepad is connected
     */
    hasGamepad() {
        return this.gamepads.size > 0;
    }

    /**
     * Get connected gamepad info
     */
    getConnectedGamepads() {
        const info = [];
        for (const [index, config] of this.gamepads) {
            info.push({
                index,
                id: config.id
            });
        }
        return info;
    }

    /**
     * Set C-stick mode
     */
    setCStickMode(mode) {
        if (mode === 'smash' || mode === 'tilt') {
            this.cStickMode = mode;
        }
    }

    /**
     * Set deadzone
     */
    setDeadzone(value) {
        this.deadzone = Math.max(0.05, Math.min(0.3, value));
    }

    /**
     * Enable/disable rumble
     */
    setRumbleEnabled(enabled) {
        this.rumbleEnabled = enabled;
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GamepadManager;
}
