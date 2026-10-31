import json
import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from chore_engine.transaction_manager import TransactionManager

INITIAL_EXPENSES = [
    {
        "id": "EXP-101",
        "merchant": "AWS Cloud Services",
        "amount": 142.50,
        "date": "2026-10-28",
        "raw_category": "Uncategorized",
        "correct_category": "Infrastructure & Hosting",
        "is_recurring": True,
        "is_tax_deductible": True,
        "monster_name": "Cloud Behemoth",
        "monster_hp": 60,
        "is_vampire": False,
        "note": "Production cluster & RDS database instance"
    },
    {
        "id": "EXP-102",
        "merchant": "Forgotten Streaming Pass",
        "amount": 19.99,
        "date": "2026-10-25",
        "raw_category": "Entertainment",
        "correct_category": "Personal Entertainment",
        "is_recurring": True,
        "is_tax_deductible": False,
        "monster_name": "Blood-Sucking Vampire Sub",
        "monster_hp": 35,
        "is_vampire": True,
        "note": "Zero logins in 90 days! Monthly leech draining gold"
    },
    {
        "id": "EXP-103",
        "merchant": "Blue Bottle Artisanal Espresso",
        "amount": 8.75,
        "date": "2026-10-30",
        "raw_category": "Uncategorized",
        "correct_category": "Meals & Nourishment",
        "is_recurring": False,
        "is_tax_deductible": False,
        "monster_name": "Caffeine Sprite",
        "monster_hp": 20,
        "is_vampire": False,
        "note": "Double oat latte during morning sprint"
    },
    {
        "id": "EXP-104",
        "merchant": "GitHub Enterprise & Copilot",
        "amount": 29.00,
        "date": "2026-10-15",
        "raw_category": "Software",
        "correct_category": "Developer Tooling",
        "is_recurring": True,
        "is_tax_deductible": True,
        "monster_name": "Octo-Golem",
        "monster_hp": 45,
        "is_vampire": False,
        "note": "Primary code repo & AI assistant suite"
    },
    {
        "id": "EXP-105",
        "merchant": "Unused Design Mockup Pro Sub",
        "amount": 48.00,
        "date": "2026-10-12",
        "raw_category": "Uncategorized",
        "correct_category": "Software & SaaS",
        "is_recurring": True,
        "is_tax_deductible": True,
        "monster_name": "Zombie SaaS Parasite",
        "monster_hp": 55,
        "is_vampire": True,
        "note": "Billed monthly since March, no active team members"
    },
    {
        "id": "EXP-106",
        "merchant": "Mechanical Keyboard Switch Kit",
        "amount": 89.50,
        "date": "2026-10-08",
        "raw_category": "Office",
        "correct_category": "Hardware & Ergonomics",
        "is_recurring": False,
        "is_tax_deductible": True,
        "monster_name": "Tactile Mechanical Wyrm",
        "monster_hp": 40,
        "is_vampire": False,
        "note": "Ergonomic keyboard maintenance equipment"
    },
    {
        "id": "EXP-107",
        "merchant": "Domain Registrar (12 Unused .io Domains)",
        "amount": 264.00,
        "date": "2026-10-02",
        "raw_category": "Hosting",
        "correct_category": "Infrastructure & Hosting",
        "is_recurring": True,
        "is_tax_deductible": True,
        "monster_name": "Graveyard Domain Hydra",
        "monster_hp": 70,
        "is_vampire": True,
        "note": "Abandoned side projects renewed automatically"
    },
    {
        "id": "EXP-108",
        "merchant": "City Metro Rail Monthly Pass",
        "amount": 75.00,
        "date": "2026-10-01",
        "raw_category": "Transit",
        "correct_category": "Travel & Commute",
        "is_recurring": True,
        "is_tax_deductible": True,
        "monster_name": "Iron Transit Engine",
        "monster_hp": 30,
        "is_vampire": False,
        "note": "Commute to engineering hub"
    }
]

EXPENSE_CATEGORIES = [
    "Developer Tooling",
    "Infrastructure & Hosting",
    "Software & SaaS",
    "Meals & Nourishment",
    "Hardware & Ergonomics",
    "Travel & Commute",
    "Personal Entertainment",
    "Tax-Deductible Guild Expenses"
]

class ExpenseEngine:
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
            CREATE TABLE IF NOT EXISTS expenses (
                id TEXT PRIMARY KEY,
                merchant TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                is_categorized INTEGER NOT NULL DEFAULT 0,
                is_recurring INTEGER NOT NULL DEFAULT 0,
                is_tax_deductible INTEGER NOT NULL DEFAULT 0,
                monster_name TEXT NOT NULL,
                monster_hp INTEGER NOT NULL,
                is_vampire INTEGER NOT NULL DEFAULT 0,
                is_cancelled INTEGER NOT NULL DEFAULT 0,
                note TEXT
            )
            """)
            conn.commit()

            cursor.execute("SELECT COUNT(*) as count FROM expenses")
            if cursor.fetchone()["count"] == 0:
                self.reset_expenses()

    def reset_expenses(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses")
            for item in INITIAL_EXPENSES:
                cursor.execute("""
                INSERT INTO expenses (id, merchant, amount, date, category, is_categorized, is_recurring, is_tax_deductible, monster_name, monster_hp, is_vampire, is_cancelled, note)
                VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, 0, ?)
                """, (
                    item["id"], item["merchant"], item["amount"], item["date"],
                    item["raw_category"], 1 if item["is_recurring"] else 0,
                    1 if item["is_tax_deductible"] else 0, item["monster_name"],
                    item["monster_hp"], 1 if item["is_vampire"] else 0, item["note"]
                ))
            conn.commit()

    def get_expenses(self, filter_type=None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if filter_type == "uncategorized":
                cursor.execute("SELECT * FROM expenses WHERE is_categorized = 0 AND is_cancelled = 0 ORDER BY amount DESC")
            elif filter_type == "vampires":
                cursor.execute("SELECT * FROM expenses WHERE is_vampire = 1 AND is_cancelled = 0 ORDER BY amount DESC")
            else:
                cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_analytics(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                COUNT(*) as total_count,
                SUM(amount) as total_amount,
                SUM(CASE WHEN is_categorized = 1 THEN 1 ELSE 0 END) as categorized_count,
                SUM(CASE WHEN is_vampire = 1 AND is_cancelled = 1 THEN amount ELSE 0 END) as saved_monthly,
                SUM(CASE WHEN is_vampire = 1 AND is_cancelled = 0 THEN amount ELSE 0 END) as active_vampire_burn,
                SUM(CASE WHEN is_tax_deductible = 1 THEN amount ELSE 0 END) as tax_deductible_sum
            FROM expenses
            WHERE is_cancelled = 0 OR is_vampire = 1
            """)
            summary = dict(cursor.fetchone())

            # Category breakdown
            cursor.execute("""
            SELECT category, SUM(amount) as total, COUNT(*) as count 
            FROM expenses 
            WHERE is_cancelled = 0 
            GROUP BY category
            """)
            breakdown = [dict(r) for r in cursor.fetchall()]

            return {
                "summary": summary,
                "breakdown": breakdown,
                "categories": EXPENSE_CATEGORIES
            }

    def categorize_expense(self, expense_id: str, new_category: str, dry_run: bool = False) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": f"Expense {expense_id} not found"}

            before_state = {"id": expense_id, "category": row["category"], "is_categorized": row["is_categorized"]}
            after_state = {"id": expense_id, "category": new_category, "is_categorized": 1}

            if not dry_run:
                cursor.execute("UPDATE expenses SET category = ?, is_categorized = 1 WHERE id = ?", (new_category, expense_id))
                conn.commit()

            tx = self.tx_mgr.record(
                chore_type="expense_tracking",
                action="categorize_expense",
                details=f"Classified ${row['amount']:.2f} at {row['merchant']} -> '{new_category}'",
                before_state=before_state,
                after_state=after_state,
                is_dry_run=dry_run,
                impact_metric="expenses_categorized",
                impact_value=1
            )

            return {"success": True, "expense_id": expense_id, "category": new_category, "transaction": tx}

    def vanquish_vampire_subscription(self, expense_id: str, dry_run: bool = False) -> Dict[str, Any]:
        """Slashes an unused recurring subscription, saving real recurring money."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": f"Expense {expense_id} not found"}

            monthly_saved = row["amount"]
            yearly_saved = monthly_saved * 12

            before_state = {"id": expense_id, "is_cancelled": row["is_cancelled"]}
            after_state = {"id": expense_id, "is_cancelled": 1}

            if not dry_run:
                cursor.execute("UPDATE expenses SET is_cancelled = 1 WHERE id = ?", (expense_id,))
                conn.commit()

            tx = self.tx_mgr.record(
                chore_type="expense_tracking",
                action="cancel_vampire_subscription",
                details=f"Slashed Vampire Subscription '{row['merchant']}'! Saved ${monthly_saved:.2f}/mo (${yearly_saved:.2f}/yr)",
                before_state=before_state,
                after_state=after_state,
                is_dry_run=dry_run,
                impact_metric="money_saved",
                impact_value=monthly_saved
            )

            return {
                "success": True,
                "merchant": row["merchant"],
                "monthly_saved": monthly_saved,
                "yearly_saved": yearly_saved,
                "transaction": tx
            }

    def export_ledger(self, export_dir: str = None) -> Dict[str, str]:
        """Exports the clean expense ledger to both CSV and Excel."""
        out_dir = Path(export_dir) if export_dir else Path(__file__).resolve().parent.parent / "sample_data" / "receipts"
        out_dir.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            df = pd.read_sql_query("SELECT id, date, merchant, amount, category, is_recurring, is_tax_deductible, is_cancelled, note FROM expenses", conn)

        df["is_recurring"] = df["is_recurring"].apply(lambda x: "Yes" if x else "No")
        df["is_tax_deductible"] = df["is_tax_deductible"].apply(lambda x: "Yes" if x else "No")
        df["status"] = df["is_cancelled"].apply(lambda x: "Vampire Cancelled (Saved!)" if x else "Active")

        csv_path = out_dir / "ChoreQuest_Expense_Ledger.csv"
        xlsx_path = out_dir / "ChoreQuest_Expense_Ledger.xlsx"

        df.to_csv(csv_path, index=False)
        df.to_excel(xlsx_path, index=False, engine="openpyxl")

        return {
            "csv_path": str(csv_path),
            "xlsx_path": str(xlsx_path),
            "row_count": len(df)
        }
