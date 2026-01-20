/**
 * Arena Brawl - Character Select UI
 * Full character selection with previews, stats, and unlock status
 */

class CharacterSelectUI {
    constructor() {
        this.selectedCharacter = 'Storm';
        this.hoveredCharacter = null;
        this.playerSlots = new Map(); // For multiplayer

        // Character data
        this.characterData = {
            'Storm': {
                name: 'Storm',
                tagline: 'The All-Rounder',
                description: 'A balanced fighter with electric abilities. Great for learning the game.',
                playstyle: 'Balanced',
                difficulty: 1,
                stats: { power: 3, speed: 3, weight: 3, recovery: 3 },
                color: '#FFD700',
                special: 'Lightning Strike'
            },
            'Blaze': {
                name: 'Blaze',
                tagline: 'The Rushdown King',
                description: 'An aggressive fighter who excels at close-range combat with fire-based attacks.',
                playstyle: 'Rushdown',
                difficulty: 2,
                stats: { power: 4, speed: 4, weight: 2, recovery: 3 },
                color: '#FF4500',
                special: 'Fire Dash'
            },
            'Tank': {
                name: 'Tank',
                tagline: 'The Immovable Force',
                description: 'A heavy bruiser with super armor on smash attacks. Hard to knock out.',
                playstyle: 'Defensive',
                difficulty: 2,
                stats: { power: 5, speed: 1, weight: 5, recovery: 2 },
                color: '#4169E1',
                special: 'Shield Block'
            },
            'Shadow': {
                name: 'Shadow',
                tagline: 'The Glass Cannon',
                description: 'A fragile but deadly assassin with teleportation and high damage output.',
                playstyle: 'Hit & Run',
                difficulty: 4,
                stats: { power: 4, speed: 5, weight: 1, recovery: 4 },
                color: '#8A2BE2',
                special: 'Teleport'
            },
            'Frost': {
                name: 'Frost',
                tagline: 'The Ice Queen',
                description: 'A zoner who controls space with ice projectiles and freeze traps.',
                playstyle: 'Zoner',
                difficulty: 3,
                stats: { power: 3, speed: 2, weight: 2, recovery: 3 },
                color: '#88FFFF',
                special: 'Ice Shard'
            },
            'Titan': {
                name: 'Titan',
                tagline: 'The Grappler',
                description: 'A massive wrestler with devastating command grabs and piledriver.',
                playstyle: 'Grappler',
                difficulty: 3,
                stats: { power: 5, speed: 1, weight: 5, recovery: 1 },
                color: '#8B4513',
                special: 'Command Grab'
            },
            'Whisper': {
                name: 'Whisper',
                tagline: 'The Trickster',
                description: 'A deceptive fighter using clone illusions and counter attacks.',
                playstyle: 'Tricky',
                difficulty: 5,
                stats: { power: 3, speed: 4, weight: 2, recovery: 3 },
                color: '#FF00FF',
                special: 'Clone Illusion'
            },
            'Volt': {
                name: 'Volt',
                tagline: 'Speed Demon',
                description: 'The fastest fighter in the game with electric dash chains.',
                playstyle: 'Speed',
                difficulty: 4,
                stats: { power: 2, speed: 5, weight: 1, recovery: 4 },
                color: '#FFFF00',
                special: 'Electric Chain'
            },
            'Golem': {
                name: 'Golem',
                tagline: 'The Mountain',
                description: 'The heaviest and slowest fighter with rock armor and ground pound.',
                playstyle: 'Super Heavy',
                difficulty: 2,
                stats: { power: 5, speed: 1, weight: 5, recovery: 1 },
                color: '#666666',
                special: 'Rock Armor'
            },
            'Aria': {
                name: 'Aria',
                tagline: 'Queen of the Skies',
                description: 'An aerial specialist with the best air game and wind-based attacks.',
                playstyle: 'Aerial',
                difficulty: 4,
                stats: { power: 2, speed: 4, weight: 2, recovery: 5 },
                color: '#AAFFAA',
                special: 'Wind Gust'
            },
            'Fang': {
                name: 'Fang',
                tagline: 'The Berserker',
                description: 'A wild brawler with bite attacks and a rage mechanic that powers up at high damage.',
                playstyle: 'Brawler',
                difficulty: 3,
                stats: { power: 4, speed: 3, weight: 3, recovery: 2 },
                color: '#884400',
                special: 'Rage Boost'
            },
            'Nova': {
                name: 'Nova',
                tagline: 'The Shoto',
                description: 'A classic fighting game character with fireball, uppercut, and hurricane kick.',
                playstyle: 'Shoto',
                difficulty: 2,
                stats: { power: 3, speed: 3, weight: 3, recovery: 3 },
                color: '#FF8800',
                special: 'Hadouken'
            }
        };

        // Callbacks
        this.onSelect = null;
        this.onConfirm = null;
        this.onBack = null;
    }

    /**
     * Generate character select HTML
     */
    generateHTML(options = {}) {
        const { showBack = true, title = 'Select Your Fighter' } = options;

        return `
            <div class="character-select-container">
                <h1 class="select-title">${title}</h1>

                <div class="character-select-layout">
                    <div class="character-grid" id="character-grid">
                        ${this.generateCharacterGrid()}
                    </div>

                    <div class="character-preview" id="character-preview">
                        ${this.generatePreview(this.selectedCharacter)}
                    </div>
                </div>

                <div class="select-actions">
                    ${showBack ? '<button class="menu-btn" id="btn-char-back">Back</button>' : ''}
                    <button class="menu-btn primary" id="btn-char-confirm">Confirm</button>
                </div>
            </div>
        `;
    }

    /**
     * Generate character grid
     */
    generateCharacterGrid() {
        const characters = Object.keys(this.characterData);
        const progressionAvailable = typeof progression !== 'undefined';

        return characters.map(name => {
            const char = this.characterData[name];
            const isSelected = name === this.selectedCharacter;
            const isUnlocked = progressionAvailable ? progression.isCharacterUnlocked(name) : true;
            const progress = progressionAvailable ? progression.getCharacterProgress(name) : { progress: 1 };

            return `
                <div class="character-card ${isSelected ? 'selected' : ''} ${!isUnlocked ? 'locked' : ''}"
                     data-character="${name}"
                     style="--char-color: ${char.color}">
                    <div class="character-portrait">
                        <div class="portrait-bg" style="background: ${char.color}"></div>
                        ${!isUnlocked ? '<div class="lock-overlay">🔒</div>' : ''}
                    </div>
                    <div class="character-name">${name}</div>
                    ${!isUnlocked ? `
                        <div class="unlock-progress">
                            <div class="progress-bar" style="width: ${progress.progress * 100}%"></div>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
    }

    /**
     * Generate character preview panel
     */
    generatePreview(characterName) {
        const char = this.characterData[characterName];
        if (!char) return '<div class="no-preview">Select a character</div>';

        const progressionAvailable = typeof progression !== 'undefined';
        const isUnlocked = progressionAvailable ? progression.isCharacterUnlocked(characterName) : true;
        const unlockInfo = progressionAvailable ? progression.getCharacterProgress(characterName) : null;

        return `
            <div class="preview-content">
                <div class="preview-header">
                    <div class="preview-portrait" style="background: ${char.color}">
                        ${!isUnlocked ? '<div class="lock-icon">🔒</div>' : ''}
                    </div>
                    <div class="preview-info">
                        <h2 class="preview-name">${char.name}</h2>
                        <div class="preview-tagline">${char.tagline}</div>
                        <div class="preview-playstyle">
                            <span class="label">Playstyle:</span>
                            <span class="value">${char.playstyle}</span>
                        </div>
                    </div>
                </div>

                ${!isUnlocked ? `
                    <div class="unlock-requirement">
                        <h3>Unlock Requirement</h3>
                        <p>${unlockInfo?.description || 'Unknown'}</p>
                        <div class="unlock-progress-bar">
                            <div class="progress-fill" style="width: ${(unlockInfo?.progress || 0) * 100}%"></div>
                        </div>
                        <span class="progress-text">${Math.floor((unlockInfo?.progress || 0) * 100)}%</span>
                    </div>
                ` : `
                    <div class="preview-description">
                        <p>${char.description}</p>
                    </div>

                    <div class="preview-stats">
                        <h3>Stats</h3>
                        <div class="stat-bars">
                            ${this.generateStatBar('Power', char.stats.power)}
                            ${this.generateStatBar('Speed', char.stats.speed)}
                            ${this.generateStatBar('Weight', char.stats.weight)}
                            ${this.generateStatBar('Recovery', char.stats.recovery)}
                        </div>
                    </div>

                    <div class="preview-special">
                        <h3>Special Move</h3>
                        <div class="special-name">${char.special}</div>
                    </div>

                    <div class="preview-difficulty">
                        <span class="label">Difficulty:</span>
                        <span class="stars">${'⭐'.repeat(char.difficulty)}${'☆'.repeat(5 - char.difficulty)}</span>
                    </div>
                `}
            </div>
        `;
    }

    /**
     * Generate stat bar HTML
     */
    generateStatBar(label, value) {
        const maxValue = 5;
        const percentage = (value / maxValue) * 100;

        return `
            <div class="stat-bar-row">
                <span class="stat-label">${label}</span>
                <div class="stat-bar">
                    <div class="stat-fill" style="width: ${percentage}%"></div>
                </div>
                <span class="stat-value">${value}/${maxValue}</span>
            </div>
        `;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners(container) {
        // Character card clicks
        container.querySelectorAll('.character-card').forEach(card => {
            card.addEventListener('click', () => {
                const characterName = card.dataset.character;
                this.selectCharacter(characterName, container);
            });

            card.addEventListener('mouseenter', () => {
                const characterName = card.dataset.character;
                this.hoverCharacter(characterName, container);
            });
        });

        // Confirm button
        container.querySelector('#btn-char-confirm')?.addEventListener('click', () => {
            const progressionAvailable = typeof progression !== 'undefined';
            const isUnlocked = progressionAvailable ? progression.isCharacterUnlocked(this.selectedCharacter) : true;

            if (isUnlocked) {
                if (this.onConfirm) {
                    this.onConfirm(this.selectedCharacter);
                }
            }
        });

        // Back button
        container.querySelector('#btn-char-back')?.addEventListener('click', () => {
            if (this.onBack) {
                this.onBack();
            }
        });

        // Keyboard navigation
        this.keyHandler = (e) => {
            const characters = Object.keys(this.characterData);
            const currentIndex = characters.indexOf(this.selectedCharacter);
            let newIndex = currentIndex;

            const columns = 4; // Grid columns

            switch (e.code) {
                case 'ArrowLeft':
                    newIndex = Math.max(0, currentIndex - 1);
                    break;
                case 'ArrowRight':
                    newIndex = Math.min(characters.length - 1, currentIndex + 1);
                    break;
                case 'ArrowUp':
                    newIndex = Math.max(0, currentIndex - columns);
                    break;
                case 'ArrowDown':
                    newIndex = Math.min(characters.length - 1, currentIndex + columns);
                    break;
                case 'Enter':
                case 'Space':
                    container.querySelector('#btn-char-confirm')?.click();
                    return;
                case 'Escape':
                    container.querySelector('#btn-char-back')?.click();
                    return;
            }

            if (newIndex !== currentIndex) {
                e.preventDefault();
                this.selectCharacter(characters[newIndex], container);
            }
        };
        document.addEventListener('keydown', this.keyHandler);
    }

    /**
     * Select a character
     */
    selectCharacter(characterName, container) {
        this.selectedCharacter = characterName;

        // Update grid selection
        container.querySelectorAll('.character-card').forEach(card => {
            card.classList.toggle('selected', card.dataset.character === characterName);
        });

        // Update preview
        const preview = container.querySelector('#character-preview');
        if (preview) {
            preview.innerHTML = this.generatePreview(characterName);
        }

        // Callback
        if (this.onSelect) {
            this.onSelect(characterName);
        }

        // Play select sound (if audio system available)
        // audio.playSound('select');
    }

    /**
     * Hover a character
     */
    hoverCharacter(characterName, container) {
        this.hoveredCharacter = characterName;

        // Could show a tooltip or update preview temporarily
    }

    /**
     * Clean up event listeners
     */
    destroy() {
        if (this.keyHandler) {
            document.removeEventListener('keydown', this.keyHandler);
            this.keyHandler = null;
        }
    }

    /**
     * Get selected character
     */
    getSelectedCharacter() {
        return this.selectedCharacter;
    }

    /**
     * Set selected character
     */
    setSelectedCharacter(characterName) {
        if (this.characterData[characterName]) {
            this.selectedCharacter = characterName;
        }
    }

    /**
     * Generate CSS styles
     */
    static getStyles() {
        return `
            .character-select-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
                max-width: 1200px;
                margin: 0 auto;
            }

            .select-title {
                font-size: 2.5em;
                margin-bottom: 20px;
                text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
            }

            .character-select-layout {
                display: flex;
                gap: 30px;
                width: 100%;
            }

            .character-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                flex: 2;
            }

            .character-card {
                background: rgba(40, 40, 60, 0.8);
                border: 3px solid #444;
                border-radius: 10px;
                padding: 10px;
                cursor: pointer;
                transition: all 0.2s;
                text-align: center;
            }

            .character-card:hover {
                border-color: var(--char-color, #666);
                transform: scale(1.05);
            }

            .character-card.selected {
                border-color: var(--char-color, #ffd700);
                box-shadow: 0 0 20px var(--char-color, rgba(255, 215, 0, 0.5));
            }

            .character-card.locked {
                opacity: 0.6;
            }

            .character-portrait {
                width: 80px;
                height: 80px;
                margin: 0 auto 10px;
                border-radius: 50%;
                position: relative;
                overflow: hidden;
            }

            .portrait-bg {
                width: 100%;
                height: 100%;
                border-radius: 50%;
            }

            .lock-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(0, 0, 0, 0.5);
                font-size: 2em;
            }

            .character-name {
                font-weight: bold;
                font-size: 0.9em;
            }

            .unlock-progress {
                height: 4px;
                background: #333;
                border-radius: 2px;
                margin-top: 5px;
                overflow: hidden;
            }

            .unlock-progress .progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #ffd700, #ffaa00);
            }

            .character-preview {
                flex: 1;
                min-width: 300px;
                background: rgba(40, 40, 60, 0.9);
                border-radius: 15px;
                padding: 20px;
            }

            .preview-header {
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }

            .preview-portrait {
                width: 100px;
                height: 100px;
                border-radius: 15px;
                position: relative;
            }

            .preview-portrait .lock-icon {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 2em;
            }

            .preview-name {
                font-size: 1.8em;
                margin: 0;
            }

            .preview-tagline {
                color: #aaa;
                font-style: italic;
            }

            .preview-playstyle {
                margin-top: 10px;
            }

            .preview-description {
                margin: 15px 0;
                line-height: 1.5;
            }

            .preview-stats h3,
            .preview-special h3 {
                margin: 15px 0 10px;
                font-size: 1.1em;
            }

            .stat-bar-row {
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 5px 0;
            }

            .stat-label {
                width: 70px;
                color: #aaa;
            }

            .stat-bar {
                flex: 1;
                height: 10px;
                background: #333;
                border-radius: 5px;
                overflow: hidden;
            }

            .stat-fill {
                height: 100%;
                background: linear-gradient(90deg, #4a90d9, #67b26f);
                transition: width 0.3s;
            }

            .stat-value {
                width: 40px;
                text-align: right;
                color: #888;
                font-size: 0.9em;
            }

            .special-name {
                color: #ffd700;
                font-size: 1.2em;
            }

            .preview-difficulty .stars {
                font-size: 1.2em;
            }

            .unlock-requirement {
                background: rgba(255, 165, 0, 0.1);
                border: 1px solid #ffa500;
                border-radius: 10px;
                padding: 15px;
                margin: 15px 0;
            }

            .unlock-requirement h3 {
                margin: 0 0 10px;
                color: #ffa500;
            }

            .unlock-progress-bar {
                height: 8px;
                background: #333;
                border-radius: 4px;
                overflow: hidden;
                margin: 10px 0;
            }

            .unlock-progress-bar .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #ffa500, #ffd700);
            }

            .progress-text {
                font-size: 0.9em;
                color: #888;
            }

            .select-actions {
                display: flex;
                gap: 15px;
                margin-top: 30px;
            }
        `;
    }
}

// Global instance
const characterSelect = new CharacterSelectUI();

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CharacterSelectUI;
}
