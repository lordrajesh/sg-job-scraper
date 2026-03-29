"""Pytest configuration: ensure project root is on sys.path."""

import os
import sys

# Insert project root so that 'models', 'merge', 'generate_data' are importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
