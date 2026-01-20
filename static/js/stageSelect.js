/**
 * Arena Brawl - Stage Select UI
 * Stage selection with previews, hazard info, and unlock status
 */

class StageSelectUI {
    constructor() {
        this.selectedStage = 'Battlefield';
        this.hoveredStage = null;

        // Stage data
        this.stageData = {
            'Street': {
                name: 'Street',
                description: 'A classic street fighting arena. Simple layout perfect for beginners.',
                category: 'Competitive',
                hasHazards: false,
                size: 'Medium',
                platforms: 'Main + 2 Side',
                theme: 'Urban',
                music: 'Street Theme',
                color: '#666666'
            },
            'Battlefield': {
                name: 'Battlefield',
                description: 'The iconic stage with a main platform and three floating platforms in a triangle formation.',
                category: 'Competitive',
                hasHazards: false,
                size: 'Medium',
                platforms: 'Main + 3 Triangle',
                theme: 'Floating Island',
                music: 'Battlefield Theme',
                color: '#88aaff'
            },
            'Final Destination': {
                name: 'Final Destination',
                description: 'A completely flat stage with no platforms. Pure skill determines the winner.',
                category: 'Competitive',
                hasHazards: false,
                size: 'Large',
                platforms: 'Main Only',
                theme: 'Space',
                music: 'Final Destination Theme',
                color: '#4444ff'
            },
            'Training Room': {
                name: 'Training Room',
                description: 'Practice your combos and techniques with a grid background and no distractions.',
                category: 'Training',
                hasHazards: false,
                size: 'Large',
                platforms: 'Main + Adjustable',
                theme: 'Practice',
                music: 'None',
                color: '#444444'
            },
            'Skyline': {
                name: 'Skyline',
                description: 'Fight atop city rooftops at night. Watch your footing!',
                category: 'Competitive',
                hasHazards: false,
                size: 'Medium',
                platforms: 'Main + 2 Side',
                theme: 'Night City',
                music: 'Skyline Theme',
                color: '#223355'
            },
            'Dojo': {
                name: 'Dojo',
                description: 'A traditional Japanese temple with a single center platform.',
                category: 'Competitive',
                hasHazards: false,
                size: 'Medium',
                platforms: 'Main + 1 Center',
                theme: 'Japanese Temple',
                music: 'Dojo Theme',
                color: '#aa4444'
            },
            'Volcano': {
                name: 'Volcano',
                description: 'Crumbling platforms over rising lava. Fall in and it\'s an instant KO!',
                category: 'Hazard',
                hasHazards: true,
                hazardDescription: 'Rising lava damages and KOs players who fall in',
                size: 'Medium',
                platforms: 'Crumbling',
                theme: 'Volcanic',
                music: 'Volcano Theme',
                color: '#ff4400'
            },
            'Thunderstorm': {
                name: 'Thunderstorm',
                description: 'Moving platforms amidst a raging thunderstorm with lightning strikes.',
                category: 'Hazard',
                hasHazards: true,
                hazardDescription: 'Lightning strikes random locations dealing damage',
                size: 'Large',
                platforms: 'Moving',
                theme: 'Storm',
                music: 'Storm Theme',
                color: '#6666aa'
            },
            'Frozen Lake': {
                name: 'Frozen Lake',
                description: 'An icy arena where the ice can break under heavy impacts.',
                category: 'Hazard',
                hasHazards: true,
                hazardDescription: 'Slippery ice, breaks under heavy attacks',
                size: 'Medium',
                platforms: 'Main + Ice',
                theme: 'Winter',
                music: 'Frozen Theme',
                color: '#88ddff'
            },
            'Windmill': {
                name: 'Windmill',
                description: 'Platforms that rotate around a giant windmill. Time your movements!',
                category: 'Hazard',
                hasHazards: true,
                hazardDescription: 'Rotating platforms and wind gusts',
                size: 'Large',
                platforms: 'Rotating',
                theme: 'Dutch Countryside',
                music: 'Windmill Theme',
                color: '#66aa66'
            }
        };

        // Stage options
        this.hazardsEnabled = true;
        this.randomStage = false;

        // Callbacks
        this.onSelect = null;
        this.onConfirm = null;
        this.onBack = null;
    }

    /**
     * Generate stage select HTML
     */
    generateHTML(options = {}) {
        const { showBack = true, title = 'Select Stage', showOptions = true } = options;

        return `
            <div class="stage-select-container">
                <h1 class="select-title">${title}</h1>

                ${showOptions ? this.generateOptions() : ''}

                <div class="stage-select-layout">
                    <div class="stage-grid" id="stage-grid">
                        ${this.generateStageGrid()}
                    </div>

                    <div class="stage-preview" id="stage-preview">
                        ${this.generatePreview(this.selectedStage)}
                    </div>
                </div>

                <div class="select-actions">
                    ${showBack ? '<button class="menu-btn" id="btn-stage-back">Back</button>' : ''}
                    <button class="menu-btn" id="btn-stage-random">Random</button>
                    <button class="menu-btn primary" id="btn-stage-confirm">Confirm</button>
                </div>
            </div>
        `;
    }

    /**
     * Generate stage options
     */
    generateOptions() {
        return `
            <div class="stage-options">
                <label class="option-toggle">
                    <input type="checkbox" id="toggle-hazards" ${this.hazardsEnabled ? 'checked' : ''}>
                    <span>Stage Hazards</span>
                </label>
            </div>
        `;
    }

    /**
     * Generate stage grid
     */
    generateStageGrid() {
        const stages = Object.keys(this.stageData);
        const progressionAvailable = typeof progression !== 'undefined';

        // Group by category
        const categories = {
            'Competitive': [],
            'Hazard': [],
            'Training': []
        };

        stages.forEach(name => {
            const stage = this.stageData[name];
            categories[stage.category]?.push(name) || categories['Competitive'].push(name);
        });

        let html = '';

        // Competitive stages
        if (categories['Competitive'].length > 0) {
            html += '<div class="stage-category"><h3>Competitive Stages</h3><div class="category-grid">';
            html += categories['Competitive'].map(name => this.generateStageCard(name, progressionAvailable)).join('');
            html += '</div></div>';
        }

        // Hazard stages
        if (categories['Hazard'].length > 0) {
            html += '<div class="stage-category"><h3>Hazard Stages</h3><div class="category-grid">';
            html += categories['Hazard'].map(name => this.generateStageCard(name, progressionAvailable)).join('');
            html += '</div></div>';
        }

        // Training
        if (categories['Training'].length > 0) {
            html += '<div class="stage-category"><h3>Training</h3><div class="category-grid">';
            html += categories['Training'].map(name => this.generateStageCard(name, progressionAvailable)).join('');
            html += '</div></div>';
        }

        return html;
    }

    /**
     * Generate single stage card
     */
    generateStageCard(name, progressionAvailable) {
        const stage = this.stageData[name];
        const isSelected = name === this.selectedStage;
        const isUnlocked = progressionAvailable ? progression.isStageUnlocked(name) : true;
        const isDisabled = stage.hasHazards && !this.hazardsEnabled;

        return `
            <div class="stage-card ${isSelected ? 'selected' : ''} ${!isUnlocked ? 'locked' : ''} ${isDisabled ? 'disabled' : ''}"
                 data-stage="${name}"
                 style="--stage-color: ${stage.color}">
                <div class="stage-thumbnail" style="background: linear-gradient(135deg, ${stage.color}, ${this.darkenColor(stage.color)})">
                    ${!isUnlocked ? '<div class="lock-overlay">🔒</div>' : ''}
                    ${stage.hasHazards ? '<div class="hazard-badge">⚠️</div>' : ''}
                </div>
                <div class="stage-name">${name}</div>
                <div class="stage-category-badge">${stage.category}</div>
            </div>
        `;
    }

    /**
     * Generate stage preview panel
     */
    generatePreview(stageName) {
        const stage = this.stageData[stageName];
        if (!stage) return '<div class="no-preview">Select a stage</div>';

        const progressionAvailable = typeof progression !== 'undefined';
        const isUnlocked = progressionAvailable ? progression.isStageUnlocked(stageName) : true;

        return `
            <div class="preview-content">
                <div class="preview-thumbnail" style="background: linear-gradient(135deg, ${stage.color}, ${this.darkenColor(stage.color)})">
                    ${!isUnlocked ? '<div class="lock-icon">🔒</div>' : ''}
                </div>

                <h2 class="preview-name">${stage.name}</h2>
                <div class="preview-theme">${stage.theme}</div>

                ${!isUnlocked ? `
                    <div class="unlock-requirement">
                        <h3>Unlock Requirement</h3>
                        <p>${this.getUnlockRequirement(stageName)}</p>
                    </div>
                ` : `
                    <div class="preview-description">
                        <p>${stage.description}</p>
                    </div>

                    <div class="stage-info-grid">
                        <div class="info-item">
                            <span class="label">Size</span>
                            <span class="value">${stage.size}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Platforms</span>
                            <span class="value">${stage.platforms}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Category</span>
                            <span class="value">${stage.category}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Music</span>
                            <span class="value">${stage.music}</span>
                        </div>
                    </div>

                    ${stage.hasHazards ? `
                        <div class="hazard-warning">
                            <span class="hazard-icon">⚠️</span>
                            <div class="hazard-info">
                                <strong>Stage Hazard</strong>
                                <p>${stage.hazardDescription}</p>
                            </div>
                        </div>
                    ` : ''}
                `}
            </div>
        `;
    }

    /**
     * Get unlock requirement text
     */
    getUnlockRequirement(stageName) {
        const requirements = {
            'Skyline': 'Play 10 matches',
            'Dojo': 'Win 5 matches',
            'Volcano': 'Get 50 total KOs',
            'Thunderstorm': 'Play 3 matches as Storm',
            'Frozen Lake': 'Unlock Frost',
            'Windmill': 'Deal 5000 total damage'
        };
        return requirements[stageName] || 'Unknown';
    }

    /**
     * Darken a hex color
     */
    darkenColor(hex) {
        const num = parseInt(hex.replace('#', ''), 16);
        const r = Math.max(0, (num >> 16) - 40);
        const g = Math.max(0, ((num >> 8) & 0x00FF) - 40);
        const b = Math.max(0, (num & 0x0000FF) - 40);
        return `#${(r << 16 | g << 8 | b).toString(16).padStart(6, '0')}`;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners(container) {
        // Stage card clicks
        container.querySelectorAll('.stage-card').forEach(card => {
            card.addEventListener('click', () => {
                const stageName = card.dataset.stage;
                if (!card.classList.contains('locked') && !card.classList.contains('disabled')) {
                    this.selectStage(stageName, container);
                }
            });

            card.addEventListener('mouseenter', () => {
                const stageName = card.dataset.stage;
                this.hoverStage(stageName, container);
            });
        });

        // Hazards toggle
        container.querySelector('#toggle-hazards')?.addEventListener('change', (e) => {
            this.hazardsEnabled = e.target.checked;
            this.refreshGrid(container);
        });

        // Random button
        container.querySelector('#btn-stage-random')?.addEventListener('click', () => {
            this.selectRandomStage(container);
        });

        // Confirm button
        container.querySelector('#btn-stage-confirm')?.addEventListener('click', () => {
            const progressionAvailable = typeof progression !== 'undefined';
            const isUnlocked = progressionAvailable ? progression.isStageUnlocked(this.selectedStage) : true;

            if (isUnlocked) {
                if (this.onConfirm) {
                    this.onConfirm(this.selectedStage, this.hazardsEnabled);
                }
            }
        });

        // Back button
        container.querySelector('#btn-stage-back')?.addEventListener('click', () => {
            if (this.onBack) {
                this.onBack();
            }
        });

        // Keyboard navigation
        this.keyHandler = (e) => {
            const stages = Object.keys(this.stageData).filter(name => {
                const stage = this.stageData[name];
                const progressionAvailable = typeof progression !== 'undefined';
                const isUnlocked = progressionAvailable ? progression.isStageUnlocked(name) : true;
                const isDisabled = stage.hasHazards && !this.hazardsEnabled;
                return isUnlocked && !isDisabled;
            });

            const currentIndex = stages.indexOf(this.selectedStage);
            let newIndex = currentIndex;

            const columns = 3;

            switch (e.code) {
                case 'ArrowLeft':
                    newIndex = Math.max(0, currentIndex - 1);
                    break;
                case 'ArrowRight':
                    newIndex = Math.min(stages.length - 1, currentIndex + 1);
                    break;
                case 'ArrowUp':
                    newIndex = Math.max(0, currentIndex - columns);
                    break;
                case 'ArrowDown':
                    newIndex = Math.min(stages.length - 1, currentIndex + columns);
                    break;
                case 'Enter':
                case 'Space':
                    container.querySelector('#btn-stage-confirm')?.click();
                    return;
                case 'Escape':
                    container.querySelector('#btn-stage-back')?.click();
                    return;
                case 'KeyR':
                    this.selectRandomStage(container);
                    return;
            }

            if (newIndex !== currentIndex && stages[newIndex]) {
                e.preventDefault();
                this.selectStage(stages[newIndex], container);
            }
        };
        document.addEventListener('keydown', this.keyHandler);
    }

    /**
     * Select a stage
     */
    selectStage(stageName, container) {
        this.selectedStage = stageName;

        // Update grid selection
        container.querySelectorAll('.stage-card').forEach(card => {
            card.classList.toggle('selected', card.dataset.stage === stageName);
        });

        // Update preview
        const preview = container.querySelector('#stage-preview');
        if (preview) {
            preview.innerHTML = this.generatePreview(stageName);
        }

        // Callback
        if (this.onSelect) {
            this.onSelect(stageName);
        }
    }

    /**
     * Hover a stage
     */
    hoverStage(stageName, container) {
        this.hoveredStage = stageName;
    }

    /**
     * Select random stage
     */
    selectRandomStage(container) {
        const stages = Object.keys(this.stageData).filter(name => {
            const stage = this.stageData[name];
            const progressionAvailable = typeof progression !== 'undefined';
            const isUnlocked = progressionAvailable ? progression.isStageUnlocked(name) : true;
            const isDisabled = stage.hasHazards && !this.hazardsEnabled;
            return isUnlocked && !isDisabled;
        });

        if (stages.length > 0) {
            const randomIndex = Math.floor(Math.random() * stages.length);
            this.selectStage(stages[randomIndex], container);
        }
    }

    /**
     * Refresh grid (after hazards toggle)
     */
    refreshGrid(container) {
        const grid = container.querySelector('#stage-grid');
        if (grid) {
            grid.innerHTML = this.generateStageGrid();
            this.attachEventListeners(container);
        }
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
     * Get selected stage
     */
    getSelectedStage() {
        return this.selectedStage;
    }

    /**
     * Are hazards enabled
     */
    areHazardsEnabled() {
        return this.hazardsEnabled;
    }

    /**
     * Generate CSS styles
     */
    static getStyles() {
        return `
            .stage-select-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
                max-width: 1200px;
                margin: 0 auto;
            }

            .stage-options {
                margin-bottom: 20px;
            }

            .option-toggle {
                display: flex;
                align-items: center;
                gap: 10px;
                cursor: pointer;
                padding: 10px 20px;
                background: rgba(40, 40, 60, 0.8);
                border-radius: 20px;
            }

            .option-toggle input {
                width: 20px;
                height: 20px;
            }

            .stage-select-layout {
                display: flex;
                gap: 30px;
                width: 100%;
            }

            .stage-grid {
                flex: 2;
            }

            .stage-category {
                margin-bottom: 20px;
            }

            .stage-category h3 {
                margin-bottom: 10px;
                color: #aaa;
                font-size: 0.9em;
                text-transform: uppercase;
            }

            .category-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
            }

            .stage-card {
                background: rgba(40, 40, 60, 0.8);
                border: 3px solid #444;
                border-radius: 10px;
                padding: 10px;
                cursor: pointer;
                transition: all 0.2s;
                text-align: center;
            }

            .stage-card:hover:not(.locked):not(.disabled) {
                border-color: var(--stage-color, #666);
                transform: scale(1.05);
            }

            .stage-card.selected {
                border-color: var(--stage-color, #ffd700);
                box-shadow: 0 0 20px var(--stage-color, rgba(255, 215, 0, 0.3));
            }

            .stage-card.locked,
            .stage-card.disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }

            .stage-thumbnail {
                width: 100%;
                height: 80px;
                border-radius: 5px;
                position: relative;
                margin-bottom: 10px;
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
                border-radius: 5px;
            }

            .hazard-badge {
                position: absolute;
                top: 5px;
                right: 5px;
                font-size: 1.2em;
            }

            .stage-name {
                font-weight: bold;
                margin-bottom: 5px;
            }

            .stage-category-badge {
                font-size: 0.8em;
                color: #888;
            }

            .stage-preview {
                flex: 1;
                min-width: 300px;
                background: rgba(40, 40, 60, 0.9);
                border-radius: 15px;
                padding: 20px;
            }

            .preview-thumbnail {
                width: 100%;
                height: 150px;
                border-radius: 10px;
                margin-bottom: 15px;
                position: relative;
            }

            .preview-thumbnail .lock-icon {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 3em;
            }

            .preview-name {
                font-size: 1.5em;
                margin: 0 0 5px;
            }

            .preview-theme {
                color: #888;
                margin-bottom: 15px;
            }

            .stage-info-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin: 15px 0;
            }

            .info-item {
                display: flex;
                flex-direction: column;
            }

            .info-item .label {
                color: #888;
                font-size: 0.85em;
            }

            .info-item .value {
                font-weight: bold;
            }

            .hazard-warning {
                display: flex;
                gap: 15px;
                background: rgba(255, 165, 0, 0.1);
                border: 1px solid #ffa500;
                border-radius: 10px;
                padding: 15px;
                margin-top: 15px;
            }

            .hazard-icon {
                font-size: 2em;
            }

            .hazard-info strong {
                color: #ffa500;
            }

            .hazard-info p {
                margin: 5px 0 0;
                color: #aaa;
            }

            .unlock-requirement {
                background: rgba(100, 100, 100, 0.2);
                border-radius: 10px;
                padding: 15px;
                margin-top: 15px;
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
const stageSelect = new StageSelectUI();

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StageSelectUI;
}
