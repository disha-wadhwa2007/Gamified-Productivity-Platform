/**
 * SoundFX - Procedural Web Audio API Synthesizer
 * 100% zero external dependencies, works offline, low latency.
 */
class SoundEngine {
    constructor() {
        this.ctx = null;
        this.muted = false;
        this.masterVolume = 0.3;
    }

    _initContext() {
        if (!this.ctx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AudioCtx();
        }
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    toggleMute() {
        this.muted = !this.muted;
        return this.muted;
    }

    playLaser() {
        if (this.muted) return;
        this._initContext();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';

        const now = this.ctx.currentTime;
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.exponentialRampToValueAtTime(110, now + 0.15);

        gain.gain.setValueAtTime(this.masterVolume * 0.4, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.15);
    }

    playCoin() {
        if (this.muted) return;
        this._initContext();
        const now = this.ctx.currentTime;
        const osc1 = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(987.77, now); // B5
        osc1.frequency.setValueAtTime(1318.51, now + 0.08); // E6

        gain.gain.setValueAtTime(this.masterVolume * 0.5, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);

        osc1.connect(gain);
        gain.connect(this.ctx.destination);
        osc1.start(now);
        osc1.stop(now + 0.3);
    }

    playPowerup() {
        if (this.muted) return;
        this._initContext();
        const now = this.ctx.currentTime;
        const notes = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99]; // C major arpeggio
        notes.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.value = freq;
            const startTime = now + idx * 0.05;
            gain.gain.setValueAtTime(this.masterVolume * 0.3, startTime);
            gain.gain.exponentialRampToValueAtTime(0.001, startTime + 0.15);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(startTime);
            osc.stop(startTime + 0.15);
        });
    }

    playExplosion() {
        if (this.muted) return;
        this._initContext();
        const now = this.ctx.currentTime;
        const bufferSize = this.ctx.sampleRate * 0.25;
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.3));
        }

        const noise = this.ctx.createBufferSource();
        noise.buffer = buffer;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(800, now);
        filter.frequency.linearRampToValueAtTime(50, now + 0.25);

        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(this.masterVolume * 0.6, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);

        noise.connect(filter);
        filter.connect(gain);
        gain.connect(this.ctx.destination);
        noise.start(now);
    }

    playSlash() {
        if (this.muted) return;
        this._initContext();
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(600, now);
        osc.frequency.exponentialRampToValueAtTime(80, now + 0.12);

        gain.gain.setValueAtTime(this.masterVolume * 0.4, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.12);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.12);
    }

    playVictory() {
        if (this.muted) return;
        this._initContext();
        const now = this.ctx.currentTime;
        const melody = [
            { f: 523.25, d: 0.15 }, // C5
            { f: 523.25, d: 0.15 }, // C5
            { f: 523.25, d: 0.15 }, // C5
            { f: 659.25, d: 0.35 }, // E5
            { f: 783.99, d: 0.50 }  // G5
        ];

        let cursor = now;
        melody.forEach(note => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'square';
            osc.frequency.value = note.f;

            gain.gain.setValueAtTime(this.masterVolume * 0.35, cursor);
            gain.gain.exponentialRampToValueAtTime(0.01, cursor + note.d);

            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(cursor);
            osc.stop(cursor + note.d);
            cursor += note.d * 0.9;
        });
    }

    playShield() {
        if (this.muted) return;
        this._initContext();
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(300, now);
        osc.frequency.linearRampToValueAtTime(880, now + 0.2);

        gain.gain.setValueAtTime(this.masterVolume * 0.4, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.25);
    }

    playError() {
        if (this.muted) return;
        this._initContext();
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(130, now);
        osc.frequency.setValueAtTime(98, now + 0.1);

        gain.gain.setValueAtTime(this.masterVolume * 0.5, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.25);
    }
}

window.Sound = new SoundEngine();
