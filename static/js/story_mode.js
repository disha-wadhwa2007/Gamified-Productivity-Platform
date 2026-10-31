/**
 * Story Mode: "The Chronicles of the Pure Realm"
 * Interactive RPG campaign guiding the player through all 4 chore disciplines.
 */
class StoryCampaignEngine {
    constructor() {
        this.campaign = [];
        this.activeChapter = null;
    }

    init() {
        this.loadCampaign();
    }

    async loadCampaign() {
        try {
            const res = await fetch("/api/story/campaign");
            const data = await res.json();
            this.campaign = data.campaign || [];
            this.renderCampaignList();
        } catch (err) {
            console.error("Failed to load story campaign:", err);
        }
    }

    renderCampaignList() {
        const container = document.getElementById("storyCampaignContainer");
        if (!container) return;

        container.innerHTML = `
            <div class="story-chronicles-grid">
                ${this.campaign.map(chap => `
                    <div class="story-chapter-card ${chap.completed ? 'chapter-cleared' : ''}">
                        <div class="chapter-badge">Chapter ${chap.number}</div>
                        <div class="chapter-hero">
                            <span class="character-avatar">${chap.avatar}</span>
                            <div class="character-info">
                                <h5>${chap.character}</h5>
                                <h3>${chap.title}</h3>
                            </div>
                        </div>
                        <div class="dialogue-box">
                            <p>"${chap.intro_dialogue}"</p>
                        </div>
                        <div class="objective-box">
                            <strong>🎯 Mission:</strong> ${chap.objective}
                        </div>
                        <div class="chapter-footer">
                            <div class="rewards">
                                <span>⭐ +${chap.reward_xp} XP</span>
                                <span>🪙 +${chap.reward_gold} Gold</span>
                            </div>
                            ${chap.completed ? `
                                <div class="badge badge-success">🏆 CHAPTER CLEARED (${chap.stars} ⭐)</div>
                            ` : `
                                <button class="btn btn-primary" onclick="window.StoryMode.embark('${chap.id}', '${chap.discipline}')">
                                    ⚔️ Embark on Quest
                                </button>
                            `}
                        </div>
                    </div>
                `).join("")}
            </div>
        `;
    }

    embark(chapterId, discipline) {
        if (window.Sound) window.Sound.playPowerup();
        // Switch to the relevant mini-game tab
        const tabMap = {
            "email_cleanup": "email",
            "file_organization": "files",
            "expense_tracking": "expenses",
            "code_debugging": "code"
        };

        const targetTab = tabMap[discipline] || "email";
        if (window.App) {
            window.App.switchTab(targetTab);
        }

        // Show a quest briefing toast
        if (window.Particles) {
            window.Particles.spawnFloatingText(window.innerWidth / 2, 100, `QUEST ACTIVE: ${discipline.toUpperCase()}`, "#38bdf8", 24);
        }
    }
}

window.addEventListener("DOMContentLoaded", () => {
    window.StoryMode = new StoryCampaignEngine();
});
