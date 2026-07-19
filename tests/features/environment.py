import os
from pathlib import Path


def before_scenario(context, scenario):
    # Network-gated: integration scenarios that hit LinkedIn are skipped offline.
    context.network = os.environ.get("BALALIKA_NETWORK") == "1"
    # tests/features/environment.py -> tests/fixtures/debug_response.html.example
    context.fixture = Path(__file__).resolve().parent.parent / "fixtures" / "debug_response.html.example"
