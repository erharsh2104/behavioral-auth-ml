# Behavioral-Based Authentication Using ML

A mini-project that authenticates users by their **typing rhythm** (keystroke dynamics), not just their password.

## What It Does
- Captures **dwell time** (key hold duration) and **flight time** (gap between keys)
- Extracts 13 behavioral features per typing session
- Trains an **ensemble ML model** (Random Forest + SVM) to distinguish users
- Authenticates in real-time by comparing keystroke patterns

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed demo data (optional but recommended)
```bash
python seed_demo.py
```
This creates 4 demo users (Alice, Bob, Charlie, Diana) with 15 samples each and trains the model automatically.

### 3. Run the app
```bash
streamlit run app.py
```

## Manual Usage (without seed)
1. Open the app → **Register User** → create 2+ users, collect 10 samples each
2. **Train Model** → click "Train Model Now"
3. **Authenticate** → select a user, type the phrase, see the result

## Features Extracted
| Feature | Description |
|---|---|
| mean_dwell | Average key hold duration (ms) |
| std_dwell | Variability of key hold time |
| median_dwell | Median hold time (robust to outliers) |
| max_dwell | Slowest key held |
| mean_flight | Average between-key gap (ms) |
| std_flight | Variability of key gaps |
| median_flight | Median gap (robust) |
| min_flight | Fastest key transition |
| typing_speed_wpm | Words per minute |
| dwell_flight_ratio | Signature hold-to-release ratio |
| rhythm_consistency | How regular the typing pace is |
| total_time_ms | Total time to complete phrase |
| n_keys | Number of keystrokes captured |

## ML Model
- **Random Forest** (100 trees) — ensemble of decision trees, robust to noise
- **SVM** (RBF kernel) — finds optimal boundary between user clusters in feature space
- **Ensemble** — weighted average (RF 60%, SVM 40%)
- **Threshold** — 45% minimum confidence to authenticate

## Project Structure
```
behavioral_auth/
├── app.py           # Streamlit web app (main UI)
├── ml_model.py      # ML training + prediction logic
├── data_manager.py  # User & sample data storage
├── seed_demo.py     # Demo data seeder script
├── requirements.txt
├── data/            # User samples (JSON)
└── models/          # Saved model (pickle)
```

## Academic References
1. Monrose & Rubin (2000) — *Keystroke Dynamics as a Biometric for Authentication*, Future Generation Computer Systems
2. Killourhy & Maxion (2009) — *Comparing Anomaly-Detection Algorithms for Keystroke Dynamics* (CMU Dataset)
3. Ahmed & Traore (2007) — *A New Biometric Technology Based on Mouse Dynamics*, IEEE Trans. Dependable & Secure Computing

## Author
Roll No: AD23B1021 | IIIT Raichur | 3-Credit Mini Project
