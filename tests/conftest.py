from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

API_BASE = "http://api.example.invalid"
ACCOUNT_ID = "user-1"
DEVICE_ID = "dev-1"
