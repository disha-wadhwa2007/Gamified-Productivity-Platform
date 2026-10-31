/**
 * File Game: "Dungeon Cargo Sorter & Loot Sorter"
 * Transforms messy desktop & downloads clutter into an arcade sorting puzzle.
 */
class FileSorterGame {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.files = [];
        this.duplicates = [];
        this.scanData = {};
        this.vaults = [
            { id: "Documents", name: "Scroll Vault", icon: "📄", color: "#38bdf8", key: "1" },
            { id: "Images", name: "Prism Gallery", icon: "🖼️", color: "#ec4899", key: "2" },
            { id: "Media", name: "Echo Cavern", icon: "🎬", color: "#a855f7", key: "3" },
            { id: "Installers", name: "Titan Foundry", icon: "⚙️", color: "#f59e0b", key: "4" },
            { id: "Archives", name: "Mummy Crypt", icon: "📦", color: "#eab308", key: "5" },
            { id: "Code", name: "Logic Shrine", icon: "💻", color: "#10b981", key: "6" }
        ];
        this.activeFileIndex = 0;
    }

    init() {
        this.canvas = document.getElementById("fileCanvas");
        this.bindEvents();
        this.loadFiles();
    }

    bindEvents() {
        window.addEventListener("keydown", (e) => {
            if (["Digit1", "Digit2", "Digit3", "Digit4", "Digit5", "Digit6"].includes(e.code)) {
                const idx = parseInt(e.code.replace("Digit", "")) - 1;
                if (this.vaults[idx]) {
                    this.sortActiveFile(this.vaults[idx].id);
                }
            }
        });
    }

    async loadFiles() {
        try {
            const res = await fetch("/api/files/scan");
            this.scanData = await res.json();
            this.files = this.scanData.files || [];
            this.duplicates = this.scanData.duplicates || [];
            this.renderHUD();
            this.renderConveyor();
            this.renderDuplicatesSection();
        } catch (err) {
            console.error("Failed to load files:", err);
        }
    }

    renderHUD() {
        const totalEl = document.getElementById("fileTotalCount");
        if (totalEl) totalEl.innerText = `${this.files.length} Loose Files`;
        const sizeEl = document.getElementById("fileTotalSize");
        if (sizeEl) sizeEl.innerText = this.scanData.total_size_formatted || "0 B";
        const dupEl = document.getElementById("fileDupCount");
        if (dupEl) dupEl.innerText = `${this.duplicates.length} Duplicates Found`;
    }

    renderConveyor() {
        const container = document.getElementById("fileConveyor");
        if (!container) return;

        if (this.files.length === 0) {
            container.innerHTML = `
                <div class="empty-warehouse">
                    <div style="font-size: 3rem;">🏰</div>
                    <h3>Cargo Bay Fully Organized!</h3>
                    <p>Every loose file has been safely moved into its structured folder.</p>
                    <button class="btn btn-primary" onclick="window.FileGame.resetSampleFiles()">Spawn Cluttered Files Wave</button>
                </div>
            `;
            return;
        }

        const activeFile = this.files[0];
        const nextFiles = this.files.slice(1, 4);

        container.innerHTML = `
            <div class="conveyor-stage">
                <div class="active-cargo-card ${activeFile.is_duplicate ? 'duplicate-glow' : ''}">
                    <div class="cargo-icon" style="font-size: 3.5rem;">${activeFile.icon}</div>
                    <div class="cargo-details">
                        <div class="cargo-title">${activeFile.name}</div>
                        <div class="cargo-meta">
                            <span class="badge badge-category">${activeFile.category}</span>
                            <span class="badge badge-size">${activeFile.size_formatted}</span>
                            ${activeFile.is_duplicate ? '<span class="badge badge-warning">⚠️ Exact Duplicate Detected!</span>' : ''}
                        </div>
                    </div>
                </div>

                <div class="vault-grid">
                    ${this.vaults.map((v, i) => `
                        <button class="vault-btn ${activeFile.category === v.id ? 'recommended-vault' : ''}" 
                                onclick="window.FileGame.sortActiveFile('${v.id}')">
                            <span class="vault-key">[${v.key}]</span>
                            <span class="vault-icon">${v.icon}</span>
                            <span class="vault-name">${v.name}</span>
                        </button>
                    `).join("")}
                </div>

                <div class="upcoming-queue">
                    <span class="queue-label">Next on Belt:</span>
                    ${nextFiles.map(f => `
                        <div class="queue-item">
                            <span>${f.icon}</span>
                            <span class="queue-filename">${f.name}</span>
                        </div>
                    `).join("")}
                </div>
            </div>
        `;
    }

    renderDuplicatesSection() {
        const container = document.getElementById("duplicateCrusherSection");
        if (!container) return;

        if (this.duplicates.length === 0) {
            container.innerHTML = `
                <div class="duplicate-clean">
                    <span>✨ Zero duplicate files detected on disk. Clean realm maintained!</span>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="duplicate-alert-banner">
                <div class="banner-text">
                    <h4>⚠️ Duplicate File Monsters Spotted (${this.duplicates.length})</h4>
                    <p>Identical content taking up duplicate disk space. Vanquish them safely to quarantine!</p>
                </div>
                <div class="duplicate-list">
                    ${this.duplicates.map(d => `
                        <div class="duplicate-row">
                            <div class="dup-info">
                                <span class="dup-name">${d.duplicate}</span>
                                <span class="dup-sub">Twin copy of: <em>${d.original}</em> (${(d.size / 1024 / 1024).toFixed(1)} MB)</span>
                            </div>
                            <button class="btn btn-danger btn-sm" onclick="window.FileGame.quarantineDuplicate('${d.duplicate}')">
                                💥 Crush Duplicate
                            </button>
                        </div>
                    `).join("")}
                </div>
            </div>
        `;
    }

    async sortActiveFile(targetCategory) {
        if (this.files.length === 0) return;
        const file = this.files[0];

        try {
            const res = await fetch("/api/files/organize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ filename: file.name, category: targetCategory })
            });
            const data = await res.json();

            if (data.success) {
                if (window.Sound) window.Sound.playCoin();
                if (window.Particles) {
                    window.Particles.spawnBurst(window.innerWidth / 2, window.innerHeight / 2, "#38bdf8", 25);
                    window.Particles.spawnFloatingText(window.innerWidth / 2, window.innerHeight / 2 - 30, `FILED TO ${targetCategory.toUpperCase()}! +25 XP`, "#38bdf8", 22);
                }
                if (window.App) window.App.refreshStatus();
                this.loadFiles();
            }
        } catch (err) {
            console.error("Sort file error:", err);
        }
    }

    async quarantineDuplicate(filename) {
        try {
            const res = await fetch("/api/files/quarantine-duplicate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ filename: filename })
            });
            const data = await res.json();

            if (data.success) {
                if (window.Sound) window.Sound.playExplosion();
                if (window.Particles) {
                    window.Particles.spawnBurst(window.innerWidth / 2, window.innerHeight / 2, "#ef4444", 35);
                    window.Particles.spawnFloatingText(window.innerWidth / 2, window.innerHeight / 2 - 40, `FREED ${data.formatted_size}! +40 XP`, "#ef4444", 24);
                }
                if (window.App) window.App.refreshStatus();
                this.loadFiles();
            }
        } catch (err) {
            console.error("Quarantine duplicate error:", err);
        }
    }

    async autoOrganizeRemaining() {
        if (this.files.length === 0) return;
        if (window.Sound) window.Sound.playPowerup();
        for (let file of [...this.files]) {
            await fetch("/api/files/organize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ filename: file.name, category: file.category })
            });
        }
        if (window.Particles) window.Particles.spawnConfetti();
        if (window.App) window.App.refreshStatus();
        this.loadFiles();
    }

    async resetSampleFiles() {
        try {
            await fetch("/api/files/reset-samples", { method: "POST" });
            if (window.Sound) window.Sound.playPowerup();
            await this.loadFiles();
        } catch (err) {
            console.error(err);
        }
    }
}

window.addEventListener("DOMContentLoaded", () => {
    window.FileGame = new FileSorterGame();
});
