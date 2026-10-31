/**
 * Code Game: "Matrix Cyberpunk Bug Exterminator"
 * Transforms code debugging, syntax fixing, and vulnerability patching into a terminal battle.
 */
class CodeMatrixGame {
    constructor() {
        this.challenges = [];
        this.activeChallengeIndex = 0;
    }

    init() {
        this.loadChallenges();
    }

    async loadChallenges() {
        try {
            const res = await fetch("/api/code/challenges");
            const data = await res.json();
            this.challenges = data.challenges || [];
            this.renderTerminal();
        } catch (err) {
            console.error("Failed to load challenges:", err);
        }
    }

    renderTerminal() {
        const container = document.getElementById("codeTerminalContainer");
        if (!container) return;

        if (this.challenges.length === 0) {
            container.innerHTML = `<p>No active anomalies detected.</p>`;
            return;
        }

        const ch = this.challenges[this.activeChallengeIndex];
        const fixedCount = this.challenges.filter(c => c.is_fixed).length;

        container.innerHTML = `
            <div class="cyber-terminal">
                <div class="terminal-bar">
                    <div class="terminal-dots">
                        <span class="dot dot-red"></span>
                        <span class="dot dot-yellow"></span>
                        <span class="dot dot-green"></span>
                    </div>
                    <span class="terminal-title">TERMINAL MATRIX :: ${ch.filename} (${ch.language.toUpperCase()})</span>
                    <span class="terminal-progress">${fixedCount}/${this.challenges.length} BUGS EXTERMINATED</span>
                </div>

                <div class="terminal-body">
                    <div class="challenge-nav">
                        ${this.challenges.map((c, idx) => `
                            <button class="nav-btn ${idx === this.activeChallengeIndex ? 'active' : ''} ${c.is_fixed ? 'fixed-btn' : ''}"
                                    onclick="window.CodeGame.selectChallenge(${idx})">
                                ${c.is_fixed ? '✅' : '👾'} ${c.title}
                            </button>
                        `).join("")}
                    </div>

                    <div class="anomaly-intel">
                        <div class="intel-header">
                            <h4>👾 Glitch Sentinel: <span class="text-neon-pink">${ch.monster_name}</span></h4>
                            <span class="badge ${ch.is_fixed ? 'badge-success' : 'badge-danger'}">
                                ${ch.is_fixed ? 'SYSTEM PURIFIED' : 'ACTIVE GLITCH'}
                            </span>
                        </div>
                        <p class="anomaly-desc"><strong>Vulnerability:</strong> ${ch.bug_type}</p>
                    </div>

                    <div class="code-editor-mock">
                        <div class="line-numbers">
                            ${ch.current_code.split("\n").map((_, i) => `<div>${i + 1}</div>`).join("")}
                        </div>
                        <pre class="code-content"><code>${this.escapeHtml(ch.current_code)}</code></pre>
                    </div>

                    ${ch.is_fixed ? `
                        <div class="diff-viewer">
                            <h5>📜 Git Purification Diff:</h5>
                            <pre class="diff-content"><code>${this.formatDiff(ch.diff)}</code></pre>
                        </div>
                    ` : `
                        <div class="patch-selection">
                            <h5>⚡ Select Debugging Patch Spell:</h5>
                            <div class="options-grid">
                                ${ch.options.map(opt => `
                                    <button class="patch-btn" onclick="window.CodeGame.deployPatch('${ch.id}', '${opt.id}')">
                                        <span class="patch-id">[${opt.id}]</span>
                                        <span class="patch-label">${opt.label}</span>
                                    </button>
                                `).join("")}
                            </div>
                        </div>
                    `}
                </div>
            </div>
        `;
    }

    selectChallenge(index) {
        this.activeChallengeIndex = index;
        this.renderTerminal();
    }

    escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
    }

    formatDiff(diffText) {
        if (!diffText) return "";
        return diffText.split("\n").map(line => {
            if (line.startsWith("+")) return `<span class="diff-add">${this.escapeHtml(line)}</span>`;
            if (line.startsWith("-")) return `<span class="diff-sub">${this.escapeHtml(line)}</span>`;
            return this.escapeHtml(line);
        }).join("\n");
    }

    async deployPatch(challengeId, optionId) {
        try {
            const res = await fetch("/api/code/patch", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ challenge_id: challengeId, option_id: optionId })
            });
            const data = await res.json();

            if (data.success && data.is_correct) {
                if (window.Sound) window.Sound.playVictory();
                if (window.Particles) {
                    window.Particles.spawnBurst(window.innerWidth / 2, window.innerHeight / 2, "#10b981", 40);
                    window.Particles.spawnFloatingText(window.innerWidth / 2, window.innerHeight / 2 - 40, "BUG VANQUISHED! +75 XP", "#10b981", 26);
                }
                if (window.App) window.App.refreshStatus();
                this.loadChallenges();
            } else {
                if (window.Sound) window.Sound.playError();
                if (window.Particles) {
                    window.Particles.spawnBurst(window.innerWidth / 2, window.innerHeight / 2, "#ef4444", 20);
                    window.Particles.spawnFloatingText(window.innerWidth / 2, window.innerHeight / 2 - 30, "SYNTAX ANOMALY! -20 HP", "#ef4444", 22);
                }
                alert(data.message || "Incorrect patch! The system rejected the fix.");
            }
        } catch (err) {
            console.error("Patch error:", err);
        }
    }
}

window.addEventListener("DOMContentLoaded", () => {
    window.CodeGame = new CodeMatrixGame();
});
