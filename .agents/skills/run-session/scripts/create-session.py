#!/usr/bin/env python3
"""Bootstrap one session from its ID and passwords supplied as JSON on stdin.

This file is part of Dichotomy.
This work is licensed under CC BY-NC-ND 4.0.
License: https://raw.githubusercontent.com/SteffenBlake/Dichotomy/refs/heads/main/LICENSE
"""

import sys

from manage import main

if __name__ == "__main__":
    sys.argv.insert(1, "create")
    main()
