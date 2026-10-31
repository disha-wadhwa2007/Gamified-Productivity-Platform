import json
import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Any
from chore_engine.transaction_manager import TransactionManager

INITIAL_EMAILS = [
    {
        "id": "EM-001",
        "sender": "crypto-king99@fastwealth-airdrop.xyz",
        "sender_name": "Crypto Airdrop Bot",
        "subject": "CLAIM NOW: 50,000 $DOGEX Tokens transferred to your wallet!",
        "snippet": "Congratulations! Your email has been randomly selected for our Web3 mega distribution...",
        "type": "spam",
        "monster_type": "Phishing Leviathan",
        "hp": 40,
        "is_vip": False,
        "size_kb": 140,
        "date": "10 mins ago",
        "recommended_action": "trash"
    },
    {
        "id": "EM-002",
        "sender": "deals@megashopper-daily.com",
        "sender_name": "MegaShopper Deals",
        "subject": "⚡ 90% OFF Flash Sale ends in 32 minutes! Don't miss out",
        "snippet": "Check out today's top picks for kitchen blenders, RGB keyboards, and massage pillows...",
        "type": "newsletter",
        "monster_type": "Bargain Swarm Drone",
        "hp": 25,
        "is_vip": False,
        "size_kb": 320,
        "date": "1 hour ago",
        "recommended_action": "archive"
    },
    {
        "id": "EM-003",
        "sender": "sarah.chen@techcorp-exec.io",
        "sender_name": "Sarah Chen (VP Engineering)",
        "subject": "URGENT: Q4 Architecture Review & Board Deck Signoff",
        "snippet": "Hi team, please review the attached slides before tomorrow's 9 AM executive briefing. Critical...",
        "type": "vip",
        "monster_type": "VIP Crystal Vessel",
        "hp": 100,
        "is_vip": True,
        "size_kb": 2400,
        "date": "2 hours ago",
        "recommended_action": "star"
    },
    {
        "id": "EM-004",
        "sender": "notifications@socialstream-buzz.net",
        "sender_name": "SocialBuzz Alerts",
        "subject": "38 people viewed your profile this week",
        "snippet": "See who checked your updates and reconnect with colleagues on SocialBuzz...",
        "type": "notification",
        "monster_type": "Chirp Probe",
        "hp": 20,
        "is_vip": False,
        "size_kb": 45,
        "date": "3 hours ago",
        "recommended_action": "mark_read"
    },
    {
        "id": "EM-005",
        "sender": "billing-alert-suspicious@paypal-verify-account-92.cc",
        "sender_name": "Security Notice Service",
        "subject": "Your account has been restricted! Verify identity within 24h",
        "snippet": "Unusual sign-in activity detected from Murmansk. Click here immediately to avoid permanent ban...",
        "type": "phishing",
        "monster_type": "Trojan Dreadnought",
        "hp": 60,
        "is_vip": False,
        "size_kb": 180,
        "date": "4 hours ago",
        "recommended_action": "trash"
    },
    {
        "id": "EM-006",
        "sender": "newsletter@weeklydevdigest.dev",
        "sender_name": "Weekly Dev Digest",
        "subject": "Issue #184: Quantum Compilers & 10 CSS Tricks You Forgot",
        "snippet": "Welcome to this week's issue! Deep dive into WebAssembly threads and compiler optimization...",
        "type": "newsletter",
        "monster_type": "Code Scribe Drone",
        "hp": 30,
        "is_vip": False,
        "size_kb": 410,
        "date": "5 hours ago",
        "recommended_action": "archive"
    },
    {
        "id": "EM-007",
        "sender": "alex.kumar@clientpartner.org",
        "sender_name": "Alex Kumar (Principal Client)",
        "subject": "Contract Renewal & Scope Extension Confirmation",
        "snippet": "Hi, we received your proposal and the committee approved the extension with no revisions...",
        "type": "vip",
        "monster_type": "VIP Crystal Vessel",
        "hp": 100,
        "is_vip": True,
        "size_kb": 1200,
        "date": "6 hours ago",
        "recommended_action": "star"
    },
    {
        "id": "EM-008",
        "sender": "winner@international-lottery-eu.org",
        "sender_name": "Lord Hamilton",
        "subject": "FINAL NOTIFICATION: £2,500,000 Unclaimed Inheritance Fund",
        "snippet": "My late client left funds with no beneficiary. Reply with your passport copy to begin transfer...",
        "type": "spam",
        "monster_type": "Mirage Wraith",
        "hp": 35,
        "is_vip": False,
        "size_kb": 95,
        "date": "8 hours ago",
        "recommended_action": "trash"
    },
    {
        "id": "EM-009",
        "sender": "no-reply@cloudprovider-billing.com",
        "sender_name": "Cloud Compute Billing",
        "subject": "Monthly Usage Alert: 85% of Monthly Tier Reached",
        "snippet": "Your cluster compute credits are running low. Current usage: $418.20 of $500 monthly limit...",
        "type": "notification",
        "monster_type": "Credit Leech Golem",
        "hp": 30,
        "is_vip": False,
        "size_kb": 65,
        "date": "9 hours ago",
        "recommended_action": "archive"
    },
    {
        "id": "EM-010",
        "sender": "support@gym-pass-frenzy.io",
        "sender_name": "FitFlex Gym Club",
        "subject": "We miss you! Re-activate your abandoned membership for $1",
        "snippet": "It has been 180 days since your last check-in. Don't lose your gains! Claim your coupon...",
        "type": "newsletter",
        "monster_type": "Gym Ghost Drone",
        "hp": 25,
        "is_vip": False,
        "size_kb": 220,
        "date": "1 day ago",
        "recommended_action": "archive"
    }
]

class EmailEngine:
    def __init__(self, db_path="chorequest.db", transaction_mgr: TransactionManager = None):
        self.db_path = db_path
        self.tx_mgr = transaction_mgr or TransactionManager()
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                sender_name TEXT NOT NULL,
                subject TEXT NOT NULL,
                snippet TEXT NOT NULL,
                type TEXT NOT NULL,
                monster_type TEXT NOT NULL,
                hp INTEGER NOT NULL,
                is_vip INTEGER NOT NULL DEFAULT 0,
                size_kb INTEGER NOT NULL DEFAULT 100,
                date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'inbox',
                is_starred INTEGER NOT NULL DEFAULT 0,
                is_read INTEGER NOT NULL DEFAULT 0
            )
            """)
            conn.commit()

            cursor.execute("SELECT COUNT(*) as count FROM emails")
            if cursor.fetchone()["count"] == 0:
                self.reset_mailbox()

    def reset_mailbox(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM emails")
            for em in INITIAL_EMAILS:
                cursor.execute("""
                INSERT INTO emails (id, sender, sender_name, subject, snippet, type, monster_type, hp, is_vip, size_kb, date, status, is_starred, is_read)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'inbox', 0, 0)
                """, (
                    em["id"], em["sender"], em["sender_name"], em["subject"], em["snippet"],
                    em["type"], em["monster_type"], em["hp"], 1 if em["is_vip"] else 0,
                    em["size_kb"], em["date"]
                ))
            conn.commit()

    def get_inbox(self, filter_status="inbox") -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emails WHERE status = ? ORDER BY id ASC", (filter_status,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'inbox' THEN 1 ELSE 0 END) as inbox_count,
                SUM(CASE WHEN status = 'trashed' THEN 1 ELSE 0 END) as trashed_count,
                SUM(CASE WHEN status = 'archived' THEN 1 ELSE 0 END) as archived_count,
                SUM(CASE WHEN is_starred = 1 THEN 1 ELSE 0 END) as starred_count,
                SUM(CASE WHEN status = 'trashed' THEN size_kb ELSE 0 END) as freed_kb
            FROM emails
            """)
            row = cursor.fetchone()
            return {
                "total": row["total"] or 0,
                "inbox_count": row["inbox_count"] or 0,
                "trashed_count": row["trashed_count"] or 0,
                "archived_count": row["archived_count"] or 0,
                "starred_count": row["starred_count"] or 0,
                "freed_kb": row["freed_kb"] or 0
            }

    def process_email_action(self, email_id: str, action: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Actions:
        - 'blast' / 'trash': Purges spam/phishing
        - 'archive': Archives newsletter/notification
        - 'star': Protects VIP message
        - 'mark_read': Marks notification as read
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": f"Email {email_id} not found"}

            before_state = {
                "id": email_id,
                "status": row["status"],
                "is_starred": row["is_starred"],
                "is_read": row["is_read"]
            }

            after_state = dict(before_state)
            details = ""
            impact_metric = "emails_cleaned"
            impact_val = 1.0

            if action in ["blast", "trash"]:
                after_state["status"] = "trashed"
                details = f"Vanquished spam: '{row['subject']}' moved to Trash"
                impact_metric = "bytes_freed"
                impact_val = row["size_kb"] * 1024
            elif action == "archive":
                after_state["status"] = "archived"
                after_state["is_read"] = 1
                details = f"Archived newsletter: '{row['subject']}' safely filed"
            elif action == "star":
                after_state["is_starred"] = 1
                after_state["is_read"] = 1
                details = f"Secured VIP Transmission: '{row['subject']}' starred & prioritized"
            elif action == "mark_read":
                after_state["is_read"] = 1
                details = f"Reviewed notification: '{row['subject']}' marked read"

            if not dry_run:
                cursor.execute("""
                UPDATE emails 
                SET status = ?, is_starred = ?, is_read = ?
                WHERE id = ?
                """, (after_state["status"], after_state["is_starred"], after_state["is_read"], email_id))
                conn.commit()

            tx = self.tx_mgr.record(
                chore_type="email_cleanup",
                action=action,
                details=details,
                before_state=before_state,
                after_state=after_state,
                is_dry_run=dry_run,
                impact_metric=impact_metric,
                impact_value=impact_val
            )

            return {
                "success": True,
                "email_id": email_id,
                "action": action,
                "details": details,
                "transaction": tx
            }
