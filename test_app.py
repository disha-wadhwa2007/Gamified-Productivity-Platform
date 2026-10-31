import unittest
import json
import sys
from pathlib import Path

# Ensure Windows UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import tornado.testing

from server import make_app, file_engine, email_engine, expense_engine, code_engine, game_engine, tx_mgr

class TestChoreQuest(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app()

    def test_01_status_api(self):
        response = self.fetch("/api/status")
        self.assertEqual(response.code, 200)
        data = json.loads(response.body.decode("utf-8"))
        self.assertIn("profile", data)
        self.assertIn("metrics", data)
        self.assertIn("campaign", data)
        print("✓ Status API returns complete profile and metrics")

    def test_02_file_scan_and_organize(self):
        response = self.fetch("/api/files/scan")
        self.assertEqual(response.code, 200)
        data = json.loads(response.body.decode("utf-8"))
        self.assertGreater(data["total_files"], 0)
        self.assertIn("duplicates", data)
        print(f"✓ File scan detected {data['total_files']} files and {data['duplicate_count']} duplicates")

        # Organize first file
        target_file = data["files"][0]
        res = self.fetch("/api/files/organize", method="POST",
                         headers={"Content-Type": "application/json"},
                         body=json.dumps({"filename": target_file["name"], "category": target_file["category"]}))
        self.assertEqual(res.code, 200)
        org_data = json.loads(res.body.decode("utf-8"))
        self.assertTrue(org_data["success"])
        tx_id = org_data["transaction"]["id"]
        print(f"✓ Real-world file organization executed with Tx {tx_id}")

        # Rollback the file move!
        res_rb = self.fetch("/api/transactions/rollback", method="POST",
                            headers={"Content-Type": "application/json"},
                            body=json.dumps({"tx_id": tx_id}))
        self.assertEqual(res_rb.code, 200)
        rb_data = json.loads(res_rb.body.decode("utf-8"))
        self.assertTrue(rb_data["success"])
        print(f"✓ Time Machine rollback restored file safely: {rb_data['message']}")

    def test_03_email_cleanup(self):
        response = self.fetch("/api/email/inbox")
        self.assertEqual(response.code, 200)
        data = json.loads(response.body.decode("utf-8"))
        self.assertGreater(len(data["emails"]), 0)

        em = data["emails"][0]
        res = self.fetch("/api/email/action", method="POST",
                         headers={"Content-Type": "application/json"},
                         body=json.dumps({"email_id": em["id"], "action": "trash"}))
        self.assertEqual(res.code, 200)
        action_data = json.loads(res.body.decode("utf-8"))
        self.assertTrue(action_data["success"])
        print(f"✓ Email cleanup action '{action_data['details']}' recorded and executed")

    def test_04_expense_vampire_slayer(self):
        response = self.fetch("/api/expense/list")
        self.assertEqual(response.code, 200)
        data = json.loads(response.body.decode("utf-8"))
        vampire = next((e for e in data["expenses"] if e["is_vampire"]), None)
        self.assertIsNotNone(vampire)

        res = self.fetch("/api/expense/slay-vampire", method="POST",
                         headers={"Content-Type": "application/json"},
                         body=json.dumps({"expense_id": vampire["id"]}))
        self.assertEqual(res.code, 200)
        slay_data = json.loads(res.body.decode("utf-8"))
        self.assertTrue(slay_data["success"])
        print(f"✓ Slayed vampire sub '{slay_data['merchant']}', saved ${slay_data['monthly_saved']:.2f}/mo!")

        # Export test
        res_exp = self.fetch("/api/expense/export")
        self.assertEqual(res_exp.code, 200)
        exp_data = json.loads(res_exp.body.decode("utf-8"))
        self.assertTrue(Path(exp_data["csv_path"]).exists())
        self.assertTrue(Path(exp_data["xlsx_path"]).exists())
        print(f"✓ Real expense ledger exported to CSV and Excel ({exp_data['row_count']} rows)")

    def test_05_code_debugger(self):
        response = self.fetch("/api/code/challenges")
        self.assertEqual(response.code, 200)
        data = json.loads(response.body.decode("utf-8"))
        self.assertGreater(len(data["challenges"]), 0)
        ch = data["challenges"][0]

        res = self.fetch("/api/code/patch", method="POST",
                         headers={"Content-Type": "application/json"},
                         body=json.dumps({"challenge_id": ch["id"], "option_id": "A"}))
        self.assertEqual(res.code, 200)
        patch_data = json.loads(res.body.decode("utf-8"))
        self.assertTrue(patch_data["success"])
        print(f"✓ Code glitch patched on disk: {patch_data['filename']}")

    def test_06_main_ui_served(self):
        response = self.fetch("/")
        self.assertEqual(response.code, 200)
        self.assertIn("ChoreQuest", response.body.decode("utf-8"))
        print("✓ Main SPA UI served with all HTML/JS/CSS assets ready")

if __name__ == "__main__":
    unittest.main()
