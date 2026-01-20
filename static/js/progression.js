/**
 * Arena Brawl - Progression System
 * Character unlocks, stage unlocks, and achievements
 */

class ProgressionManager {
    constructor() {
        // Default unlocked content
        this.defaultUnlocked = {
            characters: ['Storm', 'Blaze', 'Tank', 'Shadow'],
            stages: ['Street', 'Battlefield', 'Final Destination', 'Training Room']
        };

        // All content
        this.allCharacters = [
            'Storm', 'Blaze', 'Tank', 'Shadow',
            'Frost', 'Titan', 'Whisper', 'Volt',
            'Golem', 'Aria', 'Fang', 'Nova'
        ];

        this.allStages = [
            'Street', 'Battlefield', 'Final Destination', 'Training Room',
            'Skyline', 'Dojo', 'Volcano', 'Thunderstorm',
            'Frozen Lake', 'Windmill'
        ];

        // Unlock conditions
        this.unlockConditions = {
            characters: {
                'Frost': { type: 'matches', count: 5, description: 'Play 5 matches' },
                'Titan': { type: 'kos', count: 20, description: 'Get 20 KOs' },
                'Whisper': { type: 'wins', count: 3, description: 'Win 3 matches' },
                'Volt': { type: 'combo', count: 5, description: 'Get a 5-hit combo' },
                'Golem': { type: 'damage', count: 1000, description: 'Deal 1000 total damage' },
                'Aria': { type: 'wins_character', character: 'Storm', count: 5, description: 'Win 5 matches as Storm' },
                'Fang': { type: 'kos_single_match', count: 5, description: 'Get 5 KOs in a single match' },
                'Nova': { type: 'unlock_all', description: 'Unlock all other characters' }
            },
            stages: {
                'Skyline': { type: 'matches', count: 10, description: 'Play 10 matches' },
                'Dojo': { type: 'wins', count: 5, description: 'Win 5 matches' },
                'Volcano': { type: 'kos', count: 50, description: 'Get 50 total KOs' },
                'Thunderstorm': { type: 'play_character', character: 'Storm', count: 3, description: 'Play 3 matches as Storm' },
                'Frozen Lake': { type: 'unlock_character', character: 'Frost', description: 'Unlock Frost' },
                'Windmill': { type: 'damage', count: 5000, description: 'Deal 5000 total damage' }
            }
        };

        // Player stats
        this.stats = {
            totalMatches: 0,
            totalWins: 0,
            totalKOs: 0,
            totalDamageDealt: 0,
            maxCombo: 0,
            maxKOsInMatch: 0,
            characterWins: {},
            characterMatches: {}
        };

        // Current unlocks
        this.unlockedCharacters = new Set(this.defaultUnlocked.characters);
        this.unlockedStages = new Set(this.defaultUnlocked.stages);

        // Achievements
        this.achievements = {
            'first_blood': { name: 'First Blood', description: 'Get your first KO', unlocked: false },
            'combo_master': { name: 'Combo Master', description: 'Get a 10-hit combo', unlocked: false },
            'unstoppable': { name: 'Unstoppable', description: 'Win 3 matches in a row', unlocked: false },
            'perfectionist': { name: 'Perfectionist', description: 'Win without taking damage', unlocked: false },
            'jack_of_all': { name: 'Jack of All Trades', description: 'Win with every character', unlocked: false },
            'world_traveler': { name: 'World Traveler', description: 'Play on every stage', unlocked: false },
            'veteran': { name: 'Veteran', description: 'Play 100 matches', unlocked: false },
            'champion': { name: 'Champion', description: 'Win 50 matches', unlocked: false },
            'destroyer': { name: 'Destroyer', description: 'Deal 10000 total damage', unlocked: false },
            'complete': { name: 'Complete', description: 'Unlock everything', unlocked: false }
        };

        // Pending unlocks to show
        this.pendingUnlocks = [];

        // Win streak tracking
        this.currentWinStreak = 0;

        // Load saved progress
        this.load();
    }

    /**
     * Load progress from localStorage
     */
    load() {
        try {
            const saved = localStorage.getItem('arenaBrawlProgress');
            if (saved) {
                const data = JSON.parse(saved);

                if (data.stats) {
                    this.stats = { ...this.stats, ...data.stats };
                }
                if (data.unlockedCharacters) {
                    this.unlockedCharacters = new Set([
                        ...this.defaultUnlocked.characters,
                        ...data.unlockedCharacters
                    ]);
                }
                if (data.unlockedStages) {
                    this.unlockedStages = new Set([
                        ...this.defaultUnlocked.stages,
                        ...data.unlockedStages
                    ]);
                }
                if (data.achievements) {
                    for (const [key, unlocked] of Object.entries(data.achievements)) {
                        if (this.achievements[key]) {
                            this.achievements[key].unlocked = unlocked;
                        }
                    }
                }
                if (data.currentWinStreak) {
                    this.currentWinStreak = data.currentWinStreak;
                }
            }
        } catch (e) {
            console.warn('Failed to load progress:', e);
        }
    }

    /**
     * Save progress to localStorage
     */
    save() {
        try {
            const data = {
                stats: this.stats,
                unlockedCharacters: [...this.unlockedCharacters],
                unlockedStages: [...this.unlockedStages],
                achievements: Object.fromEntries(
                    Object.entries(this.achievements).map(([k, v]) => [k, v.unlocked])
                ),
                currentWinStreak: this.currentWinStreak
            };
            localStorage.setItem('arenaBrawlProgress', JSON.stringify(data));
        } catch (e) {
            console.warn('Failed to save progress:', e);
        }
    }

    /**
     * Process match result and check for unlocks
     */
    processMatchResult(result, playerData) {
        const won = result.winner_id === playerData.id;
        const playerStats = result.player_stats?.[playerData.id] || {};
        const character = playerData.character;

        // Update stats
        this.stats.totalMatches++;
        if (won) {
            this.stats.totalWins++;
            this.currentWinStreak++;
        } else {
            this.currentWinStreak = 0;
        }

        this.stats.totalKOs += playerStats.kills || 0;
        this.stats.totalDamageDealt += playerStats.damage_dealt || 0;

        if ((playerStats.kills || 0) > this.stats.maxKOsInMatch) {
            this.stats.maxKOsInMatch = playerStats.kills;
        }

        // Character-specific stats
        if (!this.stats.characterMatches[character]) {
            this.stats.characterMatches[character] = 0;
            this.stats.characterWins[character] = 0;
        }
        this.stats.characterMatches[character]++;
        if (won) {
            this.stats.characterWins[character]++;
        }

        // Check for unlocks
        this.checkUnlocks();

        // Check achievements
        this.checkAchievements(result, playerData, won);

        // Save progress
        this.save();

        return this.pendingUnlocks.splice(0, this.pendingUnlocks.length);
    }

    /**
     * Process combo for unlock checking
     */
    processCombo(comboCount) {
        if (comboCount > this.stats.maxCombo) {
            this.stats.maxCombo = comboCount;
            this.checkUnlocks();
            this.save();
        }
    }

    /**
     * Check all unlock conditions
     */
    checkUnlocks() {
        // Check character unlocks
        for (const [character, condition] of Object.entries(this.unlockConditions.characters)) {
            if (this.unlockedCharacters.has(character)) continue;

            if (this.checkCondition(condition)) {
                this.unlock('character', character);
            }
        }

        // Check stage unlocks
        for (const [stage, condition] of Object.entries(this.unlockConditions.stages)) {
            if (this.unlockedStages.has(stage)) continue;

            if (this.checkCondition(condition)) {
                this.unlock('stage', stage);
            }
        }
    }

    /**
     * Check if a condition is met
     */
    checkCondition(condition) {
        switch (condition.type) {
            case 'matches':
                return this.stats.totalMatches >= condition.count;
            case 'wins':
                return this.stats.totalWins >= condition.count;
            case 'kos':
                return this.stats.totalKOs >= condition.count;
            case 'damage':
                return this.stats.totalDamageDealt >= condition.count;
            case 'combo':
                return this.stats.maxCombo >= condition.count;
            case 'kos_single_match':
                return this.stats.maxKOsInMatch >= condition.count;
            case 'wins_character':
                return (this.stats.characterWins[condition.character] || 0) >= condition.count;
            case 'play_character':
                return (this.stats.characterMatches[condition.character] || 0) >= condition.count;
            case 'unlock_character':
                return this.unlockedCharacters.has(condition.character);
            case 'unlock_all':
                // All characters except this one
                const othersCount = this.allCharacters.length - 1;
                return this.unlockedCharacters.size >= othersCount;
            default:
                return false;
        }
    }

    /**
     * Unlock content
     */
    unlock(type, name) {
        if (type === 'character') {
            if (!this.unlockedCharacters.has(name)) {
                this.unlockedCharacters.add(name);
                this.pendingUnlocks.push({
                    type: 'character',
                    name,
                    message: `New Character Unlocked: ${name}!`
                });
            }
        } else if (type === 'stage') {
            if (!this.unlockedStages.has(name)) {
                this.unlockedStages.add(name);
                this.pendingUnlocks.push({
                    type: 'stage',
                    name,
                    message: `New Stage Unlocked: ${name}!`
                });
            }
        }
    }

    /**
     * Check achievements
     */
    checkAchievements(result, playerData, won) {
        const playerStats = result.player_stats?.[playerData.id] || {};

        // First Blood
        if (!this.achievements.first_blood.unlocked && this.stats.totalKOs >= 1) {
            this.unlockAchievement('first_blood');
        }

        // Combo Master
        if (!this.achievements.combo_master.unlocked && this.stats.maxCombo >= 10) {
            this.unlockAchievement('combo_master');
        }

        // Unstoppable
        if (!this.achievements.unstoppable.unlocked && this.currentWinStreak >= 3) {
            this.unlockAchievement('unstoppable');
        }

        // Perfectionist
        if (!this.achievements.perfectionist.unlocked && won && (playerStats.damage_taken || 0) === 0) {
            this.unlockAchievement('perfectionist');
        }

        // Jack of All Trades
        if (!this.achievements.jack_of_all.unlocked) {
            const wonWithAll = this.allCharacters.every(char =>
                (this.stats.characterWins[char] || 0) >= 1
            );
            if (wonWithAll) {
                this.unlockAchievement('jack_of_all');
            }
        }

        // Veteran
        if (!this.achievements.veteran.unlocked && this.stats.totalMatches >= 100) {
            this.unlockAchievement('veteran');
        }

        // Champion
        if (!this.achievements.champion.unlocked && this.stats.totalWins >= 50) {
            this.unlockAchievement('champion');
        }

        // Destroyer
        if (!this.achievements.destroyer.unlocked && this.stats.totalDamageDealt >= 10000) {
            this.unlockAchievement('destroyer');
        }

        // Complete
        if (!this.achievements.complete.unlocked) {
            if (this.unlockedCharacters.size >= this.allCharacters.length &&
                this.unlockedStages.size >= this.allStages.length) {
                this.unlockAchievement('complete');
            }
        }
    }

    /**
     * Unlock an achievement
     */
    unlockAchievement(key) {
        if (this.achievements[key] && !this.achievements[key].unlocked) {
            this.achievements[key].unlocked = true;
            this.pendingUnlocks.push({
                type: 'achievement',
                name: this.achievements[key].name,
                description: this.achievements[key].description,
                message: `Achievement Unlocked: ${this.achievements[key].name}!`
            });
        }
    }

    /**
     * Check if character is unlocked
     */
    isCharacterUnlocked(character) {
        return this.unlockedCharacters.has(character);
    }

    /**
     * Check if stage is unlocked
     */
    isStageUnlocked(stage) {
        return this.unlockedStages.has(stage);
    }

    /**
     * Get unlock progress for character
     */
    getCharacterProgress(character) {
        const condition = this.unlockConditions.characters[character];
        if (!condition) return { unlocked: true, progress: 1, description: 'Default character' };

        if (this.unlockedCharacters.has(character)) {
            return { unlocked: true, progress: 1, description: 'Unlocked!' };
        }

        let progress = 0;
        switch (condition.type) {
            case 'matches':
                progress = Math.min(this.stats.totalMatches / condition.count, 1);
                break;
            case 'wins':
                progress = Math.min(this.stats.totalWins / condition.count, 1);
                break;
            case 'kos':
                progress = Math.min(this.stats.totalKOs / condition.count, 1);
                break;
            case 'damage':
                progress = Math.min(this.stats.totalDamageDealt / condition.count, 1);
                break;
            case 'combo':
                progress = Math.min(this.stats.maxCombo / condition.count, 1);
                break;
            case 'wins_character':
                progress = Math.min((this.stats.characterWins[condition.character] || 0) / condition.count, 1);
                break;
            default:
                progress = 0;
        }

        return {
            unlocked: false,
            progress,
            description: condition.description
        };
    }

    /**
     * Get all characters with unlock status
     */
    getCharactersWithStatus() {
        return this.allCharacters.map(character => ({
            name: character,
            ...this.getCharacterProgress(character)
        }));
    }

    /**
     * Get all stages with unlock status
     */
    getStagesWithStatus() {
        return this.allStages.map(stage => ({
            name: stage,
            unlocked: this.isStageUnlocked(stage),
            condition: this.unlockConditions.stages[stage]?.description || 'Default stage'
        }));
    }

    /**
     * Get achievements list
     */
    getAchievements() {
        return Object.entries(this.achievements).map(([key, achievement]) => ({
            id: key,
            ...achievement
        }));
    }

    /**
     * Get player stats
     */
    getStats() {
        return { ...this.stats };
    }

    /**
     * Reset all progress
     */
    resetProgress() {
        this.stats = {
            totalMatches: 0,
            totalWins: 0,
            totalKOs: 0,
            totalDamageDealt: 0,
            maxCombo: 0,
            maxKOsInMatch: 0,
            characterWins: {},
            characterMatches: {}
        };
        this.unlockedCharacters = new Set(this.defaultUnlocked.characters);
        this.unlockedStages = new Set(this.defaultUnlocked.stages);
        Object.keys(this.achievements).forEach(key => {
            this.achievements[key].unlocked = false;
        });
        this.currentWinStreak = 0;
        this.pendingUnlocks = [];
        this.save();
    }

    /**
     * Unlock all content (cheat/debug)
     */
    unlockAll() {
        this.allCharacters.forEach(char => this.unlockedCharacters.add(char));
        this.allStages.forEach(stage => this.unlockedStages.add(stage));
        Object.keys(this.achievements).forEach(key => {
            this.achievements[key].unlocked = true;
        });
        this.save();
    }

    /**
     * Generate unlock notification HTML
     */
    static generateUnlockNotification(unlock) {
        const icons = {
            character: '👤',
            stage: '🏟️',
            achievement: '🏆'
        };

        return `
            <div class="unlock-notification ${unlock.type}">
                <div class="unlock-icon">${icons[unlock.type] || '⭐'}</div>
                <div class="unlock-content">
                    <div class="unlock-message">${unlock.message}</div>
                    ${unlock.description ? `<div class="unlock-description">${unlock.description}</div>` : ''}
                </div>
            </div>
        `;
    }
}

// Global progression instance
const progression = new ProgressionManager();

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProgressionManager;
}
