import sqlite3
import json
from typing import Dict, Any, List

STORY_CHAPTERS = [
    {
        "id": "chap_1",
        "number": 1,
        "title": "The Fog of 10,000 Unread",
        "discipline": "email_cleanup",
        "character": "Master Archivist Eldon",
        "avatar": "🧙‍♂️",
        "intro_dialogue": "Paladin! Look upon the Grand Messenger Spire. A foul black fog of phishing demons and promotional locusts has choked our lines of communication! Real royal decrees are trapped beneath mountains of junk scroll spam. Will you raise your blaster and cleanse the spire?",
        "objective": "Vanquish at least 3 spam demons and rescue the VIP Crystal Vessel.",
        "reward_xp": 250,
        "reward_gold": 100
    },
    {
        "id": "chap_2",
        "number": 2,
        "title": "The Hoarder's Catacombs",
        "discipline": "file_organization",
        "character": "Cyber-Alchemist Vesper",
        "avatar": "👩‍🔬",
        "intro_dialogue": "Our central cargo bay and desktop vaults are collapsing! Adventurers threw screenshots, installers, and cursed duplicate tomes haphazardly onto the floor. Storage crystals are at 99% capacity! Slay the duplicate beasts and sort the artifacts into their sacred vaults before the catacombs rupture!",
        "objective": "Classify files into their vaults and crush duplicate impostors.",
        "reward_xp": 300,
        "reward_gold": 120
    },
    {
        "id": "chap_3",
        "number": 3,
        "title": "The Vampire of the Golden Vault",
        "discipline": "expense_tracking",
        "character": "Chancellor Sterling",
        "avatar": "🧮",
        "intro_dialogue": "Disaster in the treasury! Gold coins are evaporating into the ether! Our ledger is an unorganized mess of mystery charges, and worse — dark Subscription Vampires are stealthily draining monthly coin for spells nobody has cast in moons! Hunt down the expense bounties, classify the ledger, and drive a stake through the recurring leeches!",
        "objective": "Categorize mystery expenses and vanquish all Subscription Vampires.",
        "reward_xp": 350,
        "reward_gold": 150
    },
    {
        "id": "chap_4",
        "number": 4,
        "title": "The Core of the Corrupted Automaton",
        "discipline": "code_debugging",
        "character": "Chief Mechanist Ada",
        "avatar": "🤖",
        "intro_dialogue": "Warning! The kingdom's Master Defense Matrix is stuttering! Glitch anomalies have infected the core scripts: infinite loops are melting the CPU, and null void sentinels are corrupting memory sectors. Step into the terminal matrix, identify the broken lines, and compile the purified patch before the system crashes forever!",
        "objective": "Debug the infected scripts and restore 100% operational integrity.",
        "reward_xp": 500,
        "reward_gold": 250
    }
]

class StoryEngine:
    def __init__(self, db_path="chorequest.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_progress (
                chapter_id TEXT PRIMARY KEY,
                completed INTEGER NOT NULL DEFAULT 0,
                stars INTEGER NOT NULL DEFAULT 0,
                completed_at TEXT
            )
            """)
            conn.commit()

            cursor.execute("SELECT COUNT(*) as count FROM story_progress")
            if cursor.fetchone()["count"] == 0:
                for chap in STORY_CHAPTERS:
                    cursor.execute("""
                    INSERT INTO story_progress (chapter_id, completed, stars, completed_at)
                    VALUES (?, 0, 0, NULL)
                    """, (chap["id"],))
                conn.commit()

    def get_campaign_status(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM story_progress")
            progress_map = {row["chapter_id"]: dict(row) for row in cursor.fetchall()}

            result = []
            for chap in STORY_CHAPTERS:
                data = dict(chap)
                prog = progress_map.get(chap["id"], {"completed": 0, "stars": 0})
                data["completed"] = bool(prog["completed"])
                data["stars"] = prog["stars"]
                data["completed_at"] = prog.get("completed_at")
                result.append(data)
            return result

    def complete_chapter(self, chapter_id: str, stars: int = 3) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            import datetime
            now = datetime.datetime.now().isoformat()
            cursor.execute("""
            UPDATE story_progress 
            SET completed = 1, stars = ?, completed_at = ?
            WHERE chapter_id = ?
            """, (stars, now, chapter_id))
            conn.commit()

        chap = next((c for c in STORY_CHAPTERS if c["id"] == chapter_id), None)
        return {
            "success": True,
            "chapter_id": chapter_id,
            "chapter_title": chap["title"] if chap else "",
            "stars": stars
        }
