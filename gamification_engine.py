import sqlite3
import json
import math
from typing import Dict, Any, List

SKILL_TREE = [
    {
        "id": "skill_hash_sight",
        "name": "Hash Sight",
        "category": "file",
        "icon": "👁️",
        "cost": 100,
        "description": "Instantly highlights duplicate files in the cargo bay with radiant purple aura.",
        "unlocked": False
    },
    {
        "id": "skill_regex_scythe",
        "name": "Regex Scythe",
        "category": "email",
        "icon": "⚔️",
        "cost": 150,
        "description": "Deals 2.5x critical damage to phishing and malicious scam emails.",
        "unlocked": False
    },
    {
        "id": "skill_budget_shield",
        "name": "Budget Shield",
        "category": "expense",
        "icon": "🛡️",
        "cost": 200,
        "description": "Identifies recurring vampire subscriptions with animated warning alarms.",
        "unlocked": False
    },
    {
        "id": "skill_ast_scanner",
        "name": "AST Deep Scanner",
        "category": "code",
        "icon": "🔮",
        "cost": 250,
        "description": "Reveals syntax error locations directly on the terminal HUD.",
        "unlocked": False
    },
    {
        "id": "skill_gravity_beam",
        "name": "Gravity Sorter Beam",
        "category": "file",
        "icon": "🧲",
        "cost": 300,
        "description": "Allows 1-click batch sorting of all documents and images into vaults.",
        "unlocked": False
    }
]

ACHIEVEMENTS = [
    {"id": "ach_first_blood", "title": "First Step to Order", "description": "Complete your first real productivity chore in game.", "icon": "🌱", "reward_xp": 50},
    {"id": "ach_inbox_zero", "title": "Inbox Purifier", "description": "Purge or file 5 inbox clutter messages.", "icon": "✉️", "reward_xp": 150},
    {"id": "ach_dup_destroyer", "title": "Duplicate Destroyer", "description": "Vanquish duplicate files to reclaim real disk storage.", "icon": "💥", "reward_xp": 200},
    {"id": "ach_vampire_slayer", "title": "Subscription Slayer", "description": "Slash an unused vampire subscription draining monthly gold.", "icon": "🧛", "reward_xp": 250},
    {"id": "ach_matrix_hacker", "title": "Bug Hunter Supreme", "description": "Patch corrupted code and restore clean execution.", "icon": "👾", "reward_xp": 300},
    {"id": "ach_grandmaster", "title": "Realm Protector", "description": "Reach Level 5 and restore total digital harmony.", "icon": "👑", "reward_xp": 500}
]

class GamificationEngine:
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
            CREATE TABLE IF NOT EXISTS player_profile (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL DEFAULT 'Hero of Order',
                level INTEGER NOT NULL DEFAULT 1,
                xp INTEGER NOT NULL DEFAULT 0,
                hp INTEGER NOT NULL DEFAULT 100,
                max_hp INTEGER NOT NULL DEFAULT 100,
                gold INTEGER NOT NULL DEFAULT 50,
                combo_streak INTEGER NOT NULL DEFAULT 0,
                highest_combo INTEGER NOT NULL DEFAULT 0,
                unlocked_skills TEXT NOT NULL DEFAULT '[]',
                unlocked_achievements TEXT NOT NULL DEFAULT '[]'
            )
            """)
            conn.commit()

            cursor.execute("SELECT COUNT(*) as count FROM player_profile")
            if cursor.fetchone()["count"] == 0:
                cursor.execute("""
                INSERT INTO player_profile (id, name, level, xp, hp, max_hp, gold, combo_streak, highest_combo, unlocked_skills, unlocked_achievements)
                VALUES (1, 'Cyber Paladin', 1, 0, 100, 100, 100, 0, 0, '[]', '[]')
                """)
                conn.commit()

    def get_profile(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM player_profile WHERE id = 1")
            row = dict(cursor.fetchone())
            
            unlocked_skills = json.loads(row["unlocked_skills"])
            unlocked_ach = json.loads(row["unlocked_achievements"])
            
            # XP formula: level * 100 XP
            xp_for_next = row["level"] * 100
            xp_progress_pct = min(100, int((row["xp"] / xp_for_next) * 100))

            # Enrich skills
            enriched_skills = []
            for s in SKILL_TREE:
                item = dict(s)
                item["unlocked"] = s["id"] in unlocked_skills
                enriched_skills.append(item)

            # Enrich achievements
            enriched_ach = []
            for a in ACHIEVEMENTS:
                item = dict(a)
                item["unlocked"] = a["id"] in unlocked_ach
                enriched_ach.append(item)

            return {
                "name": row["name"],
                "level": row["level"],
                "xp": row["xp"],
                "xp_for_next": xp_for_next,
                "xp_progress_pct": xp_progress_pct,
                "hp": row["hp"],
                "max_hp": row["max_hp"],
                "gold": row["gold"],
                "combo_streak": row["combo_streak"],
                "highest_combo": row["highest_combo"],
                "skills": enriched_skills,
                "achievements": enriched_ach
            }

    def award_xp_and_gold(self, xp_amount: int, gold_amount: int = 10, chore_type: str = "") -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM player_profile WHERE id = 1")
            row = dict(cursor.fetchone())

            new_combo = row["combo_streak"] + 1
            highest_combo = max(row["highest_combo"], new_combo)
            combo_multiplier = 1.0 + min(2.0, (new_combo - 1) * 0.1)

            final_xp = int(xp_amount * combo_multiplier)
            final_gold = int(gold_amount * combo_multiplier)

            current_xp = row["xp"] + final_xp
            current_gold = row["gold"] + final_gold
            current_level = row["level"]
            leveled_up = False

            # Check level up
            xp_threshold = current_level * 100
            while current_xp >= xp_threshold:
                current_xp -= xp_threshold
                current_level += 1
                leveled_up = True
                xp_threshold = current_level * 100

            # Check achievements
            unlocked_ach = set(json.loads(row["unlocked_achievements"]))
            new_achievements = []

            if "ach_first_blood" not in unlocked_ach:
                unlocked_ach.add("ach_first_blood")
                new_achievements.append("First Step to Order")

            if current_level >= 5 and "ach_grandmaster" not in unlocked_ach:
                unlocked_ach.add("ach_grandmaster")
                new_achievements.append("Realm Protector")

            cursor.execute("""
            UPDATE player_profile 
            SET xp = ?, gold = ?, level = ?, combo_streak = ?, highest_combo = ?, unlocked_achievements = ?
            WHERE id = 1
            """, (current_xp, current_gold, current_level, new_combo, highest_combo, json.dumps(list(unlocked_ach))))
            conn.commit()

            return {
                "xp_gained": final_xp,
                "gold_gained": final_gold,
                "combo": new_combo,
                "combo_multiplier": round(combo_multiplier, 1),
                "leveled_up": leveled_up,
                "new_level": current_level,
                "new_achievements": new_achievements
            }

    def unlock_skill(self, skill_id: str) -> Dict[str, Any]:
        skill = next((s for s in SKILL_TREE if s["id"] == skill_id), None)
        if not skill:
            return {"success": False, "error": "Skill not found"}

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM player_profile WHERE id = 1")
            row = dict(cursor.fetchone())

            unlocked_skills = set(json.loads(row["unlocked_skills"]))
            if skill_id in unlocked_skills:
                return {"success": False, "error": "Skill is already unlocked"}

            if row["gold"] < skill["cost"]:
                return {"success": False, "error": f"Insufficient gold! Needs {skill['cost']} gold, you have {row['gold']}"}

            unlocked_skills.add(skill_id)
            new_gold = row["gold"] - skill["cost"]

            cursor.execute("""
            UPDATE player_profile 
            SET gold = ?, unlocked_skills = ?
            WHERE id = 1
            """, (new_gold, json.dumps(list(unlocked_skills))))
            conn.commit()

            return {
                "success": True,
                "skill_name": skill["name"],
                "remaining_gold": new_gold
            }

    def reset_combo(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE player_profile SET combo_streak = 0 WHERE id = 1")
            conn.commit()
