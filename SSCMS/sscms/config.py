from pathlib import Path

APP_NAME = "SSCMS — Survivor Support & Case Management System"

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "data.json"
EXPORT_DIR = DATA_DIR / "exports"

DATE_FMT = "%Y-%m-%d"

VALID_STATUSES = ("Open", "In Progress", "Resolved", "Closed")
VALID_PRIORITIES = ("Low", "Medium", "High", "Urgent")
VALID_CASE_TYPES = ("Medical", "Legal", "Psychosocial", "Shelter", "Protection", "Other")

DEFAULT_GEOMETRY = "1250x750"
MIN_SIZE = (1100, 650)

# Admin login
ADMIN_USERNAME = "Zobayer"
ADMIN_PASSWORD = "zobayer1234"

# minor update for repository tracking