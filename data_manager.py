"""
Data Manager — handles user registration, sample storage, dataset building
"""

import json
import os
import numpy as np
from datetime import datetime

DATA_PATH = "data/users.json"
FEATURE_NAMES = [
    "mean_dwell", "std_dwell", "median_dwell", "max_dwell",
    "mean_flight", "std_flight", "median_flight", "min_flight",
    "typing_speed_wpm", "dwell_flight_ratio",
    "rhythm_consistency", "total_time_ms", "n_keys"
]


class DataManager:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self._data = self._load()

    def _load(self):
        if os.path.exists(DATA_PATH):
            try:
                with open(DATA_PATH) as f:
                    return json.load(f)
            except Exception:
                pass
        return {"users": {}}

    def _save(self):
        with open(DATA_PATH, 'w') as f:
            json.dump(self._data, f, indent=2)

    def get_all_users(self):
        return list(self._data["users"].keys())

    def register_user(self, username: str):
        if username not in self._data["users"]:
            self._data["users"][username] = {
                "created": datetime.now().isoformat(),
                "samples": []
            }
            self._save()

    def add_sample(self, username: str, typed_text: str, features: dict):
        if username not in self._data["users"]:
            self.register_user(username)
        self._data["users"][username]["samples"].append({
            "timestamp": datetime.now().isoformat(),
            "text": typed_text,
            "features": features
        })
        self._save()

    def get_sample_count(self, username: str) -> int:
        return len(self._data["users"].get(username, {}).get("samples", []))

    def get_samples(self, username: str) -> list:
        return self._data["users"].get(username, {}).get("samples", [])

    def build_dataset(self):
        """Return (X, y) arrays for model training."""
        X, y = [], []
        for user, info in self._data["users"].items():
            for s in info["samples"]:
                feat_vec = [s["features"].get(f, 0.0) for f in FEATURE_NAMES]
                X.append(feat_vec)
                y.append(user)
        return np.array(X, dtype=float), np.array(y)


    def store_password(self, username: str, pwd_hash: str):
        """Store SHA-256 password hash for a user."""
        if username in self._data["users"]:
            self._data["users"][username]["password_hash"] = pwd_hash
            self._save()

    def get_password(self, username: str):
        """Return stored password hash, or None if not set."""
        return self._data["users"].get(username, {}).get("password_hash", None)
    def delete_user(self, username: str):
        if username in self._data["users"]:
            del self._data["users"][username]
            self._save()

    def clear_all(self):
        self._data = {"users": {}}
        self._save()
