import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from chore_engine.transaction_manager import TransactionManager

CATEGORY_RULES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".csv", ".md", ".rtf"],
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".ico"],
    "Media": [".mp4", ".mp3", ".wav", ".mkv", ".mov", ".avi", ".flac", ".ogg"],
    "Installers": [".exe", ".msi", ".dmg", ".pkg", ".iso", ".bat", ".cmd"],
    "Archives": [".zip", ".tar", ".gz", ".7z", ".rar", ".tar.gz"],
    "Code": [".py", ".js", ".html", ".css", ".ts", ".json", ".sql", ".java", ".cpp", ".rs", ".go"],
    "Junk": [".tmp", ".temp", ".log", ".crdownload", ".part", ".bak", ".dmp"]
}

CATEGORY_ICONS = {
    "Documents": "📄",
    "Images": "🖼️",
    "Media": "🎬",
    "Installers": "⚙️",
    "Archives": "📦",
    "Code": "💻",
    "Junk": "🗑️",
    "Unsorted": "📁"
}

CATEGORY_MONSTERS = {
    "Documents": {"name": "Scroll Golem", "hp": 30, "color": "#38bdf8", "type": "lore"},
    "Images": {"name": "Prism Specter", "hp": 25, "color": "#ec4899", "type": "visual"},
    "Media": {"name": "Echo Drake", "hp": 35, "color": "#a855f7", "type": "sonic"},
    "Installers": {"name": "Titan Binary", "hp": 50, "color": "#f59e0b", "type": "heavy"},
    "Archives": {"name": "Mummy Bundle", "hp": 40, "color": "#eab308", "type": "packed"},
    "Code": {"name": "Cyber Automaton", "hp": 30, "color": "#10b981", "type": "logic"},
    "Junk": {"name": "Slime Parasite", "hp": 15, "color": "#ef4444", "type": "decay"},
    "Unsorted": {"name": "Rogue Chest", "hp": 20, "color": "#94a3b8", "type": "mystery"}
}

class FileEngine:
    def __init__(self, target_dir: str = None, transaction_mgr: TransactionManager = None):
        self.base_dir = Path(target_dir) if target_dir else Path(__file__).resolve().parent.parent / "sample_data" / "messy_files"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.tx_mgr = transaction_mgr or TransactionManager()

    def set_target_directory(self, new_dir: str):
        path = Path(new_dir)
        if path.exists() and path.is_dir():
            self.base_dir = path
            return True, f"Target directory switched to {path}"
        return False, "Directory does not exist or is not a folder"

    def get_category_for_ext(self, ext: str) -> str:
        ext_lower = ext.lower()
        for cat, extensions in CATEGORY_RULES.items():
            if ext_lower in extensions:
                return cat
        return "Unsorted"

    def scan_directory(self) -> Dict[str, Any]:
        """Scans the directory for unorganized files and duplicates."""
        files = []
        hashes = {}
        duplicates = []
        category_counts = {cat: 0 for cat in CATEGORY_RULES.keys()}
        category_counts["Unsorted"] = 0
        total_size = 0

        # Scan top-level files in directory (ignoring existing subfolder categories for the game)
        for entry in self.base_dir.iterdir():
            if entry.is_file():
                ext = entry.suffix.lower()
                cat = self.get_category_for_ext(ext)
                size = entry.stat().st_size
                total_size += size
                category_counts[cat] = category_counts.get(cat, 0) + 1

                # MD5 hash for duplicate detection (first 64KB for speed or full for small files)
                try:
                    file_hash = self._calc_hash(entry)
                    if file_hash in hashes:
                        duplicates.append({
                            "original": hashes[file_hash]["name"],
                            "duplicate": entry.name,
                            "path": str(entry),
                            "size": size,
                            "hash": file_hash
                        })
                    else:
                        hashes[file_hash] = {"name": entry.name, "path": str(entry), "size": size}
                except Exception:
                    file_hash = None

                files.append({
                    "name": entry.name,
                    "path": str(entry),
                    "extension": ext,
                    "category": cat,
                    "size": size,
                    "size_formatted": self._format_size(size),
                    "icon": CATEGORY_ICONS.get(cat, "📁"),
                    "monster": CATEGORY_MONSTERS.get(cat, CATEGORY_MONSTERS["Unsorted"]),
                    "is_duplicate": file_hash in hashes and hashes[file_hash]["name"] != entry.name,
                    "hash": file_hash
                })

        return {
            "directory": str(self.base_dir),
            "total_files": len(files),
            "total_size": total_size,
            "total_size_formatted": self._format_size(total_size),
            "category_counts": category_counts,
            "duplicate_count": len(duplicates),
            "duplicates": duplicates,
            "files": files
        }

    def _calc_hash(self, file_path: Path) -> str:
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    def _format_size(self, size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def organize_file(self, filename: str, target_category: str = None, dry_run: bool = False) -> Dict[str, Any]:
        """Moves a single file into its designated category directory."""
        src_path = self.base_dir / filename
        if not src_path.exists():
            return {"success": False, "error": f"File '{filename}' not found"}

        if not target_category:
            target_category = self.get_category_for_ext(src_path.suffix)

        target_dir = self.base_dir / target_category
        dest_path = target_dir / filename

        # Handle filename collisions in destination
        if dest_path.exists() and dest_path != src_path:
            stem = src_path.stem
            suffix = src_path.suffix
            counter = 1
            while dest_path.exists():
                dest_path = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        file_size = src_path.stat().st_size
        before_state = {"src_path": str(src_path), "size": file_size}
        after_state = {"dest_path": str(dest_path), "category": target_category}

        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dest_path))

        tx = self.tx_mgr.record(
            chore_type="file_organization",
            action="move_file",
            details=f"Organized '{filename}' into '{target_category}/'",
            before_state=before_state,
            after_state=after_state,
            is_dry_run=dry_run,
            impact_metric="files_sorted",
            impact_value=1
        )

        return {
            "success": True,
            "filename": filename,
            "new_path": str(dest_path),
            "category": target_category,
            "dry_run": dry_run,
            "transaction": tx
        }

    def quarantine_duplicate(self, filename: str, dry_run: bool = False) -> Dict[str, Any]:
        """Moves duplicate file into a .quarantine / Trash folder to safely free space."""
        src_path = self.base_dir / filename
        if not src_path.exists():
            return {"success": False, "error": f"File '{filename}' not found"}

        quarantine_dir = self.base_dir / ".quarantine"
        dest_path = quarantine_dir / filename
        file_size = src_path.stat().st_size

        before_state = {"orig_path": str(src_path), "size": file_size}
        after_state = {"quarantine_path": str(dest_path)}

        if not dry_run:
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dest_path))

        tx = self.tx_mgr.record(
            chore_type="file_organization",
            action="quarantine_duplicate",
            details=f"Quarantined duplicate file '{filename}' ({self._format_size(file_size)})",
            before_state=before_state,
            after_state=after_state,
            is_dry_run=dry_run,
            impact_metric="bytes_freed",
            impact_value=file_size
        )

        return {
            "success": True,
            "filename": filename,
            "bytes_freed": file_size,
            "formatted_size": self._format_size(file_size),
            "transaction": tx
        }

    def generate_sample_messy_files(self) -> int:
        """Populates the sample directory with realistic messy files for gameplay."""
        samples = [
            ("Q3_Financial_Report_Final_v2.pdf", "Documents", 245000, b"%PDF-1.4 sample quarterly report content..."),
            ("Project_Roadmap_2026.docx", "Documents", 120000, b"PK\x03\x04 Sample Word Document Roadmap"),
            ("Meeting_Notes_Oct31.txt", "Documents", 4200, b"Action items: clean inbox, sort desktop"),
            ("Client_Invoice_9041.pdf", "Documents", 98000, b"%PDF-1.4 Invoice 9041 Paid"),
            ("Screenshot_2026-10-31_114201.png", "Images", 850000, b"\x89PNG\r\n\x1a\n Sample Screenshot 1"),
            ("Banner_Concept_v3_dark.jpg", "Images", 1450000, b"\xff\xd8\xff\xe0 Sample Banner Art"),
            ("team_avatar_mascot.png", "Images", 340000, b"\x89PNG\r\n\x1a\n Mascot icon"),
            ("product_demo_reel_draft.mp4", "Media", 14500000, b"\x00\x00\x00\x20ftypisom Demo Video"),
            ("podcast_ep42_final_mix.mp3", "Media", 8900000, b"ID3\x03\x00 Podcast audio sample"),
            ("Node_v22_x64_installer.exe", "Installers", 45000000, b"MZ Sample Node installer binary"),
            ("Postgres_Setup_v16.msi", "Installers", 62000000, b"\xd0\xcf\x11\xe0 MSI Installer"),
            ("Figma_Desktop_Setup.exe", "Installers", 51000000, b"MZ Figma Setup"),
            ("backup_photos_archive.zip", "Archives", 34000000, b"PK\x03\x04 Zip Archive photos"),
            ("legacy_database_dump.tar.gz", "Archives", 28000000, b"\x1f\x8b Legacy DB backup"),
            ("api_gateway_service.py", "Code", 15400, b"import sys\ndef handler(): pass"),
            ("landing_page_bundle.js", "Code", 84000, b"const app = () => console.log('ready');"),
            ("temp_debug_dump_381.log", "Junk", 12000, b"2026-10-31 DEBUG trace error code 0x884"),
            ("installer (1).exe", "Installers", 45000000, b"MZ Sample Node installer binary"), # Duplicate!
            ("Screenshot_duplicate.png", "Images", 850000, b"\x89PNG\r\n\x1a\n Sample Screenshot 1") # Duplicate!
        ]

        created = 0
        for name, cat, size, content in samples:
            file_path = self.base_dir / name
            if not file_path.exists():
                file_path.write_bytes(content + b"\x00" * max(0, min(1024, size - len(content))))
                created += 1
        return created
