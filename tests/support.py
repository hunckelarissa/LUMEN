import io
import sys

from lumen.interpreter import run_source


def run(code: str) -> str:
    captured = io.StringIO()
    previous = sys.stdout
    sys.stdout = captured
    try:
        run_source(code)
    finally:
        sys.stdout = previous
    return captured.getvalue().strip()
