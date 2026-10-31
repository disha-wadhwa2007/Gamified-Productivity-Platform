import os
import json
import sqlite3
import datetime
import uuid
import shutil
from pathlib import Path

class TransactionManager:
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
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                chore_type TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                before_state TEXT NOT NULL,
                after_state TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'completed',
                is_dry_run INTEGER NOT NULL DEFAULT 0,
                impact_metric TEXT,
                impact_value REAL DEFAULT 0
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_stats (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """)
            conn.commit()

    def record(self, chore_type: str, action: str, details: str, before_state: dict, after_state: dict, is_dry_run: bool = False, impact_metric: str = None, impact_value: float = 0.0) -> dict:
        tx_id = f"TX-{str(uuid.uuid4())[:8].upper()}"
        now = datetime.datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO transactions (id, timestamp, chore_type, action, details, before_state, after_state, status, is_dry_run, impact_metric, impact_value)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'completed', ?, ?, ?)
            """, (
                tx_id, now, chore_type, action, details,
                json.dumps(before_state), json.dumps(after_state),
                1 if is_dry_run else 0,
                impact_metric, impact_value
            ))
            conn.commit()

        return {
            "id": tx_id,
            "timestamp": now,
            "chore_type": chore_type,
            "action": action,
            "details": details,
            "status": "completed",
            "is_dry_run": is_dry_run,
            "impact_metric": impact_metric,
            "impact_value": impact_value
        }

    def rollback(self, tx_id: str) -> dict:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": f"Transaction {tx_id} not found"}
            
            if row["status"] == "rolled_back":
                return {"success": False, "error": f"Transaction {tx_id} has already been rolled back"}

            chore_type = row["chore_type"]
            action = row["action"]
            before_state = json.loads(row["before_state"])
            after_state = json.loads(row["after_state"])
            is_dry_run = bool(row["is_dry_run"])

            rollback_success = True
            rollback_msg = "Successfully rolled back"

            if not is_dry_run:
                try:
                    if chore_type == "file_organization":
                        if action == "move_file":
                            current_path = Path(after_state.get("dest_path", ""))
                            orig_path = Path(before_state.get("src_path", ""))
                            if current_path.exists():
                                orig_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.move(str(current_path), str(orig_path))
                                rollback_msg = f"Restored file to {orig_path}"
                            else:
                                rollback_success = False
                                rollback_msg = f"File {current_path} no longer exists"

                        elif action == "quarantine_duplicate":
                            quarantine_path = Path(after_state.get("quarantine_path", ""))
                            orig_path = Path(before_state.get("orig_path", ""))
                            if quarantine_path.exists():
                                orig_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.move(str(quarantine_path), str(orig_path))
                                rollback_msg = f"Restored duplicate from quarantine to {orig_path}"
                            else:
                                rollback_success = False
                                rollback_msg = "Quarantined file not found"

                    elif chore_type == "code_debugging":
                        file_path = Path(after_state.get("file_path", ""))
                        orig_code = before_state.get("original_code")
                        if file_path.exists() and orig_code is not None:
                            file_path.write_text(orig_code, encoding="utf-8")
                            rollback_msg = f"Restored original code in {file_path.name}"
                        else:
                            rollback_success = False
                            rollback_msg = "Code file or backup missing"

                    # Email and expense state rollbacks are handled via state update
                except Exception as e:
                    rollback_success = False
                    rollback_msg = f"Rollback failed: {str(e)}"

            if rollback_success:
                cursor.execute("UPDATE transactions SET status = 'rolled_back' WHERE id = ?", (tx_id,))
                conn.commit()

            return {
                "success": rollback_success,
                "message": rollback_msg,
                "tx_id": tx_id,
                "chore_type": chore_type,
                "before_state": before_state
            }

    def get_history(self, limit: int = 50, chore_type: str = None) -> list:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if chore_type:
                cursor.execute("SELECT * FROM transactions WHERE chore_type = ? ORDER BY timestamp DESC LIMIT ?", (chore_type, limit))
            else:
                cursor.execute("SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_metrics_summary(self) -> dict:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                COUNT(*) as total_actions,
                SUM(CASE WHEN chore_type = 'file_organization' AND status = 'completed' THEN 1 ELSE 0 END) as files_organized,
                SUM(CASE WHEN chore_type = 'file_organization' AND impact_metric = 'bytes_freed' AND status = 'completed' THEN impact_value ELSE 0 END) as bytes_saved,
                SUM(CASE WHEN chore_type = 'email_cleanup' AND status = 'completed' THEN 1 ELSE 0 END) as emails_cleaned,
                SUM(CASE WHEN chore_type = 'expense_tracking' AND status = 'completed' THEN 1 ELSE 0 END) as expenses_reviewed,
                SUM(CASE WHEN chore_type = 'expense_tracking' AND impact_metric = 'money_saved' AND status = 'completed' THEN impact_value ELSE 0 END) as money_saved,
                SUM(CASE WHEN chore_type = 'code_debugging' AND status = 'completed' THEN 1 ELSE 0 END) as bugs_fixed
            FROM transactions
            """)
            row = cursor.fetchone()
            return {
                "total_actions": row["total_actions"] or 0,
                "files_organized": row["files_organized"] or 0,
                "bytes_saved": row["bytes_saved"] or 0,
                "emails_cleaned": row["emails_cleaned"] or 0,
                "expenses_reviewed": row["expenses_reviewed"] or 0,
                "money_saved": row["money_saved"] or 0.0,
                "bugs_fixed": row["bugs_fixed"] or 0
            }
