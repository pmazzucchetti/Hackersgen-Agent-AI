"""Make scuola/ importable the same way the server imports its own modules."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scuola"))
