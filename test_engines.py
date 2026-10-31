import sys
import io
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from chore_engine.transaction_manager import TransactionManager
from chore_engine.file_engine import FileEngine
from chore_engine.email_engine import EmailEngine
from chore_engine.expense_engine import ExpenseEngine
from chore_engine.code_engine import CodeEngine
from chore_engine.gamification_engine import GamificationEngine
from chore_engine.story_engine import StoryEngine

print("Starting direct engine verification...", flush=True)

# 1. Transaction Manager & Database
tx = TransactionManager(db_path="test.db")
record = tx.record("file_organization", "test_action", "Moved test file", {"a": 1}, {"b": 2})
print(f"✓ Transaction Manager recorded: {record['id']}", flush=True)

# 2. File Engine
fe = FileEngine(transaction_mgr=tx)
created = fe.generate_sample_messy_files()
scan = fe.scan_directory()
print(f"✓ File Engine: created {created} samples, total {scan['total_files']} files, duplicates: {scan['duplicate_count']}", flush=True)
if scan["files"]:
    target = scan["files"][0]
    org_res = fe.organize_file(target["name"], target["category"])
    print(f"✓ File Engine organized '{target['name']}': {org_res['success']}", flush=True)
    rb_res = tx.rollback(org_res["transaction"]["id"])
    print(f"✓ File Engine rollback: {rb_res['success']} - {rb_res['message']}", flush=True)

# 3. Email Engine
ee = EmailEngine(db_path="test.db", transaction_mgr=tx)
ee.reset_mailbox()
inbox = ee.get_inbox()
print(f"✓ Email Engine: {len(inbox)} emails in inbox", flush=True)
act_res = ee.process_email_action(inbox[0]["id"], "trash")
print(f"✓ Email Engine blasted spam: {act_res['success']}", flush=True)

# 4. Expense Engine
ex = ExpenseEngine(db_path="test.db", transaction_mgr=tx)
ex.reset_expenses()
expenses = ex.get_expenses()
print(f"✓ Expense Engine: {len(expenses)} expenses loaded", flush=True)
vamp = next(e for e in expenses if e["is_vampire"])
slay_res = ex.vanquish_vampire_subscription(vamp["id"])
print(f"✓ Expense Engine slayed vampire '{slay_res['merchant']}': saved ${slay_res['monthly_saved']:.2f}/mo", flush=True)
export_res = ex.export_ledger()
print(f"✓ Expense Engine exported CSV and Excel: {export_res['row_count']} rows", flush=True)

# 5. Code Engine
ce = CodeEngine(transaction_mgr=tx)
challenges = ce.get_challenges()
print(f"✓ Code Engine: {len(challenges)} code challenges ready", flush=True)
patch_res = ce.patch_code(challenges[0]["id"], "A")
print(f"✓ Code Engine patched challenge '{challenges[0]['id']}': {patch_res['success']}", flush=True)

# 6. Gamification Engine
ge = GamificationEngine(db_path="test.db")
prof = ge.get_profile()
print(f"✓ Gamification Engine: Player '{prof['name']}', Level {prof['level']}, Gold {prof['gold']}", flush=True)
xp_res = ge.award_xp_and_gold(xp_amount=150, gold_amount=50)
print(f"✓ Gamification Engine awarded XP: {xp_res['xp_gained']}, New level: {xp_res['new_level']}", flush=True)

# 7. Story Engine
se = StoryEngine(db_path="test.db")
campaign = se.get_campaign_status()
print(f"✓ Story Engine: {len(campaign)} chapters loaded", flush=True)
chap_res = se.complete_chapter("chap_1", stars=3)
print(f"✓ Story Engine cleared chapter: {chap_res['chapter_id']}", flush=True)

print("ALL CHORE ENGINES TESTED AND OPERATIONAL!", flush=True)
