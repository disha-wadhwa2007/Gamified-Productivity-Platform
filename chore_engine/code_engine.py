import os
import ast
import difflib
from pathlib import Path
from typing import List, Dict, Any
from chore_engine.transaction_manager import TransactionManager

CODE_CHALLENGES = [
    {
        "id": "BUG-01",
        "title": "The Infinite Loop Phantom",
        "language": "python",
        "filename": "retry_handler.py",
        "bug_type": "Infinite Loop & Unbounded Recursion",
        "difficulty": "Novice",
        "monster_name": "Recursion Wraith",
        "monster_hp": 40,
        "buggy_code": """def fetch_with_retry(api_client, endpoint, max_attempts=5):
    attempt = 0
    while attempt < max_attempts:
        response = api_client.call(endpoint)
        if response.status_code == 200:
            return response.data
        # BUG: Counter never increments! Causes infinite CPU freeze!
    return None
""",
        "fixed_code": """def fetch_with_retry(api_client, endpoint, max_attempts=5):
    attempt = 0
    while attempt < max_attempts:
        response = api_client.call(endpoint)
        if response.status_code == 200:
            return response.data
        attempt += 1  # Fixed: Increment counter each attempt
    return None
""",
        "options": [
            {"id": "A", "label": "Add 'attempt += 1' inside the loop", "correct": True, "explanation": "Increments retry count on each failed attempt, preventing indefinite CPU lock."},
            {"id": "B", "label": "Change '< max_attempts' to '> max_attempts'", "correct": False, "explanation": "Inverts condition, so the loop would never execute at all."},
            {"id": "C", "label": "Delete the while loop entirely", "correct": False, "explanation": "Removes retry capability completely."}
        ]
    },
    {
        "id": "BUG-02",
        "title": "The Null Pointer Hydra",
        "language": "javascript",
        "filename": "user_profile_loader.js",
        "bug_type": "Uncaught TypeError: Cannot read property of undefined",
        "difficulty": "Adept",
        "monster_name": "Null Void Sentinel",
        "monster_hp": 50,
        "buggy_code": """function renderUserCard(user) {
    // BUG: Crashes when user.settings is null or undefined!
    const theme = user.settings.preferences.theme;
    const avatarUrl = user.profile.avatarUrl;
    return `<div class="card ${theme}"><img src="${avatarUrl}"/></div>`;
}
""",
        "fixed_code": """function renderUserCard(user) {
    // Fixed: Optional chaining & default fallbacks
    const theme = user?.settings?.preferences?.theme ?? 'dark';
    const avatarUrl = user?.profile?.avatarUrl ?? '/default-avatar.png';
    return `<div class="card ${theme}"><img src="${avatarUrl}"/></div>`;
}
""",
        "options": [
            {"id": "A", "label": "Use optional chaining '?.' with nullish coalescing '??'", "correct": True, "explanation": "Safely navigates nested properties without throwing TypeError if an intermediate node is null/undefined."},
            {"id": "B", "label": "Wrap the whole function in an empty try/catch ignoring errors", "correct": False, "explanation": "Swallows errors silently without rendering the user interface properly."},
            {"id": "C", "label": "Convert user to a string before reading", "correct": False, "explanation": "Strings don't have user.settings, which makes the problem worse."}
        ]
    },
    {
        "id": "BUG-03",
        "title": "The Zero Division Specter",
        "language": "python",
        "filename": "metrics_calculator.py",
        "bug_type": "ZeroDivisionError in KPI Engine",
        "difficulty": "Adept",
        "monster_name": "Divide-by-Zero Singularity",
        "monster_hp": 60,
        "buggy_code": """def calculate_conversion_rate(clicks, conversions):
    # BUG: When clicks is 0, throws ZeroDivisionError!
    rate = (conversions / clicks) * 100.0
    return round(rate, 2)
""",
        "fixed_code": """def calculate_conversion_rate(clicks, conversions):
    # Fixed: Guard against zero denominator
    if not clicks or clicks <= 0:
        return 0.0
    rate = (conversions / clicks) * 100.0
    return round(rate, 2)
""",
        "options": [
            {"id": "A", "label": "Add guard condition: return 0.0 if not clicks or clicks <= 0", "correct": True, "explanation": "Guarantees safe division and handles zero impressions gracefully."},
            {"id": "B", "label": "Divide by (clicks + 1) everywhere", "correct": False, "explanation": "Artificially skews conversion math for non-zero clicks."},
            {"id": "C", "label": "Set rate = clicks / conversions instead", "correct": False, "explanation": "Inverts formula, calculating clicks per conversion instead of rate."}
        ]
    },
    {
        "id": "BUG-04",
        "title": "The SQL Injection Goblin",
        "language": "sql",
        "filename": "auth_query.py",
        "bug_type": "Critical Security Vulnerability: SQL Injection",
        "difficulty": "Master",
        "monster_name": "Tainted Query Overlord",
        "monster_hp": 80,
        "buggy_code": """def authenticate_user(db_cursor, username, password_hash):
    # CRITICAL BUG: Raw f-string interpolation invites ' OR 1=1 -- exploit!
    query = f"SELECT id, role FROM users WHERE username = '{username}' AND password = '{password_hash}'"
    db_cursor.execute(query)
    return db_cursor.fetchone()
""",
        "fixed_code": """def authenticate_user(db_cursor, username, password_hash):
    # Fixed: Parameterized query prevents injection
    query = "SELECT id, role FROM users WHERE username = ? AND password = ?"
    db_cursor.execute(query, (username, password_hash))
    return db_cursor.fetchone()
""",
        "options": [
            {"id": "A", "label": "Use parameterized queries with '?' placeholders and parameter tuple", "correct": True, "explanation": "Ensures user input is escaped by database driver, neutralizing SQL injection vectors."},
            {"id": "B", "label": "Strip single quotes using username.replace(\"'\", \"\")", "correct": False, "explanation": "Incomplete sanitization vulnerable to alternate encoding bypasses."},
            {"id": "C", "label": "Convert all inputs to uppercase", "correct": False, "explanation": "Does not prevent SQL injection attacks."}
        ]
    }
]

class CodeEngine:
    def __init__(self, target_dir: str = None, transaction_mgr: TransactionManager = None):
        self.base_dir = Path(target_dir) if target_dir else Path(__file__).resolve().parent.parent / "sample_data" / "buggy_code"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.tx_mgr = transaction_mgr or TransactionManager()
        self.init_sample_files()

    def init_sample_files(self):
        for ch in CODE_CHALLENGES:
            file_path = self.base_dir / ch["filename"]
            if not file_path.exists():
                file_path.write_text(ch["buggy_code"], encoding="utf-8")

    def get_challenges(self) -> List[Dict[str, Any]]:
        results = []
        for ch in CODE_CHALLENGES:
            file_path = self.base_dir / ch["filename"]
            current_code = file_path.read_text(encoding="utf-8") if file_path.exists() else ch["buggy_code"]
            is_fixed = current_code.strip() == ch["fixed_code"].strip()

            # Generate unified diff
            diff_lines = list(difflib.unified_diff(
                ch["buggy_code"].splitlines(keepends=True),
                ch["fixed_code"].splitlines(keepends=True),
                fromfile=f"a/{ch['filename']} (corrupted)",
                tofile=f"b/{ch['filename']} (purified)"
            ))
            diff_text = "".join(diff_lines)

            results.append({
                "id": ch["id"],
                "title": ch["title"],
                "language": ch["language"],
                "filename": ch["filename"],
                "filepath": str(file_path),
                "bug_type": ch["bug_type"],
                "difficulty": ch["difficulty"],
                "monster_name": ch["monster_name"],
                "monster_hp": ch["monster_hp"],
                "current_code": current_code,
                "is_fixed": is_fixed,
                "diff": diff_text,
                "options": ch["options"]
            })
        return results

    def patch_code(self, challenge_id: str, selected_option_id: str, dry_run: bool = False) -> Dict[str, Any]:
        challenge = next((c for c in CODE_CHALLENGES if c["id"] == challenge_id), None)
        if not challenge:
            return {"success": False, "error": f"Challenge {challenge_id} not found"}

        option = next((opt for opt in challenge["options"] if opt["id"] == selected_option_id), None)
        if not option:
            return {"success": False, "error": "Invalid option selected"}

        if not option["correct"]:
            return {
                "success": False,
                "is_correct": False,
                "message": f"Spell fizzled! {option['explanation']}",
                "damage_taken": 20
            }

        file_path = self.base_dir / challenge["filename"]
        original_code = file_path.read_text(encoding="utf-8") if file_path.exists() else challenge["buggy_code"]
        fixed_code = challenge["fixed_code"]

        # Validate syntax for python code
        syntax_valid = True
        syntax_err = ""
        if challenge["language"] == "python":
            try:
                ast.parse(fixed_code)
            except SyntaxError as e:
                syntax_valid = False
                syntax_err = str(e)

        if not syntax_valid:
            return {"success": False, "error": f"Syntax error in patch: {syntax_err}"}

        before_state = {"file_path": str(file_path), "original_code": original_code}
        after_state = {"file_path": str(file_path), "patched_code": fixed_code}

        if not dry_run:
            file_path.write_text(fixed_code, encoding="utf-8")

        tx = self.tx_mgr.record(
            chore_type="code_debugging",
            action="patch_code",
            details=f"Squashed {challenge['bug_type']} in '{challenge['filename']}'",
            before_state=before_state,
            after_state=after_state,
            is_dry_run=dry_run,
            impact_metric="bugs_fixed",
            impact_value=1
        )

        return {
            "success": True,
            "is_correct": True,
            "message": f"Critical Hit! Bug Exterminated: {option['explanation']}",
            "filename": challenge["filename"],
            "transaction": tx
        }
