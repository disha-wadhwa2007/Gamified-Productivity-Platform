import os
import sys
import json
import logging
from pathlib import Path

# Ensure Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import tornado.ioloop
import tornado.web
import tornado.websocket

from chore_engine.transaction_manager import TransactionManager
from chore_engine.file_engine import FileEngine
from chore_engine.email_engine import EmailEngine
from chore_engine.expense_engine import ExpenseEngine
from chore_engine.code_engine import CodeEngine
from chore_engine.gamification_engine import GamificationEngine
from chore_engine.story_engine import StoryEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATE_DIR = BASE_DIR / "templates"

# Global state & instances
tx_mgr = TransactionManager(db_path=str(BASE_DIR / "chorequest.db"))
file_engine = FileEngine(transaction_mgr=tx_mgr)
email_engine = EmailEngine(db_path=str(BASE_DIR / "chorequest.db"), transaction_mgr=tx_mgr)
expense_engine = ExpenseEngine(db_path=str(BASE_DIR / "chorequest.db"), transaction_mgr=tx_mgr)
code_engine = CodeEngine(transaction_mgr=tx_mgr)
game_engine = GamificationEngine(db_path=str(BASE_DIR / "chorequest.db"))
story_engine = StoryEngine(db_path=str(BASE_DIR / "chorequest.db"))

is_dry_run = False
ws_clients = set()

def broadcast_event(event_type: str, data: dict):
    payload = json.dumps({"event": event_type, "data": data})
    for client in list(ws_clients):
        try:
            client.write_message(payload)
        except Exception:
            ws_clients.discard(client)

class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def options(self):
        self.set_status(204)
        self.finish()

    def get_json_body(self):
        try:
            return json.loads(self.request.body.decode("utf-8"))
        except Exception:
            return {}

class MainHandler(BaseHandler):
    def get(self):
        self.render(str(TEMPLATE_DIR / "index.html"))

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        ws_clients.add(self)
        logging.info("WebSocket client connected. Total: %d", len(ws_clients))
        self.write_message(json.dumps({
            "event": "connected",
            "data": {"message": "Connected to ChoreQuest Real-Time Engine"}
        }))

    def on_close(self):
        ws_clients.discard(self)
        logging.info("WebSocket client disconnected. Total: %d", len(ws_clients))

# --- API HANDLERS ---

class StatusHandler(BaseHandler):
    def get(self):
        profile = game_engine.get_profile()
        metrics = tx_mgr.get_metrics_summary()
        campaign = story_engine.get_campaign_status()
        self.write({
            "dry_run": is_dry_run,
            "profile": profile,
            "metrics": metrics,
            "campaign": campaign
        })

class DryRunToggleHandler(BaseHandler):
    def post(self):
        global is_dry_run
        data = self.get_json_body()
        is_dry_run = bool(data.get("dry_run", not is_dry_run))
        broadcast_event("dry_run_toggled", {"dry_run": is_dry_run})
        self.write({"success": True, "dry_run": is_dry_run})

class TransactionsHandler(BaseHandler):
    def get(self):
        limit = int(self.get_argument("limit", 50))
        chore_type = self.get_argument("chore_type", None)
        txs = tx_mgr.get_history(limit=limit, chore_type=chore_type)
        summary = tx_mgr.get_metrics_summary()
        self.write({"transactions": txs, "summary": summary})

class RollbackHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        tx_id = data.get("tx_id")
        if not tx_id:
            self.set_status(400)
            self.write({"success": False, "error": "Missing tx_id"})
            return
        result = tx_mgr.rollback(tx_id)
        broadcast_event("transaction_rolled_back", result)
        self.write(result)

# File Handlers
class FileScanHandler(BaseHandler):
    def get(self):
        scan_res = file_engine.scan_directory()
        self.write(scan_res)

class FileOrganizeHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        filename = data.get("filename")
        category = data.get("category")
        res = file_engine.organize_file(filename, category, dry_run=is_dry_run)
        if res.get("success"):
            xp_res = game_engine.award_xp_and_gold(xp_amount=25, gold_amount=10, chore_type="file_organization")
            res["gamification"] = xp_res
            broadcast_event("file_organized", res)
        self.write(res)

class FileQuarantineDuplicateHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        filename = data.get("filename")
        res = file_engine.quarantine_duplicate(filename, dry_run=is_dry_run)
        if res.get("success"):
            xp_res = game_engine.award_xp_and_gold(xp_amount=40, gold_amount=15, chore_type="file_organization")
            res["gamification"] = xp_res
            broadcast_event("duplicate_quarantined", res)
        self.write(res)

class FileResetSamplesHandler(BaseHandler):
    def post(self):
        count = file_engine.generate_sample_messy_files()
        scan_res = file_engine.scan_directory()
        broadcast_event("files_refreshed", scan_res)
        self.write({"success": True, "created": count, "scan": scan_res})

class FileSetDirHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        path = data.get("directory")
        success, msg = file_engine.set_target_directory(path)
        if success:
            scan_res = file_engine.scan_directory()
            self.write({"success": True, "message": msg, "scan": scan_res})
        else:
            self.set_status(400)
            self.write({"success": False, "error": msg})

# Email Handlers
class EmailInboxHandler(BaseHandler):
    def get(self):
        inbox = email_engine.get_inbox()
        stats = email_engine.get_stats()
        self.write({"emails": inbox, "stats": stats})

class EmailActionHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        email_id = data.get("email_id")
        action = data.get("action", "trash")
        res = email_engine.process_email_action(email_id, action, dry_run=is_dry_run)
        if res.get("success"):
            xp_amount = 30 if action in ["blast", "trash"] else (40 if action == "star" else 20)
            xp_res = game_engine.award_xp_and_gold(xp_amount=xp_amount, gold_amount=10, chore_type="email_cleanup")
            res["gamification"] = xp_res
            broadcast_event("email_action", res)
        self.write(res)

class EmailResetHandler(BaseHandler):
    def post(self):
        email_engine.reset_mailbox()
        inbox = email_engine.get_inbox()
        stats = email_engine.get_stats()
        broadcast_event("email_reset", {"stats": stats})
        self.write({"success": True, "emails": inbox, "stats": stats})

# Expense Handlers
class ExpenseListHandler(BaseHandler):
    def get(self):
        filter_type = self.get_argument("filter", None)
        expenses = expense_engine.get_expenses(filter_type=filter_type)
        analytics = expense_engine.get_analytics()
        self.write({"expenses": expenses, "analytics": analytics})

class ExpenseCategorizeHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        exp_id = data.get("expense_id")
        category = data.get("category")
        res = expense_engine.categorize_expense(exp_id, category, dry_run=is_dry_run)
        if res.get("success"):
            xp_res = game_engine.award_xp_and_gold(xp_amount=25, gold_amount=10, chore_type="expense_tracking")
            res["gamification"] = xp_res
            broadcast_event("expense_categorized", res)
        self.write(res)

class ExpenseSlayVampireHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        exp_id = data.get("expense_id")
        res = expense_engine.vanquish_vampire_subscription(exp_id, dry_run=is_dry_run)
        if res.get("success"):
            xp_res = game_engine.award_xp_and_gold(xp_amount=60, gold_amount=30, chore_type="expense_tracking")
            res["gamification"] = xp_res
            broadcast_event("vampire_slayed", res)
        self.write(res)

class ExpenseExportHandler(BaseHandler):
    def get(self):
        res = expense_engine.export_ledger()
        self.write(res)

class ExpenseResetHandler(BaseHandler):
    def post(self):
        expense_engine.reset_expenses()
        expenses = expense_engine.get_expenses()
        analytics = expense_engine.get_analytics()
        broadcast_event("expenses_reset", {})
        self.write({"success": True, "expenses": expenses, "analytics": analytics})

# Code Debugging Handlers
class CodeChallengesHandler(BaseHandler):
    def get(self):
        challenges = code_engine.get_challenges()
        self.write({"challenges": challenges})

class CodePatchHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        ch_id = data.get("challenge_id")
        opt_id = data.get("option_id")
        res = code_engine.patch_code(ch_id, opt_id, dry_run=is_dry_run)
        if res.get("success") and res.get("is_correct"):
            xp_res = game_engine.award_xp_and_gold(xp_amount=75, gold_amount=40, chore_type="code_debugging")
            res["gamification"] = xp_res
            broadcast_event("code_patched", res)
        else:
            game_engine.reset_combo()
        self.write(res)

# Gamification & Skills
class UnlockSkillHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        skill_id = data.get("skill_id")
        res = game_engine.unlock_skill(skill_id)
        if res.get("success"):
            broadcast_event("skill_unlocked", res)
        self.write(res)

# Story Mode Handlers
class StoryCampaignHandler(BaseHandler):
    def get(self):
        campaign = story_engine.get_campaign_status()
        self.write({"campaign": campaign})

class StoryCompleteChapterHandler(BaseHandler):
    def post(self):
        data = self.get_json_body()
        chap_id = data.get("chapter_id")
        stars = int(data.get("stars", 3))
        res = story_engine.complete_chapter(chap_id, stars)
        xp_res = game_engine.award_xp_and_gold(xp_amount=150, gold_amount=80)
        res["gamification"] = xp_res
        broadcast_event("chapter_completed", res)
        self.write(res)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/ws", WebSocketHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": str(STATIC_DIR)}),
        
        # Status & Controls
        (r"/api/status", StatusHandler),
        (r"/api/settings/dry-run", DryRunToggleHandler),
        (r"/api/transactions", TransactionsHandler),
        (r"/api/transactions/rollback", RollbackHandler),
        
        # Files
        (r"/api/files/scan", FileScanHandler),
        (r"/api/files/organize", FileOrganizeHandler),
        (r"/api/files/quarantine-duplicate", FileQuarantineDuplicateHandler),
        (r"/api/files/reset-samples", FileResetSamplesHandler),
        (r"/api/files/set-directory", FileSetDirHandler),
        
        # Email
        (r"/api/email/inbox", EmailInboxHandler),
        (r"/api/email/action", EmailActionHandler),
        (r"/api/email/reset", EmailResetHandler),
        
        # Expense
        (r"/api/expense/list", ExpenseListHandler),
        (r"/api/expense/categorize", ExpenseCategorizeHandler),
        (r"/api/expense/slay-vampire", ExpenseSlayVampireHandler),
        (r"/api/expense/export", ExpenseExportHandler),
        (r"/api/expense/reset", ExpenseResetHandler),
        
        # Code
        (r"/api/code/challenges", CodeChallengesHandler),
        (r"/api/code/patch", CodePatchHandler),
        
        # Gamification & Story
        (r"/api/gamification/unlock-skill", UnlockSkillHandler),
        (r"/api/story/campaign", StoryCampaignHandler),
        (r"/api/story/complete-chapter", StoryCompleteChapterHandler),
    ], template_path=str(TEMPLATE_DIR), debug=False)

if __name__ == "__main__":
    # Populate initial sample files
    file_engine.generate_sample_messy_files()
    port = int(os.environ.get("PORT", 8765))
    app = make_app()
    app.listen(port, address="127.0.0.1")
    logging.info("==================================================")
    logging.info(" ChoreQuest Gamified Productivity Platform Online ")
    logging.info(" URL: http://127.0.0.1:%d", port)
    logging.info("==================================================")
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        logging.info("ChoreQuest Server Stopped.")
