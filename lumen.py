#!/usr/bin/env python3
"""Точка входа LUMEN: python lumen.py [run <file> | repl | version]"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from lumen.cli import main

if __name__ == "__main__":
    sys.exit(main())
