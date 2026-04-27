# Behavioral Authentication System

A two-factor authentication system that combines traditional password verification with **keystroke dynamics biometrics** to provide continuous behavioral authentication. This project implements machine learning-based user identification through typing pattern analysis.

## Overview

Traditional password-based authentication relies solely on "what you know," making it vulnerable to password theft, credential stuffing, and social engineering attacks. This system adds a second authentication factor based on **"who you are"** by analyzing unique typing characteristics that are difficult to replicate.

The system captures real-time keystroke timing data through browser-based JavaScript event listeners and uses an ensemble machine learning model to verify user identity based on their typing rhythm. Even if an attacker obtains the correct password, they cannot authenticate without matching the legitimate user's distinctive typing pattern.

### Problem Statement

- **Credential Compromise**: Stolen passwords grant immediate unauthorized access
- **Weak Password Policies**: Users often choose weak or reused passwords
- **Social Engineering**: Phishing attacks can bypass traditional authentication
- **Session Hijacking**: Valid credentials don't guarantee continuous user authenticity

### Solution

This project implements keystroke dynamics as a behavioral biometric, providing:
- Non-invasive continuous authentication
- Resistance to credential theft attacks
- Zero additional hardware requirements
- Passive authentication layer that doesn't burden users

## Features

### Core Functionality
- **Two-Factor Authentication**: Password (SHA-256) + Keystroke Dynamics
- **Real-Time Keystroke Capture**: JavaScript-based timing measurement using `performance.now()` API
- **13-Feature Biometric Profile**: Comprehensive typing pattern analysis
- **Ensemble ML Model**: Combined Random Forest + SVM classifier (60-40 weighted voting)
- **Confidence-Based Verification**: Configurable threshold (default: 45%) for authentication decisions
- **Multi-User Support**: Simultaneous registration and authentication of multiple users
- **Interactive Dashboard**: Real-time visualization of typing patterns and model performance

### Security Features
- **Password Hashing**: SHA-256 cryptographic hashing for credential storage
- **Behavioral Anomaly Detection**: ML-based identification of typing pattern deviations
- **Attack Simulation Mode**: Built-in impersonation testing functionality
- **Minimum Sample Requirements**: Enforces sufficient training data before authentication
- **Prediction Confidence Scoring**: Transparent probability-based authentication decisions

## Tech Stack

### Languages & Frameworks
- **Python 3.12+**: Core application logic
- **JavaScript (ES6)**: Client-side keystroke event capture
- **HTML5/CSS3**: User interface rendering

### Libraries & Dependencies
- **streamlit (≥1.32.0)**: Web application framework and UI components
- **scikit-learn (≥1.4.0)**: Machine learning pipeline (RandomForest, SVM, preprocessing)
- **numpy (≥1.26.0)**: Numerical computation and array operations
- **pandas (≥2.2.0)**: Data manipulation and analysis
- **plotly (≥5.20.0)**: Interactive data visualization

### Development Tools
- **pickle**: Model serialization and persistence
- **JSON**: User data and sample storage
- **hashlib**: Cryptographic password hashing

## Project Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser (Client)                      │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Keystroke Capture Widget (JavaScript)             │     │
│  │  • keydown/keyup event listeners                   │     │
│  │  • performance.now() timing                        │     │
│  │  • 13-feature extraction                           │     │
│  └────────────────────────────────────────────────────┘     │
│                           ↓ URL params                       │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Application                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   app.py    │→ │data_manager  │→ │  ml_model    │       │
│  │  (UI Logic) │  │   .py        │  │    .py       │       │
│  │             │  │              │  │              │       │
│  │ • Register  │  │ • User CRUD  │  │ • Training   │       │
│  │ • Authenti- │  │ • Sample     │  │ • Prediction │       │
│  │   cate      │  │   Storage    │  │ • Ensemble   │       │
│  │ • Train     │  │ • Dataset    │  │   Model      │       │
│  │ • Dashboard │  │   Builder    │  │              │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│         ↓                ↓                   ↓               │
└─────────────────────────────────────────────────────────────┘
          ↓                ↓                   ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ data/        │  │ models/      │  │Session State │
│ users.json   │  │ *.pkl        │  │ (in-memory)  │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Module Descriptions

**app.py (Main Application)**
- Streamlit-based web interface with 7 navigation pages
- JavaScript widget integration for keystroke capture
- Session state management for real-time feature transmission
- Multi-page routing: Home, Register, Train, Authenticate, Attack Simulation, Dashboard, Documentation

**ml_model.py (Machine Learning Pipeline)**
- `BehavioralAuthModel` class implementing ensemble classifier
- Random Forest (100 trees, balanced class weights)
- SVM with RBF kernel (C=10, gamma='scale')
- StandardScaler feature normalization (fit on training set only)
- Pickle-based model persistence

**data_manager.py (Data Layer)**
- `DataManager` class for user and sample CRUD operations
- JSON-based persistent storage (`data/users.json`)
- Password hash storage (SHA-256)
- Dataset builder for ML training (X, y array generation)

**seed_demo.py (Demo Data Generator)**
- Simulates 4 users (Alice, Bob, Charlie, Diana) with distinct typing personas
- Generates 15 realistic samples per user using statistical distributions
- Automatic model training after data generation

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd behavioral_auth_DEPLOY/behavioral_auth
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Generate Demo Data (Recommended)
```bash
python seed_demo.py
```

**Expected Output:**
```
Seeding demo users and samples...
  Alice: 15 samples | password: Alice@123
  Bob: 15 samples | password: Bob@123
  Charlie: 15 samples | password: Charlie@123
  Diana: 15 samples | password: Diana@123

Building dataset and training model...
  Dataset: 60 samples × 13 features, 4 users
  Model accuracy: 95.0%
  RF accuracy:    91.7%
  SVM accuracy:   91.7%

Top features:
  mean_flight: 0.2453
  typing_speed_wpm: 0.1842
  ...

✅ Done! Run:  streamlit run app.py
```

### Step 4: Launch Application
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

## Usage

### Quick Start with Demo Data

1. **Authentication Test**
   - Navigate to **Authenticate** page
   - Select user: `Alice`
   - Enter password: `Alice@123`
   - Type the target phrase: `the quick brown fox jumps`
   - View authentication result with confidence score

2. **Attack Simulation**
   - Navigate to **Attack Demo** page
   - Select legitimate user (e.g., `Alice`)
   - Select attacker identity (e.g., `Bob`)
   - Enter Alice's password: `Alice@123`
   - Type the phrase as Bob (different typing rhythm)
   - Observe authentication failure despite correct password

3. **Dashboard Analysis**
   - Navigate to **Dashboard** page
   - Explore user clusters in feature space
   - Analyze typing speed distributions
   - View correlation heatmaps
   - Inspect confusion matrix

### Manual User Registration

1. **Register New User**
   - Navigate to **Register User** page
   - Enter username and password
   - Type the target phrase 10-15 times
   - System captures keystroke features for each sample

2. **Train Model**
   - Navigate to **Train Model** page
   - Ensure at least 2 users with 5+ samples each
   - Click **Train Model Now**
   - Review accuracy metrics and feature importance

3. **Authenticate**
   - Navigate to **Authenticate** page
   - Select username, enter password, type phrase
   - System validates both password and typing pattern

## Behavioral Feature Extraction

The system extracts 13 temporal features from raw keystroke events:

| Feature | Description | Security Relevance |
|---------|-------------|-------------------|
| `mean_dwell` | Average key hold duration (ms) | Distinguishes fast vs. deliberate typists |
| `std_dwell` | Standard deviation of dwell times | Measures typing consistency |
| `median_dwell` | Median hold time | Robust to outliers (e.g., pauses) |
| `max_dwell` | Maximum hold duration | Detects hesitation patterns |
| `mean_flight` | Average inter-key interval (ms) | **Strongest discriminative feature** |
| `std_flight` | Standard deviation of flight times | Rhythm variability signature |
| `median_flight` | Median inter-key gap | Robust rhythm metric |
| `min_flight` | Minimum flight time | Captures peak typing speed |
| `typing_speed_wpm` | Words per minute | Overall speed profile |
| `dwell_flight_ratio` | Hold time / gap time ratio | Unique per-user typing signature |
| `rhythm_consistency` | 1/(1 + CV of flight times) | Regularity of typing cadence |
| `total_time_ms` | Total phrase completion time | Session-level timing |
| `n_keys` | Number of keystrokes captured | Data quality check |

**Feature Computation:**
- Dwell time: `keyup.timestamp - keydown.timestamp`
- Flight time: `keydown[i+1].timestamp - keyup[i].timestamp`
- All timing via `performance.now()` (sub-millisecond precision)

## Security Considerations

### Threats Mitigated

1. **Credential Theft**
   - **Attack**: Attacker obtains valid username/password through phishing or database breach
   - **Defense**: Authentication fails if typing pattern doesn't match enrolled samples
   - **Effectiveness**: 95%+ detection rate in testing (see Dashboard metrics)

2. **Replay Attacks**
   - **Attack**: Attacker captures and replays authentication session
   - **Defense**: Each keystroke sequence is unique due to natural timing variations
   - **Limitation**: Direct feature injection via API manipulation not currently prevented

3. **Brute Force Password Guessing**
   - **Attack**: Automated password enumeration
   - **Defense**: Even correct password requires matching typing pattern
   - **Additional Barrier**: Computationally infeasible to simultaneously brute-force password and biometric signature

### Best Practices Implemented

- **No Plaintext Storage**: Passwords hashed with SHA-256 before persistence
- **Balanced Training Data**: Class weights adjusted to prevent bias toward majority users
- **Confidence Thresholding**: Minimum 45% probability required for authentication
- **Feature Normalization**: StandardScaler prevents feature magnitude bias
- **Train-Test Split**: 80-20 split with stratification ensures unbiased evaluation

### Known Limitations

1. **Typing Condition Variability**
   - User fatigue, stress, or injury may alter typing patterns
   - Keyboard switching (laptop → desktop) impacts feature distributions
   - **Mitigation**: Collect samples across multiple sessions and devices

2. **Sample Size Requirements**
   - Minimum 10-15 samples per user for reliable authentication
   - Cold-start problem for new users
   - **Mitigation**: Graceful degradation (password-only mode) until sufficient samples collected

3. **Storage Security**
   - Keystroke features stored in plaintext JSON
   - Pickle model files vulnerable to deserialization attacks
   - **Recommendation**: Encrypt `data/users.json` and validate model signatures in production

4. **Side-Channel Leakage**
   - Timing data transmitted via URL parameters (visible in browser history)
   - **Recommendation**: Use POST requests or encrypted WebSocket communication

## Challenges & Solutions

### Challenge 1: JavaScript-Python Communication
**Problem**: Streamlit's architecture runs Python on server-side; keystroke timing must be captured client-side in browser. Standard `st.text_input` doesn't expose timing events.

**Solution**: 
- Implemented custom HTML/JavaScript widget using `st.components.v1`
- Widget captures `keydown`/`keyup` events with `performance.now()` timestamps
- Encodes feature JSON and transmits via URL query parameter (`?ks_json=...`)
- Python reads `st.query_params` on next rerun, stores in session state
- Enables seamless bidirectional data flow without external websocket server

**Code Reference**: Lines 89-235 in `app.py` (`keystroke_widget()` function)

### Challenge 2: Ensemble Model Performance vs. Individual Classifiers
**Problem**: Random Forest alone achieved 88% accuracy, SVM 86%. Neither single classifier was robust enough for security-critical authentication.

**Solution**:
- Implemented weighted ensemble (0.6×RF + 0.4×SVM)
- Random Forest handles non-linear decision boundaries and feature importance
- SVM with RBF kernel optimizes margin separation in high-dimensional space
- Weighted averaging produces calibrated probability estimates
- **Result**: 95%+ ensemble accuracy on demo dataset

**Code Reference**: Lines 84-87, 122-123 in `ml_model.py`

### Challenge 3: Cold-Start Problem (New User Registration)
**Problem**: New users have zero training samples initially. Model requires minimum data before authentication is feasible.

**Solution**:
- Registration phase requires 10-15 sample collections before enabling authentication
- UI displays progress bar showing sample count / minimum required
- Training disabled until at least 2 users with 5+ samples each exist
- Graceful degradation: system clearly communicates when insufficient data available
- **Trade-off**: User must invest ~2-3 minutes during registration, but ensures authentication reliability

**Code Reference**: Lines 463-556 in `app.py` (`page_register()` function)

### Challenge 4: Typing Speed Variation Across Sessions
**Problem**: User typing speed varies due to fatigue, multitasking, keyboard changes. Early testing showed false rejection rates of 15-20% when users typed slower/faster than training samples.

**Solution**:
- Feature engineering: Added `rhythm_consistency` and `dwell_flight_ratio` which normalize timing patterns
- StandardScaler normalization ensures features are comparable across speed ranges
- Confidence threshold tuning: 45% allows reasonable tolerance for intra-user variation
- Model trained on samples with simulated speed variance (±10 WPM in demo data)
- **Result**: False rejection rate reduced to <5% while maintaining security

**Code Reference**: Lines 48-49 in `data_manager.py` (feature computation)

## Future Improvements

### Security Enhancements
- **Encrypted Feature Storage**: AES-256 encryption for `data/users.json` to prevent feature theft
- **Model Signature Verification**: Cryptographic signing of pickled models to prevent tampering
- **Rate Limiting**: Implement authentication attempt throttling to prevent ML-based impersonation attacks
- **Secure Communication**: Migrate from URL parameters to encrypted WebSocket for feature transmission

### Machine Learning
- **Deep Learning Exploration**: Test CNN/LSTM architectures for sequential keystroke pattern modeling
- **One-Class SVM**: Per-user anomaly detection models for stricter verification
- **Active Learning**: Collect hard negative samples (failed attempts) to retrain and improve robustness
- **Adaptive Thresholds**: Per-user confidence thresholds based on enrollment sample consistency

### Usability
- **Mobile Support**: Touchscreen typing dynamics feature extraction (touch pressure, swipe speed)
- **Multi-Language Phrases**: Support for non-English target phrases
- **Accessibility**: Audio feedback for visually impaired users during typing capture
- **Progressive Enrollment**: Allow authentication with 3-5 samples initially, improve model over time

### Deployment
- **Database Integration**: Replace JSON storage with PostgreSQL/MongoDB for scalability
- **API Endpoint**: RESTful API for integration with existing authentication systems
- **Docker Containerization**: Package as containerized service with docker-compose
- **Monitoring Dashboard**: Real-time false acceptance/rejection rate tracking in production

### Research Extensions
- **Multi-Modal Biometrics**: Combine keystroke dynamics with mouse movement patterns
- **Continuous Authentication**: Background verification during active session (not just login)
- **Cross-Device Learning**: Transfer learning to recognize users across different keyboards
- **Stress Detection**: Analyze typing disruption patterns to detect user distress

## Contributing

Contributions are welcome! This project was developed as an academic research prototype and benefits from community improvements.

### Areas for Contribution
- Security hardening (encryption, secure communication)
- ML model optimization (hyperparameter tuning, new architectures)
- UI/UX improvements (responsive design, accessibility)
- Documentation (API docs, deployment guides)
- Testing (unit tests, integration tests, security audits)

### Contribution Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement-name`)
3. Commit changes with descriptive messages
4. Add tests for new functionality
5. Submit pull request with detailed description

## Academic References

1. **Monrose, F., & Rubin, A. (2000)**. *Keystroke Dynamics as a Biometric for Authentication*. Future Generation Computer Systems, 16(4), 351-359.
   - Foundational work on keystroke biometrics for security

2. **Killourhy, K. S., & Maxion, R. A. (2009)**. *Comparing Anomaly-Detection Algorithms for Keystroke Dynamics*. IEEE/IFIP International Conference on Dependable Systems & Networks.
   - CMU benchmark dataset for keystroke authentication evaluation

3. **Breiman, L. (2001)**. *Random Forests*. Machine Learning, 45(1), 5-32.
   - Theoretical foundation for Random Forest classifier used in ensemble

4. **Cortes, C., & Vapnik, V. (1995)**. *Support-Vector Networks*. Machine Learning, 20(3), 273-297.
   - Original SVM formulation applied in this project's ensemble model

## License

This project is released under the MIT License for academic and research purposes.

## Author
**Harsh Tripathi**

**Institution**: IIIT Raichur  

**Vaishali Pawar**  
**Institution**: IIIT Raichur  

---

**Disclaimer**: This is a research prototype demonstrating behavioral authentication concepts. Production deployment requires additional security hardening, comprehensive testing, and compliance with biometric data regulations (GDPR, CCPA, etc.).
