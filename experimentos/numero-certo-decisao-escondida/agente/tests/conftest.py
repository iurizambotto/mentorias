import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent / "skills"
for scripts in SKILLS.glob("*/scripts"):
    sys.path.insert(0, str(scripts))
