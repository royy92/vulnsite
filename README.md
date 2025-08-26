# VulnSite (Training)
Deliberately-vulnerable Django app for web PT demos (SQLi, Stored XSS, IDOR, Unrestricted Upload).

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
