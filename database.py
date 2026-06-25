import json
import os
from pathlib import Path
from typing import Optional, Dict, List


DATA_DIR = Path.home() / ".financeai_data"


class Database:
    def __init__(self):
        DATA_DIR.mkdir(exist_ok=True)
        self.users_file = DATA_DIR / "users.json"
        self.tx_dir     = DATA_DIR / "transactions"
        self.api_dir    = DATA_DIR / "api_keys"
        self.tx_dir.mkdir(exist_ok=True)
        self.api_dir.mkdir(exist_ok=True)
        if not self.users_file.exists():
            self._write(self.users_file, {})

    # ── Internals ─────────────────────────────────────────────────────────────
    def _read(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ── Users ─────────────────────────────────────────────────────────────────
    def get_user(self, username: str) -> Optional[Dict]:
        users = self._read(self.users_file)
        return users.get(username)

    def create_user(self, name: str, username: str,
                    hashed_pw: str, acc_type: str):
        users = self._read(self.users_file)
        users[username] = {
            "name": name,
            "username": username,
            "password": hashed_pw,
            "acc_type": acc_type,
        }
        self._write(self.users_file, users)

    # ── Transactions ──────────────────────────────────────────────────────────
    def _tx_path(self, username: str) -> Path:
        return self.tx_dir / f"{username}.json"

    def get_transactions(self, username: str) -> List[Dict]:
        path = self._tx_path(username)
        if not path.exists():
            return []
        return self._read(path)

    def add_transaction(self, username: str, tx: Dict):
        txs = self.get_transactions(username)
        txs.append(tx)
        self._write(self._tx_path(username), txs)

    # ── API Keys ──────────────────────────────────────────────────────────────
    def _api_path(self, username: str) -> Path:
        return self.api_dir / f"{username}.json"

    def get_api_key(self, username: str) -> Optional[str]:
        path = self._api_path(username)
        if not path.exists():
            return None
        data = self._read(path)
        return data.get("api_key")

    def save_api_key(self, username: str, api_key: str):
        self._write(self._api_path(username), {"api_key": api_key})
