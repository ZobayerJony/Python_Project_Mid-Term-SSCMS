from pathlib import Path

APP_NAME = "SSCMS — Survivor Support & Case Management System"

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "data.json"
EXPORT_DIR = DATA_DIR / "exports"

DATE_FMT = "%Y-%m-%d"

VALID_STATUSES = ("Open", "In Progress", "Resolved", "Closed")
VALID_PRIORITIES = ("Low", "Medium", "High", "Urgent")
VALID_CASE_TYPES = ("Medical", "Legal", "Psychosocial", "Shelter", "Protection", "Other")

# UI defaults (used by UI layer)
DEFAULT_GEOMETRY = "1250x750"
MIN_SIZE = (1100, 650)