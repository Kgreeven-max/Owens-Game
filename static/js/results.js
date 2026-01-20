/**
 * Arena Brawl - Results Screen
 * Match results display with detailed stats and animations
 */

class ResultsScreen {
    constructor() {
        this.result = null;
        this.animationPhase = 0;
        this.animationTimer = 0;

        // Animation timing
        this.phaseDurations = {
            0: 500,   // Initial delay
            1: 1000,  // Winner reveal
            2: 500,   // Stats header
            3: 2000,  // Stats reveal
            4: 0      // Ready for input
        };
    }

    /**
     * Show results screen with match data
     */
    show(result) {
        this.result = result;
        this.animationPhase = 0;
        this.animationTimer = 0;

        const container = document.getElementById('results-screen');
        if (!container) return;

        container.innerHTML = this.generateHTML();
        container.classList.add('active');

        // Start animation
        this.animate();

        // Attach event listeners
        this.attachEventListeners(container);
    }

    /**
     * Generate results HTML
     */
    generateHTML() {
        const result = this.result;
        const isTeamMode = result.mode_result?.winner_team != null;
        const isTie = !result.winner_id && !result.mode_result?.winner_team;

        return `
            <div class="results-container">
                <div class="results-header animate-in" data-phase="1">
                    ${this.generateWinnerSection(result, isTeamMode, isTie)}
                </div>

                <div class="results-stats animate-in" data-phase="2">
                    <h2>Match Statistics</h2>
                    <div class="stats-grid">
                        ${this.generateStatsCards(result)}
                    </div>
                </div>

                <div class="results-scoreboard animate-in" data-phase="3">
                    <h2>Scoreboard</h2>
                    <table class="scoreboard-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Player</th>
                                <th>KOs</th>
                                <th>Falls</th>
                                <th>Damage</th>
                                <th>Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${this.generateScoreboardRows(result)}
                        </tbody>
                    </table>
                </div>

                <div class="results-actions animate-in" data-phase="4">
                    <button class="menu-btn" id="btn-results-rematch">Rematch</button>
                    <button class="menu-btn" id="btn-results-character">Change Character</button>
                    <button class="menu-btn" id="btn-results-menu">Main Menu</button>
                </div>
            </div>
        `;
    }

    /**
     * Generate winner section
     */
    generateWinnerSection(result, isTeamMode, isTie) {
        if (isTie) {
            return `
                <div class="winner-display tie">
                    <div class="tie-icon">⚔️</div>
                    <h1>DRAW!</h1>
                    <p>No winner this time</p>
                </div>
            `;
        }

        if (isTeamMode) {
            const teamColor = result.mode_result.winner_team;
            const teamColors = {
                red: '#ff4444',
                blue: '#4444ff',
                green: '#44ff44',
                yellow: '#ffff44'
            };

            return `
                <div class="winner-display team" style="--team-color: ${teamColors[teamColor] || '#fff'}">
                    <div class="team-badge" style="background: ${teamColors[teamColor]}">${teamColor.toUpperCase()}</div>
                    <h1>TEAM ${teamColor.toUpperCase()} WINS!</h1>
                </div>
            `;
        }

        // Individual winner
        return `
            <div class="winner-display">
                <div class="winner-crown">👑</div>
                <h1>VICTORY!</h1>
                <div class="winner-name">${this.escapeHtml(result.winner_name || 'Unknown')}</div>
                <div class="winner-character">${result.winner_character || ''}</div>
            </div>
        `;
    }

    /**
     * Generate stat cards for each player
     */
    generateStatsCards(result) {
        const stats = result.player_stats || {};
        const players = result.players || [];

        return players.map(player => {
            const playerStats = stats[player.id] || {};

            // Calculate performance metrics
            const kdr = playerStats.deaths > 0
                ? (playerStats.kills / playerStats.deaths).toFixed(2)
                : playerStats.kills.toFixed(2);

            const damageRatio = playerStats.damage_taken > 0
                ? (playerStats.damage_dealt / playerStats.damage_taken).toFixed(2)
                : playerStats.damage_dealt.toFixed(2);

            const isWinner = player.id === result.winner_id;

            return `
                <div class="stat-card ${isWinner ? 'winner' : ''}">
                    <div class="stat-card-header">
                        <div class="player-avatar" style="background: ${this.getCharacterColor(player.character)}">
                            ${isWinner ? '<span class="crown">👑</span>' : ''}
                        </div>
                        <div class="player-info">
                            <div class="player-name">${this.escapeHtml(player.name)}</div>
                            <div class="player-character">${player.character}</div>
                        </div>
                    </div>
                    <div class="stat-card-body">
                        <div class="stat-row">
                            <span class="stat-label">Kills</span>
                            <span class="stat-value">${playerStats.kills || 0}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Deaths</span>
                            <span class="stat-value">${playerStats.deaths || 0}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">K/D Ratio</span>
                            <span class="stat-value ${parseFloat(kdr) >= 1 ? 'positive' : 'negative'}">${kdr}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Damage Dealt</span>
                            <span class="stat-value">${playerStats.damage_dealt || 0}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Damage Taken</span>
                            <span class="stat-value">${playerStats.damage_taken || 0}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Damage Ratio</span>
                            <span class="stat-value ${parseFloat(damageRatio) >= 1 ? 'positive' : 'negative'}">${damageRatio}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">Powerups</span>
                            <span class="stat-value">${playerStats.powerups_collected || 0}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Generate scoreboard rows
     */
    generateScoreboardRows(result) {
        const scoreboard = result.mode_result?.scoreboard || [];
        const stats = result.player_stats || {};
        const players = result.players || [];

        // If no scoreboard, create from players
        let rankings = scoreboard.length > 0 ? scoreboard : players.map(p => ({
            player_id: p.id,
            name: p.name,
            ko_count: stats[p.id]?.kills || 0,
            fall_count: stats[p.id]?.deaths || 0,
            damage_dealt: stats[p.id]?.damage_dealt || 0,
            score: (stats[p.id]?.kills || 0) - (stats[p.id]?.deaths || 0)
        }));

        // Sort by score
        rankings.sort((a, b) => b.score - a.score);

        return rankings.map((entry, index) => {
            const player = players.find(p => p.id === entry.player_id) || { name: 'Unknown', character: '' };
            const playerStats = stats[entry.player_id] || {};
            const isWinner = entry.player_id === result.winner_id;

            const rankDisplay = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `${index + 1}`;

            return `
                <tr class="${isWinner ? 'winner' : ''} animate-row" style="animation-delay: ${index * 0.1}s">
                    <td class="rank">${rankDisplay}</td>
                    <td class="player">
                        <span class="player-color" style="background: ${this.getCharacterColor(player.character)}"></span>
                        ${this.escapeHtml(player.name)}
                    </td>
                    <td class="kos">${entry.ko_count || playerStats.kills || 0}</td>
                    <td class="falls">${entry.fall_count || playerStats.deaths || 0}</td>
                    <td class="damage">${entry.damage_dealt || playerStats.damage_dealt || 0}</td>
                    <td class="score">${entry.score || 0}</td>
                </tr>
            `;
        }).join('');
    }

    /**
     * Animate results reveal
     */
    animate() {
        const animatePhase = () => {
            const elements = document.querySelectorAll(`[data-phase="${this.animationPhase}"]`);
            elements.forEach(el => el.classList.add('visible'));

            this.animationPhase++;

            if (this.animationPhase < Object.keys(this.phaseDurations).length) {
                const delay = this.phaseDurations[this.animationPhase - 1] || 500;
                setTimeout(animatePhase, delay);
            }
        };

        setTimeout(animatePhase, this.phaseDurations[0]);
    }

    /**
     * Attach event listeners
     */
    attachEventListeners(container) {
        // Rematch
        container.querySelector('#btn-results-rematch')?.addEventListener('click', () => {
            if (typeof network !== 'undefined') {
                network.requestRematch();
            }
            this.hide();
            if (typeof ui !== 'undefined') {
                ui.showScreen('lobby');
            }
        });

        // Change character
        container.querySelector('#btn-results-character')?.addEventListener('click', () => {
            this.hide();
            if (typeof ui !== 'undefined') {
                ui.showScreen('lobby');
            }
        });

        // Main menu
        container.querySelector('#btn-results-menu')?.addEventListener('click', () => {
            if (typeof network !== 'undefined') {
                network.leaveRoom();
            }
            this.hide();
            if (typeof ui !== 'undefined') {
                ui.showScreen('menu');
            }
        });

        // Keyboard shortcuts
        this.keyHandler = (e) => {
            if (e.code === 'Enter' || e.code === 'Space') {
                // Default to rematch
                container.querySelector('#btn-results-rematch')?.click();
            } else if (e.code === 'Escape') {
                container.querySelector('#btn-results-menu')?.click();
            }
        };
        document.addEventListener('keydown', this.keyHandler);
    }

    /**
     * Hide results screen
     */
    hide() {
        const container = document.getElementById('results-screen');
        if (container) {
            container.classList.remove('active');
        }

        if (this.keyHandler) {
            document.removeEventListener('keydown', this.keyHandler);
            this.keyHandler = null;
        }
    }

    /**
     * Get character color
     */
    getCharacterColor(character) {
        const colors = {
            'Blaze': '#ff4400',
            'Tank': '#4169E1',
            'Shadow': '#8A2BE2',
            'Storm': '#FFD700',
            'Frost': '#88ffff',
            'Titan': '#8b4513',
            'Whisper': '#ff00ff',
            'Volt': '#ffff00',
            'Golem': '#666666',
            'Aria': '#aaffaa',
            'Fang': '#884400',
            'Nova': '#ff8800'
        };
        return colors[character] || '#666666';
    }

    /**
     * Escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }

    /**
     * Generate CSS for results screen
     */
    static getStyles() {
        return `
            .results-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
                max-width: 1200px;
                margin: 0 auto;
            }

            .animate-in {
                opacity: 0;
                transform: translateY(20px);
                transition: opacity 0.5s, transform 0.5s;
            }

            .animate-in.visible {
                opacity: 1;
                transform: translateY(0);
            }

            .winner-display {
                text-align: center;
                margin-bottom: 30px;
            }

            .winner-display h1 {
                font-size: 3em;
                margin: 10px 0;
                text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
            }

            .winner-crown {
                font-size: 4em;
                animation: bounce 1s ease infinite;
            }

            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }

            .winner-name {
                font-size: 2em;
                color: #ffd700;
            }

            .winner-display.tie h1 {
                color: #888;
                text-shadow: none;
            }

            .winner-display.team h1 {
                color: var(--team-color, white);
            }

            .team-badge {
                display: inline-block;
                padding: 10px 30px;
                border-radius: 10px;
                font-size: 1.5em;
                font-weight: bold;
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                width: 100%;
                margin: 20px 0;
            }

            .stat-card {
                background: rgba(40, 40, 60, 0.9);
                border-radius: 10px;
                padding: 15px;
                border: 2px solid #444;
            }

            .stat-card.winner {
                border-color: #ffd700;
                box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
            }

            .stat-card-header {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 15px;
                padding-bottom: 15px;
                border-bottom: 1px solid #444;
            }

            .player-avatar {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                position: relative;
            }

            .player-avatar .crown {
                position: absolute;
                top: -15px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 1.2em;
            }

            .player-info .player-name {
                font-size: 1.2em;
                font-weight: bold;
            }

            .player-info .player-character {
                color: #888;
                font-size: 0.9em;
            }

            .stat-row {
                display: flex;
                justify-content: space-between;
                padding: 5px 0;
            }

            .stat-label {
                color: #aaa;
            }

            .stat-value {
                font-weight: bold;
            }

            .stat-value.positive {
                color: #4f4;
            }

            .stat-value.negative {
                color: #f44;
            }

            .scoreboard-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }

            .scoreboard-table th,
            .scoreboard-table td {
                padding: 12px;
                text-align: center;
                border-bottom: 1px solid #444;
            }

            .scoreboard-table th {
                background: rgba(60, 60, 80, 0.8);
                color: #ddd;
            }

            .scoreboard-table tr.winner {
                background: rgba(255, 215, 0, 0.1);
            }

            .scoreboard-table .rank {
                font-size: 1.3em;
            }

            .scoreboard-table .player {
                text-align: left;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .player-color {
                width: 12px;
                height: 12px;
                border-radius: 50%;
            }

            .animate-row {
                animation: slideIn 0.3s ease forwards;
                opacity: 0;
            }

            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateX(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }

            .results-actions {
                display: flex;
                gap: 15px;
                margin-top: 30px;
            }
        `;
    }
}

// Global results instance
const resultsScreen = new ResultsScreen();

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ResultsScreen;
}
