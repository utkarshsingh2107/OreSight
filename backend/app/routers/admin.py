import io
import os
import sys
from contextlib import redirect_stdout

from fastapi import APIRouter

router = APIRouter()

SIH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if SIH_ROOT not in sys.path:
    sys.path.insert(0, SIH_ROOT)


@router.post("/admin/reset-demo")
def reset_demo():
    """
    Re-runs scripts/seed.py's reset+reload logic: wipes Balaghat's data and
    reloads it from the checked-in synthetic CSVs. Idempotent, safe to call
    repeatedly — this is the "Reset demo" button the blueprint calls
    essential (a demo will be run more than once).
    """
    import scripts.seed as seed_script  # imported lazily so app startup doesn't need scripts/

    buf = io.StringIO()
    with redirect_stdout(buf):
        seed_script.main()

    return {"status": "reset complete", "log": buf.getvalue().splitlines()}
