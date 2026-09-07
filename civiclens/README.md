# CivicLens Kenya

Evidence-first civic data analysis dashboard built with Flask.

## Local
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py

## GitHub
Create an empty repository, then:
git init
git add .
git commit -m "Initial CivicLens project"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main

## Render
Connect the GitHub repository as a Web Service. Build command: `pip install -r requirements.txt`. Start command: `gunicorn app:app`. The included render.yaml can configure this automatically.

IMPORTANT: The included leader values are illustrative. Before publishing real political analysis, implement official-source collectors, validation, timestamps, source links, and a review/audit workflow.
