# EVO HASH: NeuroEvolution Augmented Hashing Mechanism

## 📌 Project Overview

Traditional password protection relies on hashing (e.g., SHA, MD5) combined with salts. However, these methods are still vulnerable to brute-force, rainbow tables, and database leaks. Our project introduces **EVO HASH**, a novel authentication mechanism that replaces salts with an intelligent **NEAT (NeuroEvolution of Augmenting Topologies)**-based transformation layer.

Each user is assigned a unique NEAT model that transforms their password into an unpredictable but deterministic output before hashing. This output is then securely stored in the database. During authentication, the same NEAT model verifies the password.

This approach removes the need for salts, simplifies architecture, and adds an AI-powered security layer resistant to offline brute-force attacks.

---

## 🚀 Key Highlights

* **Saltless Authentication**: No salt management needed.
* **ML Transformation Layer**: Password → NEAT Model → Output → Hash → DB.
* **Per-User Model**: Each user is mapped to a unique NEAT model.
* **Stronger Defense**: Even if the database leaks, attackers require the NEAT model to validate.
* **FastAPI Backend** with modular and scalable design.

---

## 🛠️ Tech Stack

* **Backend**: Python, FastAPI
* **Machine Learning**: NEAT-Python
* **Libraries**: NumPy, hashlib, pickle, SQLAlchemy
* **Frontend**: HTML, CSS, JavaScript (Jinja2 Templates)
* **Database**: SQLite
* **Deployment**: Vercel / Local

---

## 📂 Project Structure

```
├── main.py                # FastAPI application
├── database.py            # Database models & connection
├── config-feedforward.txt # NEAT configuration file
├── models/                # Stored NEAT models per user
├── templates/             # Jinja2 HTML templates
│   ├── login.html
│   ├── register.html
│   ├── admin_login.html
│   └── admin_dashboard.html
└── README.md              # Project documentation
```

---

## ⚙️ Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/evo-hash.git
   cd evo-hash
   ```

2. **Create virtual environment & install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/Mac
   venv\Scripts\activate      # On Windows
   pip install -r requirements.txt
   ```

3. **Run the server**

   ```bash
   uvicorn main:app --reload
   ```

4. **Access the app**

   * Register: `http://127.0.0.1:8000/register`
   * Login: `http://127.0.0.1:8000/login`
   * Admin Dashboard: `http://127.0.0.1:8000/admin/dashboard`

---

## 🔐 Authentication Flow

1. **Registration**

   * A new NEAT model is generated per user.
   * User password → NEAT transformation → SHA256 hash stored in DB.

2. **Login**

   * Input password is transformed using user’s NEAT model.
   * Transformed output is hashed and compared with stored hash.
   * If match → user authenticated.

---

## 📖 Example Use Case

* In 2012, LinkedIn leaked **6.5M passwords** due to weak SHA-1 hashing without proper salting.
* In 2025, **16B+ credentials leaked** in MOAB breach, highlighting failure of deterministic hashing.
* EVO HASH mitigates these risks by requiring both **DB + ML model** for verification, adding a strong barrier against offline brute-force attacks.

---

## 📚 References

* Kulkarni, V. R. et al. *Hash Function Implementation Using Artificial Neural Network*
* Matheus Gomes Cordeiro et al. *A Minimal Training Strategy to Play Flappy Bird Indefinitely with NEAT*

---

## ✅ Conclusion

EVO HASH introduces a **deterministic yet unpredictable password obfuscation layer** using NEAT. This fusion of AI and security:

* Enhances password protection.
* Removes complexity of salts.
* Improves resilience against breaches.
* Provides a scalable and adaptive authentication system.

---

### 🔒 "EVO HASH – Reinventing Password Security with AI"
