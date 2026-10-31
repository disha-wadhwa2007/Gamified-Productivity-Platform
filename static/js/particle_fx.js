/**
 * ParticleFX - Fast canvas-based particle bursts and floating combat text.
 */
class ParticleEngine {
    constructor(canvasId = "fxCanvas") {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            this.canvas = document.createElement("canvas");
            this.canvas.id = canvasId;
            this.canvas.style.position = "fixed";
            this.canvas.style.top = "0";
            this.canvas.style.left = "0";
            this.canvas.style.width = "100%";
            this.canvas.style.height = "100%";
            this.canvas.style.pointerEvents = "none";
            this.canvas.style.zIndex = "9999";
            document.body.appendChild(this.canvas);
        }
        this.ctx = this.canvas.getContext("2d");
        this.particles = [];
        this.floatingTexts = [];
        this.resize();
        window.addEventListener("resize", () => this.resize());
        this.loop = this.loop.bind(this);
        requestAnimationFrame(this.loop);
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    spawnBurst(x, y, color = "#38bdf8", count = 25) {
        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 6 + 2;
            this.particles.push({
                x,
                y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                size: Math.random() * 4 + 2,
                color,
                alpha: 1.0,
                decay: Math.random() * 0.03 + 0.02
            });
        }
    }

    spawnFloatingText(x, y, text, color = "#fbbf24", fontSize = 20) {
        this.floatingTexts.push({
            x,
            y,
            text,
            color,
            fontSize,
            vy: -2,
            alpha: 1.0,
            decay: 0.02
        });
    }

    spawnConfetti() {
        const colors = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6"];
        for (let i = 0; i < 80; i++) {
            this.particles.push({
                x: window.innerWidth * Math.random(),
                y: -10,
                vx: (Math.random() - 0.5) * 3,
                vy: Math.random() * 4 + 3,
                size: Math.random() * 6 + 4,
                color: colors[Math.floor(Math.random() * colors.length)],
                alpha: 1.0,
                decay: 0.008
            });
        }
    }

    loop() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Update particles
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.alpha -= p.decay;

            if (p.alpha <= 0) {
                this.particles.splice(i, 1);
                continue;
            }

            this.ctx.save();
            this.ctx.globalAlpha = Math.max(0, p.alpha);
            this.ctx.fillStyle = p.color;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.restore();
        }

        // Update floating combat texts
        for (let i = this.floatingTexts.length - 1; i >= 0; i--) {
            const t = this.floatingTexts[i];
            t.y += t.vy;
            t.alpha -= t.decay;

            if (t.alpha <= 0) {
                this.floatingTexts.splice(i, 1);
                continue;
            }

            this.ctx.save();
            this.ctx.globalAlpha = Math.max(0, t.alpha);
            this.ctx.font = `bold ${t.fontSize}px 'Outfit', 'Inter', sans-serif`;
            this.ctx.fillStyle = t.color;
            this.ctx.shadowColor = "#000";
            this.ctx.shadowBlur = 6;
            this.ctx.fillText(t.text, t.x, t.y);
            this.ctx.restore();
        }

        requestAnimationFrame(this.loop);
    }
}

window.addEventListener("DOMContentLoaded", () => {
    window.Particles = new ParticleEngine();
});
