# ⚔️ ChoreQuest: The Gamified Productivity Platform

> **Transform boring digital chores into engaging, fast-paced games and interactive stories while the system automatically performs the corresponding real-world tasks in the background.**

---

## 🌟 Overview & The "Dual-Engine" Architecture

Most gamified apps merely reward points or display to-do checklists while you still do all the boring chores manually. **ChoreQuest fundamentally flips this paradigm**:

```
 ┌───────────────────────────────────────────────────────────────┐
 │                     GAMEPLAY ACTION LAYER                     │
 │  • Space Blaster    • Sorter Belt    • Bounty Hunt   • Hacking │
 └──────────────────────────────┬────────────────────────────────┘
                                │ Bi-Directional Event Stream
                                ▼
 ┌───────────────────────────────────────────────────────────────┐
 │                  BACKGROUND REAL-WORLD ENGINE                 │
 │  • Email Cleanup    • File Sorting   • Expense Audit • AST Fix │
 └──────────────────────────────┬────────────────────────────────┘
                                │ Atomic Journal & Safety Locks
                                ▼
 ┌───────────────────────────────────────────────────────────────┐
 │               TIME MACHINE & AUDIT ROLLBACK ENGINE            │
 │  • 1-Click Rollback • MD5 Deduplication • Dry-Run Simulation  │
 └───────────────────────────────────────────────────────────────┘
```

When you destroy an enemy in **Spam Galaxy Defender**, the background engine physically purges junk from your inbox. When you sort an incoming cargo crate into the **Scroll Vault**, the file is physically moved into `Documents/` on your drive. When you slay a **Subscription Vampire**, the recurring expense is canceled, updating your monthly burn and generating a verified Excel ledger.

---

## 🎮 The 4 Game Arenas & Chore Disciplines

### 1. 🚀 Spam Galaxy Defender (Email Cleanup)
- **The Game**: An arcade starship dogfight with 60fps canvas controls (`[A]`/`[D]` or Mouse, `[SPACE]` to shoot laser, rapid fire).
- **Enemies**:
  - **Phishing Leviathans & Trojan Dreadnoughts**: Heavy-damage red ships representing dangerous scam emails.
  - **Bargain Swarms & Scribe Drones**: Yellow drones representing promotional newsletter clutter.
  - **VIP Crystal Freighters**: Radiant gold ally vessels carrying urgent executive or client transmissions.
- **Real-World Action**:
  - Blasting enemies automatically moves real emails to the **Trash** or archives them.
  - Shielding or locking onto VIP freighters stars and prioritizes urgent messages.
  - Real-time HUD displays total KB reclaimed and unread counts.

### 2. 📦 Dungeon Cargo Sorter & Loot Sorter (File Organization)
- **The Game**: A warehouse conveyor belt puzzle where chaotic crates and chests tumble into the sorting bay.
- **Mechanics**:
  - Hotkeys `[1]` to `[6]` flick loose files into dedicated vaults: **Scroll Vault** (`Documents`), **Prism Gallery** (`Images`), **Echo Cavern** (`Media`), **Titan Foundry** (`Installers`), **Mummy Crypt** (`Archives`), and **Logic Shrine** (`Code`).
  - **Duplicate Smasher**: Files with identical byte-for-byte **MD5 hashes** (e.g., duplicate installers or screenshots) glow with a dangerous purple aura. Slaying them immediately quarantines the duplicates and reclaims megabytes of disk space!
  - **Gravity Sorter Beam**: 1-click batch sweep that cleans an entire directory in seconds.
- **Real-World Action**:
  - Physically sorts files in `sample_data/messy_files` or any custom folder on your system.

### 3. 🗡️ Receipt Rogue: Vampire Slayer (Expense Tracking)
- **The Game**: An RPG tavern bounty board where receipts and unreviewed bank line items are wild bounties.
- **Mechanics**:
  - Claim bounties by classifying expenses into Kingdom tax categories (Developer Tooling, Infrastructure & Hosting, Meals, Hardware, etc.).
  - **Vampire Subscription Lair**: Automatically detects forgotten monthly SaaS recurring charges that have zero recent activity.
  - Driving a silver stake into the vampire cancels the recurring subscription, saving real money per month and per year!
- **Real-World Action**:
  - Calculates active burn rate and net savings.
  - One-click export generates both a formatted **CSV** and an **Excel (`.xlsx`)** workbook using `pandas` and `openpyxl`.

### 4. 💻 Matrix Bug Exterminator (Code Debugging)
- **The Game**: A cyberpunk terminal mainframe battle against rogue glitch sentinels.
- **Mechanics**:
  - Real corruptions: Infinite CPU loops, null pointer property access, zero-division errors, and SQL injection flaws.
  - Interactive terminal displays line-by-line syntax highlighting and vulnerability intel.
  - Player deploys tactical code patches. Choosing the correct spell defeats the Glitch Sentinel and generates a live git diff (`+` and `-`).
- **Real-World Action**:
  - Validates syntax using Python's `ast.parse` and writes the purified code directly to the real file on disk.

---

## 📖 "The Chronicles of the Pure Realm" (Story Mode)

An interactive 4-chapter narrative campaign connecting all productivity disciplines:
- **Chapter 1: The Fog of 10,000 Unread** — Cleanse the royal messenger spires with *Master Archivist Eldon*.
- **Chapter 2: The Hoarder's Catacombs** — Reclaim collapsing desktop vaults with *Cyber-Alchemist Vesper*.
- **Chapter 3: The Vampire of the Golden Vault** — Audit kingdom treasury leaks with *Chancellor Sterling*.
- **Chapter 4: The Core of the Corrupted Automaton** — Debug defense mainframe scripts with *Chief Mechanist Ada*.

---

## 🛡️ Time Machine Audit & Safety Guardrails

- **Atomic Transaction Journal**: Every action (file move, trash, tag, expense categorization, code patch) is saved with a unique ID (e.g. `TX-F1453EBA`) and full before/after snapshots in an atomic SQLite ledger.
- **1-Click Rollback**: Any action can be reversed instantly. If you moved a file by accident, clicking rollback restores the file to its exact original location.
- **Dry Run Mode**: A global toggle on the top navigation bar switches the entire platform into a risk-free simulation mode so users can practice without touching disk or databases.

---

## 🔊 Zero-Dependency Procedural Audio & Visuals

- **Web Audio API Procedural Synthesizer (`sound_fx.js`)**: 100% offline, zero external MP3s, generating dynamic 8-bit laser blasts, coin clinks, powerups, slashes, and victory fanfares.
- **Canvas Particle Engine (`particle_fx.js`)**: High-performance floating combat text (`+25 XP`, `DUPLICATE CRUSHED!`), fireworks, explosions, and combo streak multipliers.

---

## 🚀 Quick Start

### Option 1: Double Click
Double-click `start.bat` in this folder. It will start the server and open `http://127.0.0.1:8765` in your browser.

### Option 2: Command Line
```powershell
cd c:\Users\Disha\Downloads\chorequest
python server.py
```
Then open: **`http://127.0.0.1:8765`**
