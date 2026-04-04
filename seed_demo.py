"""
seed_demo.py — Run this once to pre-populate demo data and train the model.
Usage:  python seed_demo.py
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from data_manager import DataManager
from ml_model import BehavioralAuthModel

TARGET = "the quick brown fox jumps"

DEMO_USERS = ["Alice", "Bob", "Charlie", "Diana"]

# Each user has a distinct typing persona: (base_dwell, base_flight, noise_level, wpm_range)
USER_PERSONAS = {
    "Alice":   dict(base_dwell=70,  base_flight=55,  noise=8,  wpm_base=90),   # Fast, precise
    "Bob":     dict(base_dwell=160, base_flight=140, noise=30, wpm_base=40),   # Slow, inconsistent
    "Charlie": dict(base_dwell=110, base_flight=200, noise=12, wpm_base=55),   # Med dwell, long gaps
    "Diana":   dict(base_dwell=95,  base_flight=70,  noise=5,  wpm_base=75),   # Fast, very consistent
}

def simulate_features(user: str, seed_offset: int = 0):
    p = USER_PERSONAS.get(user, dict(base_dwell=120, base_flight=100, noise=20, wpm_base=60))
    seed = sum(ord(c) for c in user) + seed_offset
    rng = np.random.RandomState(seed)
    n = 25

    dwells  = np.clip(rng.normal(p["base_dwell"],  p["noise"],       n), 30, 400)
    flights = np.clip(rng.normal(p["base_flight"], p["noise"] * 1.5, n), 20, 500)

    total_ms = float(np.sum(dwells) + np.sum(flights))
    wpm = float(np.clip(p["wpm_base"] + rng.normal(0, 5), 10, 200))

    return {
        "mean_dwell":         float(np.mean(dwells)),
        "std_dwell":          float(np.std(dwells)),
        "median_dwell":       float(np.median(dwells)),
        "max_dwell":          float(np.max(dwells)),
        "mean_flight":        float(np.mean(flights)),
        "std_flight":         float(np.std(flights)),
        "median_flight":      float(np.median(flights)),
        "min_flight":         float(np.min(flights)),
        "typing_speed_wpm":   wpm,
        "dwell_flight_ratio": float(np.mean(dwells) / max(np.mean(flights), 1)),
        "rhythm_consistency": float(1.0 / (1.0 + np.std(flights) / max(np.mean(flights), 1))),
        "total_time_ms":      total_ms,
        "n_keys":             n,
    }

def main():
    dm = DataManager()
    model = BehavioralAuthModel()

    # Default passwords for demo users
    DEMO_PASSWORDS = {
        "Alice":   "Alice@123",
        "Bob":     "Bob@123",
        "Charlie": "Charlie@123",
        "Diana":   "Diana@123",
    }

    print("Seeding demo users and samples...")
    for user in DEMO_USERS:
        dm.register_user(user)
        # Store password hash
        import hashlib
        pwd_hash = hashlib.sha256(DEMO_PASSWORDS[user].encode("utf-8")).hexdigest()
        dm.store_password(user, pwd_hash)
        for i in range(15):          # 15 samples per user
            feat = simulate_features(user, seed_offset=i * 7)
            dm.add_sample(user, TARGET, feat)
        cnt = dm.get_sample_count(user)
        print(f"  {user}: {cnt} samples | password: {DEMO_PASSWORDS[user]}")

    print("\nBuilding dataset and training model...")
    X, y = dm.build_dataset()
    print(f"  Dataset: {X.shape[0]} samples × {X.shape[1]} features, {len(set(y))} users")

    results = model.train(X, y)
    print(f"  Model accuracy: {results['accuracy']*100:.1f}%")
    print(f"  RF accuracy:    {results['rf_accuracy']*100:.1f}%")
    print(f"  SVM accuracy:   {results['svm_accuracy']*100:.1f}%")
    print("\nTop features:")
    for feat, imp in list(results['feature_importance'].items())[:5]:
        print(f"  {feat}: {imp:.4f}")

    print("\n✅ Done! Run:  streamlit run app.py")

if __name__ == "__main__":
    main()
