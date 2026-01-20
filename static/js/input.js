/**
 * Arena Brawl - Input Handler
 * Keyboard and touch controls
 */

class InputHandler {
    constructor() {
        // Current input state
        this.keys = {
            left: false,
            right: false,
            up: false,
            down: false,
            attack: false,
            heavy: false,
            special: false,
            block: false,
            dodge: false,  // Parry/dodge button
            grab: false    // Grab button
        };

        // Touch state
        this.touchActive = false;

        // Key mappings for Player 1 (WASD + JKL)
        this.keyMap = {
            'KeyA': 'left',
            'KeyD': 'right',
            'KeyW': 'up',
            'KeyS': 'down',
            'KeyJ': 'attack',
            'KeyK': 'heavy',      // Smash modifier
            'KeyL': 'special',
            'KeyI': 'dodge',      // Dodge/parry button
            'KeyU': 'grab',       // Grab button
            'Space': 'up',        // Space also jumps
            'ShiftLeft': 'dodge'  // Shift is dodge
        };

        // Alternative mappings (Arrow keys + Numpad)
        this.altKeyMap = {
            'ArrowLeft': 'left',
            'ArrowRight': 'right',
            'ArrowUp': 'up',
            'ArrowDown': 'down',
            'Numpad1': 'attack',
            'Numpad2': 'heavy',
            'Numpad3': 'special',
            'Numpad4': 'grab',
            'Numpad0': 'dodge',
            'NumpadEnter': 'dodge'
        };

        this.enabled = false;

        this.init();
    }

    init() {
        // Keyboard events
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        document.addEventListener('keyup', (e) => this.handleKeyUp(e));

        // Touch events for mobile controls
        this.setupTouchControls();

        // Prevent default behavior for game keys
        document.addEventListener('keydown', (e) => {
            if (this.enabled && (this.keyMap[e.code] || this.altKeyMap[e.code])) {
                e.preventDefault();
            }
        });
    }

    handleKeyDown(e) {
        if (!this.enabled) return;

        const action = this.keyMap[e.code] || this.altKeyMap[e.code];
        if (action) {
            this.keys[action] = true;
        }
    }

    handleKeyUp(e) {
        if (!this.enabled) return;

        const action = this.keyMap[e.code] || this.altKeyMap[e.code];
        if (action) {
            this.keys[action] = false;
        }
    }

    setupTouchControls() {
        // D-pad buttons
        const directions = ['up', 'down', 'left', 'right'];
        directions.forEach(dir => {
            const btn = document.getElementById(`btn-${dir}`);
            if (btn) {
                btn.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    this.keys[dir] = true;
                    this.touchActive = true;
                });
                btn.addEventListener('touchend', (e) => {
                    e.preventDefault();
                    this.keys[dir] = false;
                });
                btn.addEventListener('touchcancel', (e) => {
                    this.keys[dir] = false;
                });
            }
        });

        // Action buttons
        const actions = ['attack', 'heavy', 'special', 'block'];
        actions.forEach(action => {
            const btn = document.getElementById(`btn-${action}`);
            if (btn) {
                btn.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    this.keys[action] = true;
                    this.touchActive = true;
                });
                btn.addEventListener('touchend', (e) => {
                    e.preventDefault();
                    this.keys[action] = false;
                });
                btn.addEventListener('touchcancel', (e) => {
                    this.keys[action] = false;
                });
            }
        });

        // Detect touch device and show controls
        if ('ontouchstart' in window) {
            const mobileControls = document.getElementById('mobile-controls');
            if (mobileControls) {
                mobileControls.style.display = 'flex';
            }
        }
    }

    getInputState() {
        // Determine movement direction
        let move = 'none';
        if (this.keys.left && !this.keys.right) {
            move = 'left';
        } else if (this.keys.right && !this.keys.left) {
            move = 'right';
        }

        // Check for jump
        const jump = this.keys.up;

        // Determine action (priority: dodge > grab > special > attack)
        // Note: heavy is now a modifier for smash attacks, not an action
        let action = 'none';
        if (this.keys.dodge) {
            action = 'dodge';
        } else if (this.keys.grab) {
            action = 'grab';
        } else if (this.keys.special) {
            action = 'special';
        } else if (this.keys.attack) {
            action = 'attack';
        }

        // Check if holding down (crouch/fast fall)
        const down = this.keys.down;

        // Check if holding up (for up-tilt/up-smash)
        const up = this.keys.up;

        // Check if hiding (crouch while cop is active - legacy)
        const hide = this.keys.down;

        return {
            move: move,
            action: action,
            jump: jump,
            up: up,
            down: down,
            heavy: this.keys.heavy,  // Smash modifier
            dodge: this.keys.dodge,
            grab: this.keys.grab,
            hide: hide
        };
    }

    enable() {
        this.enabled = true;
    }

    disable() {
        this.enabled = false;
        this.resetKeys();
    }

    resetKeys() {
        Object.keys(this.keys).forEach(key => {
            this.keys[key] = false;
        });
    }

    isAnyKeyPressed() {
        return Object.values(this.keys).some(v => v);
    }
}

// Global input instance
const input = new InputHandler();
