/**
 * Expense Game: "Bounty Rogue: Receipt Slayer"
 * Transforms receipt tracking, category budgeting & vampire subscription hunting into an RPG bounty quest.
 */
class ExpenseBountyGame {
    constructor() {
        this.expenses = [];
        this.analytics = {};
        this.categories = [];
        this.selectedExpense = null;
    }

    init() {
        this.loadExpenses();
    }

    async loadExpenses(filter = null) {
        try {
            const url = filter ? `/api/expense/list?filter=${filter}` : "/api/expense/list";
            const res = await fetch(url);
            const data = await res.json();
            this.expenses = data.expenses || [];
            this.analytics = data.analytics || {};
            this.categories = this.analytics.categories || [];
            this.renderHUD();
            this.renderBounties();
            this.renderVampires();
        } catch (err) {
            console.error("Failed to load expenses:", err);
        }
    }

    renderHUD() {
        const burnEl = document.getElementById("expenseBurnAmount");
        if (burnEl) {
            const sum = this.analytics.summary || {};
            burnEl.innerText = `$${(sum.total_amount || 0).toFixed(2)}`;
        }

        const savedEl = document.getElementById("expenseVampireSaved");
        if (savedEl) {
            const sum = this.analytics.summary || {};
            savedEl.innerText = `$${(sum.saved_monthly || 0).toFixed(2)}/mo Slayed`;
        }

        const countEl = document.getElementById("expenseBountyCount");
        if (countEl) {
            const uncategorized = this.expenses.filter(e => !e.is_categorized).length;
            countEl.innerText = `${uncategorized} Unclassified`;
        }
    }

    renderBounties() {
        const container = document.getElementById("bountyBoardContainer");
        if (!container) return;

        const uncategorized = this.expenses.filter(e => !e.is_categorized && !e.is_cancelled);

        if (uncategorized.length === 0) {
            container.innerHTML = `
                <div class="empty-tavern">
                    <div style="font-size: 3rem;">⚔️</div>
                    <h3>All Bounties Claimed & Categorized!</h3>
                    <p>Every transaction in your ledger has been audited and classified.</p>
                    <button class="btn btn-primary" onclick="window.ExpenseGame.resetExpenses()">Reset Bounty Ledger</button>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="bounty-cards-grid">
                ${uncategorized.map(exp => `
                    <div class="bounty-card ${exp.is_vampire ? 'vampire-border' : ''}">
                        <div class="bounty-header">
                            <span class="bounty-merchant">${exp.merchant}</span>
                            <span class="bounty-amount">$${exp.amount.toFixed(2)}</span>
                        </div>
                        <div class="bounty-monster">
                            <span class="monster-name">👾 Monster: ${exp.monster_name}</span>
                            ${exp.is_recurring ? '<span class="badge badge-recurring">🔄 Recurring Billing</span>' : ''}
                        </div>
                        <p class="bounty-note">${exp.note || 'Unreviewed line item'}</p>
                        
                        <div class="bounty-actions">
                            <select class="category-select" id="cat-sel-${exp.id}">
                                <option value="">Select Kingdom Category...</option>
                                ${this.categories.map(c => `
                                    <option value="${c}">${c}</option>
                                `).join("")}
                            </select>
                            <button class="btn btn-primary btn-sm" onclick="window.ExpenseGame.categorize('${exp.id}')">
                                🗡️ Claim Bounty
                            </button>
                        </div>
                    </div>
                `).join("")}
            </div>
        `;
    }

    renderVampires() {
        const container = document.getElementById("vampireSectionContainer");
        if (!container) return;

        const vampires = this.expenses.filter(e => e.is_vampire);

        container.innerHTML = `
            <div class="vampire-chamber">
                <div class="vampire-header">
                    <h4>🧛 Vampire Subscription Lair</h4>
                    <p>Forgotten recurring SaaS and memberships silently draining monthly gold!</p>
                </div>
                <div class="vampire-grid">
                    ${vampires.map(v => `
                        <div class="vampire-card ${v.is_cancelled ? 'slayed-vampire' : ''}">
                            <div class="vampire-top">
                                <span class="vampire-name">${v.merchant}</span>
                                <span class="vampire-cost">$${v.amount.toFixed(2)} / month</span>
                            </div>
                            <div class="vampire-desc">${v.note}</div>
                            <div class="vampire-foot">
                                ${v.is_cancelled ? `
                                    <span class="badge badge-slayed">☠️ SLAYED! (Saved $${(v.amount * 12).toFixed(2)}/yr)</span>
                                ` : `
                                    <button class="btn btn-danger btn-stake" onclick="window.ExpenseGame.slayVampire('${v.id}')">
                                        🗡️ Drive Silver Stake (Cancel Sub)
                                    </button>
                                `}
                            </div>
                        </div>
                    `).join("")}
                </div>
            </div>
        `;
    }

    async categorize(expenseId) {
        const select = document.getElementById(`cat-sel-${expenseId}`);
        const category = select ? select.value : "";
        if (!category) {
            alert("Please choose a kingdom budget category first!");
            return;
        }

        try {
            const res = await fetch("/api/expense/categorize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ expense_id: expenseId, category: category })
            });
            const data = await res.json();

            if (data.success) {
                if (window.Sound) window.Sound.playCoin();
                if (window.Particles) {
                    window.Particles.spawnBurst(window.innerWidth / 2, window.innerHeight / 2, "#10b981", 20);
                    window.Particles.spawnFloatingText(window.innerWidth / 2, window.innerHeight / 2 - 25, `CLASSIFIED! +25 XP`, "#10b981", 22);
                }
                if (window.App) window.App.refreshStatus();
                this.loadExpenses();
            }
        } catch (err) {
            console.error("Categorize error:", err);
        }
    }

    async slayVampire(expenseId) {
        try {
            const res = await fetch("/api/expense/slay-vampire", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ expense_id: expenseId })
            });
            const data = await res.json();

            if (data.success) {
                if (window.Sound) window.Sound.playExplosion();
                if (window.Particles) {
                    window.Particles.spawnBurst(window.innerWidth / 2, window.innerHeight / 2, "#fbbf24", 40);
                    window.Particles.spawnFloatingText(window.innerWidth / 2, window.innerHeight / 2 - 40, `VAMPIRE SLAYED! SAVED $${data.yearly_saved}/YR!`, "#fbbf24", 26);
                }
                if (window.App) window.App.refreshStatus();
                this.loadExpenses();
            }
        } catch (err) {
            console.error("Slay vampire error:", err);
        }
    }

    async exportLedger() {
        try {
            const res = await fetch("/api/expense/export");
            const data = await res.json();
            if (window.Sound) window.Sound.playVictory();
            alert(`🎉 Expense Ledger successfully exported!\n\n• CSV: ${data.csv_path}\n• Excel: ${data.xlsx_path}\nTotal items: ${data.row_count}`);
        } catch (err) {
            console.error("Export error:", err);
        }
    }

    async resetExpenses() {
        try {
            await fetch("/api/expense/reset", { method: "POST" });
            if (window.Sound) window.Sound.playPowerup();
            await this.loadExpenses();
        } catch (err) {
            console.error(err);
        }
    }
}

window.addEventListener("DOMContentLoaded", () => {
    window.ExpenseGame = new ExpenseBountyGame();
});
