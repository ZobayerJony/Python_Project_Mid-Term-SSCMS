# SSCMS — Survivor Support and Case Management System (Midterm)

## Track
Track 2 — Desktop App (GUI)

## Project Name
Survivor Support and Case Management System (SSCMS)

## External Library Used
customtkinter (installed via pip)

## Environment Setup (Windows PowerShell)
1) Create venv:
   - `python -m venv .venv`

2) Activate venv:
   - `.\.venv\Scripts\Activate.ps1`

   If PowerShell blocks activation (Execution Policy error), run once:
   - `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

3) Install dependencies:
   - `pip install -r requirements.txt`

4) Run the project:
   - `python main.py`

5) Freeze requirements (for submission):
   - `pip freeze > requirements.txt`

## Project Features (Meets Midterm Requirements)
### Core Functionality
- CRUD: Add, View, Edit, Delete survivor cases
- Search: by Case ID / Survivor Name / Phone / Notes
- Sort/Filter: by Status / Priority / Case Type / Assigned Worker and sortable columns
- Summary Reports:
  - Total cases
  - Open vs Closed/Resolved count
  - Counts by status/priority/type
  - Top assigned workers
  - Average days open (open cases)

### Persistence
- JSON persistence: data saved in `data/data.json`
- Data survives program restart (load on startup, save on changes)
- Stable incremental IDs stored using `next_id`

### Validation & Robustness
- No crashes on invalid input
- Friendly validation errors:
  - required fields
  - phone format check
  - date format check (YYYY-MM-DD)
  - safe handling of empty search results

## OOP Design (4+ Classes)
1) Entity: `SurvivorCase` (+ `CaseActivity` for timeline)
2) Manager/Service: `CaseManager`
3) Storage: `JsonStore`
4) UI/Controller: `SSCMSApp` (GUI controller with views)

## Files Included for Submission
- Python source code under `sscms/`
- `main.py`
- `requirements.txt`
- `README_REPORT.md`
- Data file: `data/data.json` (auto created on first run) OR included sample

## Demo Proof (Screenshots to include: 3–5)
1) Cases list/table view + filters
2) Add Case form filled and saved
3) Search result example (search box)
4) Reports page showing summary stats
5) Edit/Delete action confirmation

## Notes
- App uses a clean UI layout with separate views for list/form/detail/report/export.
- Double-clicking a case row opens it for editing (if implemented in UI).