-----

uvicorn app.main:app --reload

-------
# simple static server on port 5501
python -m http.server 5501

------

Open the app pages:

Login: http://127.0.0.1:5501/login.html

Dashboard: http://127.0.0.1:5501/dashboard.html

Competition: http://127.0.0.1:5501/competition.html

-------

/backend/
app/: All FastAPI logic, models, and database work.
main.py: FastAPI app instance, routers, CORS, etc.
models.py: SQLAlchemy models (Referee/Coach, Group, Children, Results, etc.).
database.py: DB connection and session.
schemas.py: Pydantic models for data validation.
crud.py: CRUD operations (create, read, update, delete).
deps.py: Dependency overrides (auth, get_db).
pdf_utils.py: PDF generation functions (using ReportLab, WeasyPrint, etc.).
tests/: Unit and integration tests for backend logic.
requirements.txt: All Python dependencies (FastAPI, SQLAlchemy, etc.).


/frontend/
HTML pages for user flows:
index.html: Landing page (maybe redirects to login).
login.html: Login for referees/coaches.
register.html: Registration page.
dashboard.html: After login, select/manage groups.
group.html: Create/edit group.
competition.html: Run a competition, input results.
results.html: Display results, download PDF.
css/: Styles.
styles.css: All styles here (can split if app grows).
js/: Scripts for each page/module.
main.js: Shared logic/utilities.
auth.js: Login/register handling.
group.js: Group-related logic.
competition.js: Competition logic.
results.js: Fetch and display results, trigger PDF download.

Root
.gitignore: Ignore .db, __pycache__, etc.
README.md: Project setup and instructions.

-----------------------------------------------
If you haven’t created a virtual environment, do this first: python -m venv venv
If you’re using a virtual environment (recommended!), activate it: .\venv\Scripts\activate
Install Requirements (Including Uvicorn) Install all dependencies from your requirements.txt: pip install -r requirements.txt

🎉 Perfect! Your FastAPI backend is now running and ready!
You can open your browser and go to:
http://127.0.0.1:8000/docs
to see the automatic interactive API documentation (Swagger UI).

Now your backend is ready for:
Registration
JWT Authentication
Group and Child management
Competition and results
PDF export of results

---------------------------------

Serve this with a simple static server (e.g., VS Code Live Server or python -m http.server 5500 inside frontend/).
Then set CORS on the backend to allow your frontend origin (e.g., http://127.0.0.1:5500).

--------------------------------------

How to run
Backend: already running at http://127.0.0.1:8000.

Frontend:

In frontend/, run: python -m http.server 5500
Open http://127.0.0.1:5500/login.html

Or use VS Code Live Server.

Flow:

Register → Login → Dashboard: create group & add children → Competition: create competition → enter results → Download PDF.

------------------------------------------------

git --version

--------------

Create a .gitignore so you don’t upload junk

# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd

# SQLite DBs
*.db

# Env / secrets
.env
*.env

# OS/editor
.DS_Store
Thumbs.db
.vscode/

# Frontend (if any later)
node_modules/
dist/

This keeps your virtualenv, DB, and secrets out of Git.

-------------

Initialize the repo locally

git init
git config user.name "Your Name"
git config user.email "you@example.com"
git status

--------------

First commit

git add .
git commit -m "Initial commit: backend + frontend"
--------------

Create the repo on GitHub

Go to https://github.com/new
Repository name: Gymnastic_competition (or any name you like)
Visibility: Public or Private
Do NOT add a README/.gitignore/license on GitHub (we already have local files).
Click Create repository.
Copy the HTTPS URL (looks like https://github.com/<you>/Gymnastic_competition.git).

Link your local repo to GitHub and push

git branch -M main
git remote add origin https://github.com/Midaugs/Gymnastic_competition.git
git push -u origin main