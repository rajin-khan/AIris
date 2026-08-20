"""
AIris ablation-study runner.

Starts the backend with one component disabled so you can evaluate
Activity Guide or Scene Description under a controlled condition.

Examples:
    python ablate.py --noActiveGuidance
    python ablate.py --noHandTracking
    python ablate.py --noDepthHeuristic
    python ablate.py --noBLIP
    python ablate.py --noLLM
    python ablate.py --baseline
    python ablate.py --list
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from utils.ablation import CONDITIONS, apply_condition, get_ablation_flags


def print_conditions() -> None:
    print("\nAIris ablation conditions\n")
    print("Activity Guide (use the frontend Activity Guide tab):")
    for key in ("no_active_guidance", "no_hand_tracking", "no_depth_heuristic"):
        c = CONDITIONS[key]
        print(f"  {c['flag']:<22} {c['title']}")
        print(f"  {'':<22} disables: {c['disables']}")
    print("\nScene Description (use the frontend Scene Description tab):")
    for key in ("no_blip", "no_llm"):
        c = CONDITIONS[key]
        print(f"  {c['flag']:<22} {c['title']}")
        print(f"  {'':<22} disables: {c['disables']}")
    print("\n  --baseline             Full system (all components on)")
    print("\nUsage:")
    print("  python ablate.py --noActiveGuidance")
    print("  python ablate.py --noBLIP --port 8000")
    print()


def print_banner(condition_key: str | None, host: str, port: int) -> None:
    flags = get_ablation_flags()
    width = 68
    print("\n" + "=" * width)
    print("AIris Ablation Study")
    print("=" * width)
    if condition_key is None:
        print("Condition : baseline (all components on)")
        print("Service   : Activity Guide + Scene Description")
        print("Disabled  : nothing")
    else:
        meta = CONDITIONS[condition_key]
        print(f"Condition : {meta['title']}")
        print(f"Flag      : {meta['flag']}")
        print(f"Service   : {meta['service']}  ({meta['mode']} mode)")
        print(f"Disabled  : {meta['disables']}")
        print(f"Still on  : {meta['keeps']}")
    print("-" * width)
    print(f"Backend   : http://{host}:{port}")
    print("Frontend  : http://localhost:5173  (keep npm run dev running)")
    print()
    print("Stop any existing `python main.py` first (port 8000).")
    print("Run the matching mode in the UI, record success/time/notes,")
    print("then Ctrl+C and start the next condition.")
    print("=" * width)
    print(f"Active flags: {flags.describe()}")
    print("=" * width + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run AIris with one ablation condition enabled.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python ablate.py --noActiveGuidance\n"
            "  python ablate.py --noHandTracking\n"
            "  python ablate.py --noDepthHeuristic\n"
            "  python ablate.py --noBLIP\n"
            "  python ablate.py --noLLM\n"
            "  python ablate.py --baseline\n"
        ),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--noActiveGuidance",
        action="store_true",
        dest="no_active_guidance",
        help="No Active Guidance / No directional loop",
    )
    group.add_argument(
        "--noHandTracking",
        action="store_true",
        dest="no_hand_tracking",
        help="No Hand Tracking / MediaPipe off",
    )
    group.add_argument(
        "--noDepthHeuristic",
        action="store_true",
        dest="no_depth_heuristic",
        help="No depth heuristic / Area ratio forward/backoff",
    )
    group.add_argument(
        "--noBLIP",
        action="store_true",
        dest="no_blip",
        help="No BLIP / Captioning off",
    )
    group.add_argument(
        "--noLLM",
        action="store_true",
        dest="no_llm",
        help="No LLM / Groq/GPT-OSS off",
    )
    group.add_argument(
        "--baseline",
        action="store_true",
        help="Full system with every component enabled",
    )
    group.add_argument(
        "--list",
        action="store_true",
        help="Print ablation conditions and exit",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    return parser.parse_args()


def selected_condition(args: argparse.Namespace) -> str | None:
    for key in CONDITIONS:
        if getattr(args, key, False):
            return key
    return None


def main() -> None:
    args = parse_args()
    if args.list:
        print_conditions()
        return

    condition_key = selected_condition(args)
    apply_condition(condition_key)
    print_banner(condition_key, args.host, args.port)

    import uvicorn

    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
