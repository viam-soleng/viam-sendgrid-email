#!/usr/bin/env python3
import sys
from pathlib import Path
import pytest

# Add the project root directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

def run_tests():
    """Run all pytest tests in the tests/ directory."""
    args = ["-xvs", "tests/", "--asyncio-mode=auto"]
    return pytest.main(args)

if __name__ == "__main__":
    sys.exit(run_tests())