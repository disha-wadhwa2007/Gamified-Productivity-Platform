/**
 * ChoreQuest Master Controller
 * Connects WebSocket telemetry, tab navigation, Time Machine rollbacks, and HUD updates.
 */
class ChoreQuestApp {
    constructor() {
        this.currentTab = "dashboard";
        this.profile = {};
        this.metrics = {};
        this.dryRun = false;
        this.ws = null;
    }

    init() {
        this.setupNavigation();
        this.setupWebSocket();
        this.refreshStatus();
        this.loadTransactions();

        // Polling fallback if WebSocket drops
        setInterval(() => this.refreshStatus(), 10000);
    }

    setupNavigation() {
        document.querySelectorAll(".nav-item").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const tab = btn.dataset.tab;
                if (tab) this.switchTab(tab);
            });
        });
    }

    switchTab(tabId) {
        this.currentTab = tabId;
        document.querySelectorAll(".nav-item").forEach(b => b.classList.toggle("active", b.dataset.tab === tabId));
        document.querySelectorAll(".tab-pane").forEach(p => p.classList.toggle("active", p.id === `tab-${tabId}`));

        // Trigger game starts/pauses
        if (tabId === "email" && window.EmailGame) {
            window.EmailGame.start();
            window.EmailGame.loadEmails();
        } else if (window.EmailGame) {
            window.EmailGame.stop();
        }

        if (tabId === "files" && window.FileGame) {
            window.FileGame.loadFiles();
        }
        if (tabId === "expenses" && window.ExpenseGame) {
            window.ExpenseGame.loadExpenses();
        }
        if (tabId === "code" && window.CodeGame) {
            window.CodeGame.loadChallenges();
        }
        if (tabId === "story" && window.StoryMode) {
            window.StoryMode.loadCampaign();
        }
        if (tabId === "audit") {
            this.loadTransactions();
        }
    }

    setupWebSocket() {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log("⚡ Telemetry link established to ChoreQuest Engine");
            const wsBadge = document.getElementById("wsStatusBadge");
            if (wsBadge) {
                wsBadge.className = "status-indicator live";
                wsBadge.title = "Real-Time Telemetry Connected";
            }
        };

        this.ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                this.handleTelemetryEvent(msg);
            } catch (e) {
                console.error(e);
            }
        };

        this.ws.onclose = () => {
            const wsBadge = document.getElementById("wsStatusBadge");
            if (wsBadge) {
                wsBadge.className = "status-indicator offline";
            }
            setTimeout(() => this.setupWebSocket(), 3000);
        };
    }

    handleTelemetryEvent(msg) {
        const { event, data } = msg;

        // Visual floating text or sounds for server-side events
        if (data && data.gamification) {
            const g = data.gamification;
            if (g.leveled_up) {
                if (window.Sound) window.Sound.playVictory();
                if (window.Particles) {
                    window.Particles.spawnConfetti();
                    window.Particles.spawnFloatingText(window.innerWidth / 2, 200, `LEVEL UP! LEVEL ${g.new_level}!`, "#fbbf24", 32);
                }
            }
        }

        this.refreshStatus();
    }

    async refreshStatus() {
        try {
            const res = await fetch("/api/status");
            const data = await res.json();
            this.profile = data.profile || {};
            this.metrics = data.metrics || {};
            this.dryRun = data.dry_run;
            this.updatePlayerHUD();
            this.updateMetricsDashboard();
            this.updateDryRunIndicator();
        } catch (err) {
            console.error("Status refresh error:", err);
        }
    }

    updatePlayerHUD() {
        const nameEl = document.getElementById("playerName");
        if (nameEl) nameEl.innerText = this.profile.name || "Hero";

        const lvlEl = document.getElementById("playerLevel");
        if (lvlEl) lvlEl.innerText = `LVL ${this.profile.level || 1}`;

        const xpTextEl = document.getElementById("playerXpText");
        if (xpTextEl) xpTextEl.innerText = `${this.profile.xp || 0} / ${this.profile.xp_for_next || 100} XP`;

        const xpBarEl = document.getElementById("playerXpBar");
        if (xpBarEl) xpBarEl.style.width = `${this.profile.xp_progress_pct || 0}%`;

        const goldEl = document.getElementById("playerGold");
        if (goldEl) goldEl.innerText = `${this.profile.gold || 0} 🪙`;

        const comboEl = document.getElementById("playerCombo");
        if (comboEl) {
            const streak = this.profile.combo_streak || 0;
            comboEl.innerText = streak > 1 ? `⚡ ${streak}x STREAK` : "";
            comboEl.style.display = streak > 1 ? "inline-block" : "none";
        }
    }

    updateMetricsDashboard() {
        const m = this.metrics;
        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.innerText = val;
        };

        setVal("metricTotalActions", m.total_actions || 0);
        setVal("metricFilesOrganized", m.files_organized || 0);
        setVal("metricBytesSaved", this.formatBytes(m.bytes_saved || 0));
        setVal("metricEmailsCleaned", m.emails_cleaned || 0);
        setVal("metricExpensesReviewed", m.expenses_reviewed || 0);
        setVal("metricMoneySaved", `$${(m.money_saved || 0).toFixed(2)}/mo`);
        setVal("metricBugsFixed", m.bugs_fixed || 0);
    }

    formatBytes(bytes) {
        if (!bytes || bytes === 0) return "0 MB";
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
        return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
    }

    updateDryRunIndicator() {
        const toggle = document.getElementById("dryRunToggle");
        if (toggle) toggle.checked = this.dryRun;
        const badge = document.getElementById("dryRunModeBadge");
        if (badge) {
            badge.className = this.dryRun ? "badge badge-simulation" : "badge badge-real";
            badge.innerText = this.dryRun ? "🛡️ DRY RUN (Simulation)" : "⚡ LIVE REAL-WORLD";
        }
    }

    async toggleDryRun() {
        const toggle = document.getElementById("dryRunToggle");
        const nextVal = toggle ? toggle.checked : !this.dryRun;
        try {
            const res = await fetch("/api/settings/dry-run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ dry_run: nextVal })
            });
            const data = await res.json();
            this.dryRun = data.dry_run;
            this.updateDryRunIndicator();
            if (window.Sound) window.Sound.playShield();
        } catch (err) {
            console.error("Toggle dry run error:", err);
        }
    }

    async loadTransactions() {
        try {
            const res = await fetch("/api/transactions");
            const data = await res.json();
            const txs = data.transactions || [];
            const container = document.getElementById("transactionLogList");
            if (!container) return;

            if (txs.length === 0) {
                container.innerHTML = `<div class="empty-log">No transactions logged yet. Complete tasks to record real-world operations!</div>`;
                return;
            }

            container.innerHTML = txs.map(tx => `
                <div class="transaction-row ${tx.status}">
                    <div class="tx-id-col">
                        <span class="tx-id">${tx.id}</span>
                        <span class="tx-time">${new Date(tx.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div class="tx-details-col">
                        <div class="tx-details">${tx.details}</div>
                        <div class="tx-meta">
                            <span class="badge badge-subtle">${tx.chore_type.replace('_', ' ').toUpperCase()}</span>
                            ${tx.is_dry_run ? '<span class="badge badge-simulation">SIMULATION</span>' : '<span class="badge badge-real">REAL DISK/DB</span>'}
                        </div>
                    </div>
                    <div class="tx-action-col">
                        ${tx.status === "completed" ? `
                            <button class="btn btn-warning btn-sm" onclick="window.App.rollbackTransaction('${tx.id}')">
                                ⏪ 1-Click Rollback
                            </button>
                        ` : `
                            <span class="badge badge-rolledback">ROLLED BACK</span>
                        `}
                    </div>
                </div>
            `).join("");
        } catch (err) {
            console.error("Load transactions error:", err);
        }
    }

    async rollbackTransaction(txId) {
        if (!confirm(`Are you sure you want to rollback transaction ${txId}? This will reverse the real-world operation on disk or database.`)) return;

        try {
            const res = await fetch("/api/transactions/rollback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tx_id: txId })
            });
            const data = await res.json();

            if (data.success) {
                if (window.Sound) window.Sound.playPowerup();
                if (window.Particles) {
                    window.Particles.spawnBurst(window.innerWidth / 2, window.innerHeight / 2, "#fbbf24", 30);
                    window.Particles.spawnFloatingText(window.innerWidth / 2, window.innerHeight / 2, "TIME MACHINE RESTORED!", "#fbbf24", 24);
                }
                alert(`Success: ${data.message}`);
                this.loadTransactions();
                this.refreshStatus();
            } else {
                alert(`Rollback failed: ${data.error}`);
            }
        } catch (err) {
            console.error("Rollback error:", err);
        }
    }

    renderSkillsTab() {
        const container = document.getElementById("skillTreeGrid");
        if (!container || !this.profile.skills) return;

        container.innerHTML = this.profile.skills.map(s => `
            <div class="skill-card ${s.unlocked ? 'skill-unlocked' : ''}">
                <div class="skill-icon">${s.icon}</div>
                <div class="skill-body">
                    <div class="skill-title">${s.name}</div>
                    <div class="skill-desc">${s.description}</div>
                    <div class="skill-action">
                        ${s.unlocked ? `
                            <span class="badge badge-success">UNLOCKED</span>
                        ` : `
                            <button class="btn btn-primary btn-sm" onclick="window.App.unlockSkill('${s.id}')">
                                Unlock for ${s.cost} 🪙
                            </button>
                        `}
                    </div>
                </div>
            </div>
        `).join("");
    }

    async unlockSkill(skillId) {
        try {
            const res = await fetch("/api/gamification/unlock-skill", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ skill_id: skillId })
            });
            const data = await res.json();
            if (data.success) {
                if (window.Sound) window.Sound.playPowerup();
                if (window.Particles) window.Particles.spawnConfetti();
                this.refreshStatus();
            } else {
                alert(data.error);
            }
        } catch (err) {
            console.error("Unlock skill error:", err);
        }
    }

    toggleSound() {
        if (window.Sound) {
            const isMuted = window.Sound.toggleMute();
            const btn = document.getElementById("soundToggleBtn");
            if (btn) btn.innerText = isMuted ? "🔇 Unmute Sound" : "🔊 Audio On";
        }
    }
}

window.addEventListener("DOMContentLoaded", () => {
    window.App = new ChoreQuestApp();
    window.App.init();
});
