#!/usr/bin/env python3

import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import main

if __name__ == "__main__":
    main() 