#!/usr/bin/env python3
"""Fixed player command. Players must never read or edit this implementation.

This file is part of Dichotomy.
This work is licensed under CC BY-NC-ND 4.0.
License: https://raw.githubusercontent.com/SteffenBlake/Dichotomy/refs/heads/main/LICENSE
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from client import run

if __name__ == '__main__':
    run('start_chapter', player='Johnny')
