from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from quantum_folk_lab.quantum.ibm_runtime import load_api_token, run_hardware_smoke


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded EXP-007 IBM hardware smoke test.")
    parser.add_argument("--credential-file", required=True, type=Path)
    parser.add_argument("--shots", default=256, type=int)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--confirm-qpu", action="store_true")
    args = parser.parse_args()

    try:
        token = load_api_token(args.credential_file)
        result = run_hardware_smoke(token=token, shots=args.shots, confirm_qpu=args.confirm_qpu)
        payload = json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n"
        if args.output is not None:
            args.output.write_text(payload, encoding="utf-8", newline="\n")
        print(payload, end="")
        return 0
    except Exception as exc:  # provider errors must never be reproduced verbatim
        print(f"IBM smoke test failed safely ({type(exc).__name__}).", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
