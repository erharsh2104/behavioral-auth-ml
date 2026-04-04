"""
ML Model for Behavioral Authentication
Ensemble of Random Forest + SVM
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, confusion_matrix,
                             classification_report)
from sklearn.pipeline import Pipeline
import pickle
import os
import warnings
warnings.filterwarnings("ignore")

MODEL_PATH = "models/behavioral_auth_model.pkl"

FEATURE_NAMES = [
    "mean_dwell", "std_dwell", "median_dwell", "max_dwell",
    "mean_flight", "std_flight", "median_flight", "min_flight",
    "typing_speed_wpm", "dwell_flight_ratio",
    "rhythm_consistency", "total_time_ms", "n_keys"
]


class BehavioralAuthModel:
    def __init__(self):
        self.rf = None
        self.svm = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        self.accuracy = 0.0
        self.class_labels = []
        self.feature_names = FEATURE_NAMES
        self.threshold = 0.45  # Minimum confidence to authenticate
        self._load()

    # ── Training ──────────────────────────────────────────────────────────────
    def train(self, X: np.ndarray, y: np.ndarray,
              n_estimators: int = 100,
              test_size: float = 0.2) -> dict:

        y_enc = self.label_encoder.fit_transform(y)
        self.class_labels = list(self.label_encoder.classes_)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_enc, test_size=test_size, random_state=42, stratify=y_enc
        )

        # Scale
        X_train_sc = self.scaler.fit_transform(X_train)
        X_test_sc = self.scaler.transform(X_test)

        # Random Forest
        self.rf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=None,
            min_samples_split=2,
            random_state=42,
            class_weight='balanced'
        )
        self.rf.fit(X_train_sc, y_train)

        # SVM
        self.svm = SVC(
            kernel='rbf',
            C=10,
            gamma='scale',
            probability=True,
            random_state=42
        )
        self.svm.fit(X_train_sc, y_train)

        # Evaluate
        rf_preds = self.rf.predict(X_test_sc)
        svm_preds = self.svm.predict(X_test_sc)

        # Ensemble: weighted vote (RF heavier)
        rf_proba = self.rf.predict_proba(X_test_sc)
        svm_proba = self.svm.predict_proba(X_test_sc)
        ensemble_proba = 0.6 * rf_proba + 0.4 * svm_proba
        ensemble_preds = np.argmax(ensemble_proba, axis=1)

        self.accuracy = accuracy_score(y_test, ensemble_preds)
        self.is_trained = True

        # Feature importance (RF only)
        fi_raw = self.rf.feature_importances_
        fi = {self.feature_names[i]: float(fi_raw[i])
              for i in np.argsort(fi_raw)[::-1]}

        cm = confusion_matrix(y_test, ensemble_preds)

        self._save()

        return {
            "accuracy": self.accuracy,
            "n_train": len(X_train),
            "n_test": len(X_test),
            "n_features": X.shape[1],
            "confusion_matrix": cm,
            "class_labels": self.class_labels,
            "feature_importance": fi,
            "rf_accuracy": accuracy_score(y_test, rf_preds),
            "svm_accuracy": accuracy_score(y_test, svm_preds),
        }

    # ── Prediction ────────────────────────────────────────────────────────────
    def predict(self, features: dict, claimed_user: str) -> dict:
        if not self.is_trained:
            raise RuntimeError("Model not trained yet.")

        x = np.array([[features.get(f, 0.0) for f in self.feature_names]])
        x_sc = self.scaler.transform(x)

        rf_proba = self.rf.predict_proba(x_sc)[0]
        svm_proba = self.svm.predict_proba(x_sc)[0]
        ensemble_proba = 0.6 * rf_proba + 0.4 * svm_proba

        predicted_idx = np.argmax(ensemble_proba)
        predicted_user = self.class_labels[predicted_idx]
        confidence = float(ensemble_proba[predicted_idx])

        # Confidence for claimed user
        if claimed_user in self.class_labels:
            claimed_idx = self.class_labels.index(claimed_user)
            claimed_confidence = float(ensemble_proba[claimed_idx])
        else:
            claimed_confidence = 0.0

        authenticated = (
            predicted_user == claimed_user and
            claimed_confidence >= self.threshold
        )

        all_probs = {
            self.class_labels[i]: float(ensemble_proba[i])
            for i in range(len(self.class_labels))
        }

        return {
            "authenticated": authenticated,
            "predicted_user": predicted_user,
            "confidence": confidence,
            "claimed_confidence": claimed_confidence,
            "all_probabilities": all_probs,
            "threshold": self.threshold,
        }

    # ── Persistence ───────────────────────────────────────────────────────────
    def _save(self):
        os.makedirs("models", exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump({
                'rf': self.rf,
                'svm': self.svm,
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'accuracy': self.accuracy,
                'class_labels': self.class_labels,
                'feature_names': self.feature_names,
                'threshold': self.threshold,
            }, f)

    def _load(self):
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, 'rb') as f:
                    d = pickle.load(f)
                self.rf = d['rf']
                self.svm = d['svm']
                self.scaler = d['scaler']
                self.label_encoder = d['label_encoder']
                self.accuracy = d['accuracy']
                self.class_labels = d['class_labels']
                self.feature_names = d.get('feature_names', FEATURE_NAMES)
                self.threshold = d.get('threshold', 0.45)
                self.is_trained = True
            except Exception:
                pass
