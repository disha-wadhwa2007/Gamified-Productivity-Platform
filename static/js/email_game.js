/**
 * Email Game: "Spam Galaxy Defender"
 * Transforms unread inbox clutter, phishing, & bloated newsletters into an arcade space battle.
 */
class EmailDefenderGame {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.emails = [];
        this.stats = {};
        this.running = false;
        this.player = { x: 300, y: 380, width: 44, height: 44, speed: 7 };
        this.bullets = [];
        this.enemies = [];
        this.stars = [];
        this.keys = {};
        this.lastShot = 0;
        this.combo = 0;
        this.selectedEmail = null;
    }

    init() {
        this.canvas = document.getElementById("emailCanvas");
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext("2d");
        this.setupStars();
        this.bindEvents();
        this.loadEmails();
    }

    setupStars() {
        this.stars = [];
        for (let i = 0; i < 60; i++) {
            this.stars.push({
                x: Math.random() * (this.canvas ? this.canvas.width : 700),
                y: Math.random() * (this.canvas ? this.canvas.height : 450),
                size: Math.random() * 2 + 0.5,
                speed: Math.random() * 1.5 + 0.5
            });
        }
    }

    bindEvents() {
        window.addEventListener("keydown", (e) => {
            if (["ArrowLeft", "ArrowRight", "Space", "KeyA", "KeyD"].includes(e.code)) {
                this.keys[e.code] = true;
                if (e.code === "Space") e.preventDefault();
            }
        });
        window.addEventListener("keyup", (e) => {
            this.keys[e.code] = false;
        });

        // Mouse aiming on canvas
        this.canvas.addEventListener("mousemove", (e) => {
            const rect = this.canvas.getBoundingClientRect();
            this.player.x = e.clientX - rect.left - this.player.width / 2;
        });

        this.canvas.addEventListener("click", (e) => {
            this.shoot();
        });
    }

    async loadEmails() {
        try {
            const res = await fetch("/api/email/inbox");
            const data = await res.json();
            this.emails = data.emails || [];
            this.stats = data.stats || {};
            this.spawnEnemiesFromEmails();
            this.renderEmailList();
            this.updateHUD();
        } catch (err) {
            console.error("Failed to load emails:", err);
        }
    }

    spawnEnemiesFromEmails() {
        this.enemies = [];
        const padding = 30;
        const width = this.canvas.width - padding * 2;
        const count = Math.min(this.emails.length, 6);

        for (let i = 0; i < count; i++) {
            const email = this.emails[i];
            const col = i % 4;
            const row = Math.floor(i / 4);
            const x = padding + (col * (width / 4)) + 20;
            const y = 50 + (row * 80);

            this.enemies.push({
                email: email,
                x: x,
                y: y,
                width: 64,
                height: 50,
                hp: email.hp || 30,
                maxHp: email.hp || 30,
                isVip: email.is_vip,
                type: email.type,
                bobOffset: Math.random() * Math.PI * 2,
                color: email.is_vip ? "#f59e0b" : (email.type === "phishing" ? "#ef4444" : "#38bdf8")
            });
        }
    }

    start() {
        if (!this.running) {
            this.running = true;
            this.loop = this.loop.bind(this);
            requestAnimationFrame(this.loop);
        }
    }

    stop() {
        this.running = false;
    }

    shoot() {
        const now = Date.now();
        if (now - this.lastShot < 180) return;
        this.lastShot = now;

        this.bullets.push({
            x: this.player.x + this.player.width / 2 - 3,
            y: this.player.y,
            width: 6,
            height: 16,
            speed: 12
        });

        if (window.Sound) window.Sound.playLaser();
    }

    loop() {
        if (!this.running) return;

        // Player controls
        if (this.keys["ArrowLeft"] || this.keys["KeyA"]) {
            this.player.x = Math.max(10, this.player.x - this.player.speed);
        }
        if (this.keys["ArrowRight"] || this.keys["KeyD"]) {
            this.player.x = Math.min(this.canvas.width - this.player.width - 10, this.player.x + this.player.speed);
        }
        if (this.keys["Space"]) {
            this.shoot();
        }

        this.update();
        this.draw();

        requestAnimationFrame(this.loop);
    }

    update() {
        // Move stars
        for (let star of this.stars) {
            star.y += star.speed;
            if (star.y > this.canvas.height) {
                star.y = 0;
                star.x = Math.random() * this.canvas.width;
            }
        }

        // Update bullets
        for (let i = this.bullets.length - 1; i >= 0; i--) {
            const b = this.bullets[i];
            b.y -= b.speed;
            if (b.y < -20) {
                this.bullets.splice(i, 1);
                continue;
            }

            // Bullet vs Enemy collision
            for (let j = this.enemies.length - 1; j >= 0; j--) {
                const e = this.enemies[j];
                if (b.x < e.x + e.width && b.x + b.width > e.x &&
                    b.y < e.y + e.height && b.y + b.height > e.y) {
                    
                    this.bullets.splice(i, 1);
                    e.hp -= 20;

                    if (window.Particles) {
                        window.Particles.spawnBurst(b.x, b.y, e.color, 8);
                    }

                    if (e.hp <= 0) {
                        this.destroyEnemy(e, j);
                    } else {
                        if (window.Sound) window.Sound.playSlash();
                    }
                    break;
                }
            }
        }

        // Enemy hovering
        const t = Date.now() * 0.003;
        for (let e of this.enemies) {
            e.y += Math.sin(t + e.bobOffset) * 0.3;
        }
    }

    async destroyEnemy(enemy, index) {
        this.enemies.splice(index, 1);
        const rect = this.canvas.getBoundingClientRect();
        const screenX = rect.left + enemy.x + enemy.width / 2;
        const screenY = rect.top + enemy.y + enemy.height / 2;

        if (window.Sound) window.Sound.playExplosion();
        if (window.Particles) {
            window.Particles.spawnBurst(screenX, screenY, enemy.color, 30);
            window.Particles.spawnFloatingText(screenX, screenY - 20, enemy.isVip ? "RESCUED!" : "PURGED! +30 XP", "#10b981", 20);
        }

        const action = enemy.isVip ? "star" : (enemy.type === "newsletter" ? "archive" : "trash");
        await this.triggerRealEmailAction(enemy.email.id, action);
    }

    async triggerRealEmailAction(emailId, action) {
        try {
            const res = await fetch("/api/email/action", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email_id: emailId, action: action })
            });
            const data = await res.json();
            if (data.success) {
                if (window.App) window.App.refreshStatus();
                this.loadEmails();
            }
        } catch (err) {
            console.error("Email action error:", err);
        }
    }

    draw() {
        this.ctx.fillStyle = "#090d16";
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw stars
        this.ctx.fillStyle = "#ffffff";
        for (let s of this.stars) {
            this.ctx.beginPath();
            this.ctx.arc(s.x, s.y, s.size, 0, Math.PI * 2);
            this.ctx.fill();
        }

        // Draw enemies
        for (let e of this.enemies) {
            this.ctx.save();
            this.ctx.translate(e.x, e.y);

            // Monster ship body
            this.ctx.fillStyle = e.color;
            this.ctx.beginPath();
            if (e.isVip) {
                // Crystal vessel shape
                this.ctx.moveTo(e.width / 2, 0);
                this.ctx.lineTo(e.width, e.height / 2);
                this.ctx.lineTo(e.width / 2, e.height);
                this.ctx.lineTo(0, e.height / 2);
                this.ctx.closePath();
            } else {
                // Invader fighter
                this.ctx.moveTo(e.width / 2, e.height);
                this.ctx.lineTo(e.width, 10);
                this.ctx.lineTo(e.width - 10, 0);
                this.ctx.lineTo(e.width / 2, 15);
                this.ctx.lineTo(10, 0);
                this.ctx.lineTo(0, 10);
                this.ctx.closePath();
            }
            this.ctx.fill();

            // Glow outline
            this.ctx.strokeStyle = "#ffffff";
            this.ctx.lineWidth = 1.5;
            this.ctx.stroke();

            // HP Bar
            const hpWidth = e.width * (e.hp / e.maxHp);
            this.ctx.fillStyle = "#334155";
            this.ctx.fillRect(0, -10, e.width, 5);
            this.ctx.fillStyle = e.isVip ? "#fbbf24" : "#ef4444";
            this.ctx.fillRect(0, -10, Math.max(0, hpWidth), 5);

            // Icon / Label
            this.ctx.fillStyle = "#ffffff";
            this.ctx.font = "10px sans-serif";
            this.ctx.textAlign = "center";
            const label = e.email.sender_name.slice(0, 10) + "..";
            this.ctx.fillText(label, e.width / 2, e.height + 14);

            this.ctx.restore();
        }

        // Draw bullets
        this.ctx.fillStyle = "#38bdf8";
        this.ctx.shadowColor = "#38bdf8";
        this.ctx.shadowBlur = 10;
        for (let b of this.bullets) {
            this.ctx.fillRect(b.x, b.y, b.width, b.height);
        }
        this.ctx.shadowBlur = 0;

        // Draw player ship
        this.ctx.save();
        this.ctx.translate(this.player.x, this.player.y);
        this.ctx.fillStyle = "#10b981";
        this.ctx.beginPath();
        this.ctx.moveTo(this.player.width / 2, 0);
        this.ctx.lineTo(this.player.width, this.player.height);
        this.ctx.lineTo(this.player.width / 2, this.player.height - 10);
        this.ctx.lineTo(0, this.player.height);
        this.ctx.closePath();
        this.ctx.fill();

        // Thruster flame
        this.ctx.fillStyle = "#f59e0b";
        this.ctx.beginPath();
        this.ctx.moveTo(this.player.width / 2 - 6, this.player.height - 5);
        this.ctx.lineTo(this.player.width / 2 + 6, this.player.height - 5);
        this.ctx.lineTo(this.player.width / 2, this.player.height + 12 + Math.random() * 6);
        this.ctx.closePath();
        this.ctx.fill();

        this.ctx.restore();
    }

    renderEmailList() {
        const container = document.getElementById("emailDeckList");
        if (!container) return;

        if (this.emails.length === 0) {
            container.innerHTML = `
                <div class="empty-deck">
                    <div style="font-size: 3rem;">🎉</div>
                    <h3>Inbox Zero Attained!</h3>
                    <p>All junk, phishing, and newsletters vanquished from your inbox.</p>
                    <button class="btn btn-primary" onclick="window.EmailGame.resetMailbox()">Spawn New Wave</button>
                </div>
            `;
            return;
        }

        container.innerHTML = this.emails.map(em => `
            <div class="email-card ${em.is_vip ? 'vip-card' : ''} ${em.type}">
                <div class="email-header">
                    <span class="sender-name">${em.sender_name}</span>
                    <span class="email-date">${em.date}</span>
                </div>
                <div class="email-subject">${em.subject}</div>
                <div class="email-snippet">${em.snippet}</div>
                <div class="email-actions">
                    ${em.is_vip ? `
                        <button class="btn btn-vip" onclick="window.EmailGame.triggerRealEmailAction('${em.id}', 'star')">
                            ⭐ Rescue & Star (VIP)
                        </button>
                    ` : `
                        <button class="btn btn-blast" onclick="window.EmailGame.triggerRealEmailAction('${em.id}', 'trash')">
                            💥 Blast to Trash (${em.size_kb} KB)
                        </button>
                        <button class="btn btn-archive" onclick="window.EmailGame.triggerRealEmailAction('${em.id}', 'archive')">
                            📥 Safe Archive
                        </button>
                    `}
                </div>
            </div>
        `).join("");
    }

    updateHUD() {
        const countEl = document.getElementById("emailCountBadge");
        if (countEl) countEl.innerText = `${this.emails.length} Unread`;
        const freedEl = document.getElementById("emailFreedKb");
        if (freedEl) freedEl.innerText = `${(this.stats.freed_kb || 0).toLocaleString()} KB Purged`;
    }

    async resetMailbox() {
        try {
            await fetch("/api/email/reset", { method: "POST" });
            if (window.Sound) window.Sound.playPowerup();
            await this.loadEmails();
        } catch (err) {
            console.error(err);
        }
    }
}

window.addEventListener("DOMContentLoaded", () => {
    window.EmailGame = new EmailDefenderGame();
});
