/**
 * Arena Brawl - Settings Manager
 * Input rebinding, audio settings, and display options
 */

class SettingsManager {
    constructor() {
        // Default keyboard bindings (Player 1)
        this.defaultBindingsP1 = {
            moveLeft: 'KeyA',
            moveRight: 'KeyD',
            moveUp: 'KeyW',
            moveDown: 'KeyS',
            jump: 'Space',
            attack: 'KeyJ',
            special: 'KeyK',
            parry: 'KeyL',
            grab: 'KeyI',
            taunt: 'KeyT'
        };

        // Default keyboard bindings (Player 2)
        this.defaultBindingsP2 = {
            moveLeft: 'ArrowLeft',
            moveRight: 'ArrowRight',
            moveUp: 'ArrowUp',
            moveDown: 'ArrowDown',
            jump: 'Numpad0',
            attack: 'Numpad1',
            special: 'Numpad2',
            parry: 'Numpad3',
            grab: 'NumpadEnter',
            taunt: 'Numpad5'
        };

        // Current bindings
        this.bindings = {
            player1: { ...this.defaultBindingsP1 },
            player2: { ...this.defaultBindingsP2 }
        };

        // Audio settings
        this.audio = {
            masterVolume: 0.8,
            musicVolume: 0.6,
            sfxVolume: 0.8,
            voiceVolume: 0.7,
            muted: false
        };

        // Display settings
        this.display = {
            screenShake: true,
            hitEffects: true,
            showDamageNumbers: true,
            showComboCounter: true,
            showInputDisplay: false,
            cameraZoom: 1.0,
            vsync: true
        };

        // Gameplay settings
        this.gameplay = {
            tapJump: true,           // Tap up to jump
            stickSensitivity: 0.5,   // For gamepad
            cStickMode: 'smash',     // 'smash' or 'tilt'
            rumble: true,
            inputBuffer: 6           // Frames of input buffer
        };

        // Currently rebinding
        this.rebindingAction = null;
        this.rebindingPlayer = null;
        this.rebindCallback = null;

        // Load saved settings
        this.load();
    }

    /**
     * Load settings from localStorage
     */
    load() {
        try {
            const saved = localStorage.getItem('arenaBrawlSettings');
            if (saved) {
                const data = JSON.parse(saved);

                if (data.bindings) {
                    this.bindings.player1 = { ...this.defaultBindingsP1, ...data.bindings.player1 };
                    this.bindings.player2 = { ...this.defaultBindingsP2, ...data.bindings.player2 };
                }
                if (data.audio) {
                    this.audio = { ...this.audio, ...data.audio };
                }
                if (data.display) {
                    this.display = { ...this.display, ...data.display };
                }
                if (data.gameplay) {
                    this.gameplay = { ...this.gameplay, ...data.gameplay };
                }
            }
        } catch (e) {
            console.warn('Failed to load settings:', e);
        }
    }

    /**
     * Save settings to localStorage
     */
    save() {
        try {
            const data = {
                bindings: this.bindings,
                audio: this.audio,
                display: this.display,
                gameplay: this.gameplay
            };
            localStorage.setItem('arenaBrawlSettings', JSON.stringify(data));
        } catch (e) {
            console.warn('Failed to save settings:', e);
        }
    }

    /**
     * Reset all settings to default
     */
    resetAll() {
        this.bindings = {
            player1: { ...this.defaultBindingsP1 },
            player2: { ...this.defaultBindingsP2 }
        };
        this.audio = {
            masterVolume: 0.8,
            musicVolume: 0.6,
            sfxVolume: 0.8,
            voiceVolume: 0.7,
            muted: false
        };
        this.display = {
            screenShake: true,
            hitEffects: true,
            showDamageNumbers: true,
            showComboCounter: true,
            showInputDisplay: false,
            cameraZoom: 1.0,
            vsync: true
        };
        this.gameplay = {
            tapJump: true,
            stickSensitivity: 0.5,
            cStickMode: 'smash',
            rumble: true,
            inputBuffer: 6
        };
        this.save();
    }

    /**
     * Reset controls for a player
     */
    resetControls(player = 'player1') {
        if (player === 'player1') {
            this.bindings.player1 = { ...this.defaultBindingsP1 };
        } else {
            this.bindings.player2 = { ...this.defaultBindingsP2 };
        }
        this.save();
    }

    /**
     * Start rebinding an action
     */
    startRebind(player, action, callback) {
        this.rebindingPlayer = player;
        this.rebindingAction = action;
        this.rebindCallback = callback;

        // Listen for key press
        this.rebindHandler = (e) => {
            e.preventDefault();

            // Cancel on Escape
            if (e.code === 'Escape') {
                this.cancelRebind();
                return;
            }

            // Set new binding
            this.setBinding(player, action, e.code);
            this.finishRebind(e.code);
        };

        document.addEventListener('keydown', this.rebindHandler);
    }

    /**
     * Cancel current rebind
     */
    cancelRebind() {
        if (this.rebindHandler) {
            document.removeEventListener('keydown', this.rebindHandler);
        }
        this.rebindingAction = null;
        this.rebindingPlayer = null;
        if (this.rebindCallback) {
            this.rebindCallback(null, true);
            this.rebindCallback = null;
        }
    }

    /**
     * Finish rebind with new key
     */
    finishRebind(newKey) {
        if (this.rebindHandler) {
            document.removeEventListener('keydown', this.rebindHandler);
        }
        this.rebindingAction = null;
        this.rebindingPlayer = null;
        if (this.rebindCallback) {
            this.rebindCallback(newKey, false);
            this.rebindCallback = null;
        }
    }

    /**
     * Set a key binding
     */
    setBinding(player, action, key) {
        // Check for conflicts within same player
        const playerBindings = this.bindings[player];
        for (const [existingAction, existingKey] of Object.entries(playerBindings)) {
            if (existingKey === key && existingAction !== action) {
                // Swap bindings
                playerBindings[existingAction] = playerBindings[action];
                break;
            }
        }

        playerBindings[action] = key;
        this.save();
    }

    /**
     * Get binding for an action
     */
    getBinding(player, action) {
        return this.bindings[player]?.[action] || null;
    }

    /**
     * Get all bindings for a player
     */
    getBindings(player = 'player1') {
        return { ...this.bindings[player] };
    }

    /**
     * Check if a key is bound to an action
     */
    getActionForKey(player, keyCode) {
        const bindings = this.bindings[player];
        for (const [action, key] of Object.entries(bindings)) {
            if (key === keyCode) {
                return action;
            }
        }
        return null;
    }

    /**
     * Get display name for a key code
     */
    getKeyDisplayName(keyCode) {
        const keyNames = {
            'Space': 'Space',
            'ArrowUp': '↑',
            'ArrowDown': '↓',
            'ArrowLeft': '←',
            'ArrowRight': '→',
            'ShiftLeft': 'L Shift',
            'ShiftRight': 'R Shift',
            'ControlLeft': 'L Ctrl',
            'ControlRight': 'R Ctrl',
            'AltLeft': 'L Alt',
            'AltRight': 'R Alt',
            'Enter': 'Enter',
            'Backspace': 'Backspace',
            'Tab': 'Tab',
            'Escape': 'Esc',
            'NumpadEnter': 'Num Enter',
            'Numpad0': 'Num 0',
            'Numpad1': 'Num 1',
            'Numpad2': 'Num 2',
            'Numpad3': 'Num 3',
            'Numpad4': 'Num 4',
            'Numpad5': 'Num 5',
            'Numpad6': 'Num 6',
            'Numpad7': 'Num 7',
            'Numpad8': 'Num 8',
            'Numpad9': 'Num 9'
        };

        if (keyNames[keyCode]) {
            return keyNames[keyCode];
        }

        // Handle letter keys
        if (keyCode.startsWith('Key')) {
            return keyCode.slice(3);
        }

        // Handle digit keys
        if (keyCode.startsWith('Digit')) {
            return keyCode.slice(5);
        }

        return keyCode;
    }

    /**
     * Set audio setting
     */
    setAudio(setting, value) {
        if (setting in this.audio) {
            this.audio[setting] = value;
            this.save();
            this.applyAudioSettings();
        }
    }

    /**
     * Apply audio settings to game
     */
    applyAudioSettings() {
        // Would integrate with audio system
        // For now, just store the values
    }

    /**
     * Set display setting
     */
    setDisplay(setting, value) {
        if (setting in this.display) {
            this.display[setting] = value;
            this.save();
        }
    }

    /**
     * Set gameplay setting
     */
    setGameplay(setting, value) {
        if (setting in this.gameplay) {
            this.gameplay[setting] = value;
            this.save();
        }
    }

    /**
     * Generate settings menu HTML
     */
    generateMenuHTML(activeTab = 'controls') {
        return `
            <div class="settings-menu">
                <div class="settings-tabs">
                    <button class="settings-tab ${activeTab === 'controls' ? 'active' : ''}"
                            data-tab="controls">Controls</button>
                    <button class="settings-tab ${activeTab === 'audio' ? 'active' : ''}"
                            data-tab="audio">Audio</button>
                    <button class="settings-tab ${activeTab === 'display' ? 'active' : ''}"
                            data-tab="display">Display</button>
                    <button class="settings-tab ${activeTab === 'gameplay' ? 'active' : ''}"
                            data-tab="gameplay">Gameplay</button>
                </div>

                <div class="settings-content">
                    ${this.generateControlsTab()}
                    ${this.generateAudioTab()}
                    ${this.generateDisplayTab()}
                    ${this.generateGameplayTab()}
                </div>

                <div class="settings-footer">
                    <button class="menu-btn" id="btn-reset-settings">Reset to Default</button>
                    <button class="menu-btn primary" id="btn-close-settings">Done</button>
                </div>
            </div>
        `;
    }

    /**
     * Generate controls tab HTML
     */
    generateControlsTab() {
        const actions = [
            { key: 'moveLeft', label: 'Move Left' },
            { key: 'moveRight', label: 'Move Right' },
            { key: 'moveUp', label: 'Move Up' },
            { key: 'moveDown', label: 'Move Down' },
            { key: 'jump', label: 'Jump' },
            { key: 'attack', label: 'Attack' },
            { key: 'special', label: 'Special' },
            { key: 'parry', label: 'Parry/Dodge' },
            { key: 'grab', label: 'Grab' },
            { key: 'taunt', label: 'Taunt' }
        ];

        const generateBindingRows = (player) => {
            return actions.map(action => `
                <div class="binding-row">
                    <span class="binding-label">${action.label}</span>
                    <button class="binding-btn"
                            data-player="${player}"
                            data-action="${action.key}">
                        ${this.getKeyDisplayName(this.bindings[player][action.key])}
                    </button>
                </div>
            `).join('');
        };

        return `
            <div class="settings-tab-content" data-tab="controls">
                <div class="controls-container">
                    <div class="player-controls">
                        <h3>Player 1 (Keyboard)</h3>
                        ${generateBindingRows('player1')}
                        <button class="menu-btn small" data-reset="player1">Reset P1</button>
                    </div>
                    <div class="player-controls">
                        <h3>Player 2 (Keyboard)</h3>
                        ${generateBindingRows('player2')}
                        <button class="menu-btn small" data-reset="player2">Reset P2</button>
                    </div>
                </div>
                <div class="gamepad-status" id="gamepad-status">
                    <h3>Gamepads</h3>
                    <div id="gamepad-list">No gamepads connected</div>
                </div>
            </div>
        `;
    }

    /**
     * Generate audio tab HTML
     */
    generateAudioTab() {
        return `
            <div class="settings-tab-content" data-tab="audio" style="display:none">
                <div class="setting-group">
                    <label>Master Volume</label>
                    <input type="range" min="0" max="100"
                           value="${this.audio.masterVolume * 100}"
                           data-setting="masterVolume" data-type="audio">
                    <span class="value-display">${Math.round(this.audio.masterVolume * 100)}%</span>
                </div>
                <div class="setting-group">
                    <label>Music Volume</label>
                    <input type="range" min="0" max="100"
                           value="${this.audio.musicVolume * 100}"
                           data-setting="musicVolume" data-type="audio">
                    <span class="value-display">${Math.round(this.audio.musicVolume * 100)}%</span>
                </div>
                <div class="setting-group">
                    <label>Sound Effects</label>
                    <input type="range" min="0" max="100"
                           value="${this.audio.sfxVolume * 100}"
                           data-setting="sfxVolume" data-type="audio">
                    <span class="value-display">${Math.round(this.audio.sfxVolume * 100)}%</span>
                </div>
                <div class="setting-group">
                    <label>Voice Volume</label>
                    <input type="range" min="0" max="100"
                           value="${this.audio.voiceVolume * 100}"
                           data-setting="voiceVolume" data-type="audio">
                    <span class="value-display">${Math.round(this.audio.voiceVolume * 100)}%</span>
                </div>
                <div class="setting-group checkbox">
                    <label>
                        <input type="checkbox" ${this.audio.muted ? 'checked' : ''}
                               data-setting="muted" data-type="audio">
                        Mute All Audio
                    </label>
                </div>
            </div>
        `;
    }

    /**
     * Generate display tab HTML
     */
    generateDisplayTab() {
        return `
            <div class="settings-tab-content" data-tab="display" style="display:none">
                <div class="setting-group checkbox">
                    <label>
                        <input type="checkbox" ${this.display.screenShake ? 'checked' : ''}
                               data-setting="screenShake" data-type="display">
                        Screen Shake
                    </label>
                </div>
                <div class="setting-group checkbox">
                    <label>
                        <input type="checkbox" ${this.display.hitEffects ? 'checked' : ''}
                               data-setting="hitEffects" data-type="display">
                        Hit Effects
                    </label>
                </div>
                <div class="setting-group checkbox">
                    <label>
                        <input type="checkbox" ${this.display.showDamageNumbers ? 'checked' : ''}
                               data-setting="showDamageNumbers" data-type="display">
                        Damage Numbers
                    </label>
                </div>
                <div class="setting-group checkbox">
                    <label>
                        <input type="checkbox" ${this.display.showComboCounter ? 'checked' : ''}
                               data-setting="showComboCounter" data-type="display">
                        Combo Counter
                    </label>
                </div>
                <div class="setting-group checkbox">
                    <label>
                        <input type="checkbox" ${this.display.showInputDisplay ? 'checked' : ''}
                               data-setting="showInputDisplay" data-type="display">
                        Show Inputs (Training)
                    </label>
                </div>
                <div class="setting-group">
                    <label>Camera Zoom</label>
                    <input type="range" min="80" max="120"
                           value="${this.display.cameraZoom * 100}"
                           data-setting="cameraZoom" data-type="display">
                    <span class="value-display">${Math.round(this.display.cameraZoom * 100)}%</span>
                </div>
            </div>
        `;
    }

    /**
     * Generate gameplay tab HTML
     */
    generateGameplayTab() {
        return `
            <div class="settings-tab-content" data-tab="gameplay" style="display:none">
                <div class="setting-group checkbox">
                    <label>
                        <input type="checkbox" ${this.gameplay.tapJump ? 'checked' : ''}
                               data-setting="tapJump" data-type="gameplay">
                        Tap Jump (Up to Jump)
                    </label>
                </div>
                <div class="setting-group checkbox">
                    <label>
                        <input type="checkbox" ${this.gameplay.rumble ? 'checked' : ''}
                               data-setting="rumble" data-type="gameplay">
                        Controller Rumble
                    </label>
                </div>
                <div class="setting-group">
                    <label>C-Stick Mode</label>
                    <select data-setting="cStickMode" data-type="gameplay">
                        <option value="smash" ${this.gameplay.cStickMode === 'smash' ? 'selected' : ''}>
                            Smash Attacks
                        </option>
                        <option value="tilt" ${this.gameplay.cStickMode === 'tilt' ? 'selected' : ''}>
                            Tilt Attacks
                        </option>
                    </select>
                </div>
                <div class="setting-group">
                    <label>Stick Sensitivity</label>
                    <input type="range" min="20" max="80"
                           value="${this.gameplay.stickSensitivity * 100}"
                           data-setting="stickSensitivity" data-type="gameplay">
                    <span class="value-display">${Math.round(this.gameplay.stickSensitivity * 100)}%</span>
                </div>
                <div class="setting-group">
                    <label>Input Buffer (frames)</label>
                    <input type="range" min="0" max="12"
                           value="${this.gameplay.inputBuffer}"
                           data-setting="inputBuffer" data-type="gameplay">
                    <span class="value-display">${this.gameplay.inputBuffer}</span>
                </div>
            </div>
        `;
    }

    /**
     * Attach event listeners to settings menu
     */
    attachEventListeners(container) {
        // Tab switching
        container.querySelectorAll('.settings-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;

                // Update tab buttons
                container.querySelectorAll('.settings-tab').forEach(t => {
                    t.classList.toggle('active', t.dataset.tab === tabName);
                });

                // Show/hide content
                container.querySelectorAll('.settings-tab-content').forEach(content => {
                    content.style.display = content.dataset.tab === tabName ? 'block' : 'none';
                });
            });
        });

        // Key binding buttons
        container.querySelectorAll('.binding-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const player = btn.dataset.player;
                const action = btn.dataset.action;

                btn.textContent = 'Press a key...';
                btn.classList.add('rebinding');

                this.startRebind(player, action, (newKey, cancelled) => {
                    btn.classList.remove('rebinding');
                    if (!cancelled && newKey) {
                        btn.textContent = this.getKeyDisplayName(newKey);
                    } else {
                        btn.textContent = this.getKeyDisplayName(this.bindings[player][action]);
                    }
                });
            });
        });

        // Reset player controls
        container.querySelectorAll('[data-reset]').forEach(btn => {
            btn.addEventListener('click', () => {
                const player = btn.dataset.reset;
                this.resetControls(player);

                // Update displayed bindings
                container.querySelectorAll(`.binding-btn[data-player="${player}"]`).forEach(bindBtn => {
                    const action = bindBtn.dataset.action;
                    bindBtn.textContent = this.getKeyDisplayName(this.bindings[player][action]);
                });
            });
        });

        // Range sliders
        container.querySelectorAll('input[type="range"]').forEach(slider => {
            slider.addEventListener('input', () => {
                const setting = slider.dataset.setting;
                const type = slider.dataset.type;
                let value = parseInt(slider.value);

                // Convert to decimal for most settings
                if (setting !== 'inputBuffer') {
                    value = value / 100;
                }

                if (type === 'audio') {
                    this.setAudio(setting, value);
                } else if (type === 'display') {
                    this.setDisplay(setting, value);
                } else if (type === 'gameplay') {
                    this.setGameplay(setting, value);
                }

                // Update display
                const display = slider.parentElement.querySelector('.value-display');
                if (display) {
                    if (setting === 'inputBuffer') {
                        display.textContent = value;
                    } else {
                        display.textContent = `${Math.round(value * 100)}%`;
                    }
                }
            });
        });

        // Checkboxes
        container.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                const setting = checkbox.dataset.setting;
                const type = checkbox.dataset.type;
                const value = checkbox.checked;

                if (type === 'audio') {
                    this.setAudio(setting, value);
                } else if (type === 'display') {
                    this.setDisplay(setting, value);
                } else if (type === 'gameplay') {
                    this.setGameplay(setting, value);
                }
            });
        });

        // Select dropdowns
        container.querySelectorAll('select').forEach(select => {
            select.addEventListener('change', () => {
                const setting = select.dataset.setting;
                const type = select.dataset.type;
                const value = select.value;

                if (type === 'gameplay') {
                    this.setGameplay(setting, value);
                }
            });
        });

        // Reset all button
        const resetBtn = container.querySelector('#btn-reset-settings');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                if (confirm('Reset all settings to default?')) {
                    this.resetAll();
                    // Refresh the menu
                    container.innerHTML = this.generateMenuHTML();
                    this.attachEventListeners(container);
                }
            });
        }
    }

    /**
     * Update gamepad display
     */
    updateGamepadDisplay(gamepads) {
        const list = document.getElementById('gamepad-list');
        if (!list) return;

        if (gamepads.length === 0) {
            list.innerHTML = '<p>No gamepads connected</p>';
        } else {
            list.innerHTML = gamepads.map((gp, i) => `
                <div class="gamepad-item">
                    <span class="gamepad-icon">🎮</span>
                    <span class="gamepad-name">${gp.id}</span>
                    <span class="gamepad-index">Player ${i + 1}</span>
                </div>
            `).join('');
        }
    }
}

// Global settings instance
const settings = new SettingsManager();

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SettingsManager;
}
