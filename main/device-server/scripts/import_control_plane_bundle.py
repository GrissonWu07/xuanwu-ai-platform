from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.control_plane.import_bundle import import_control_plane_bundle
from core.control_plane.local_store import LocalControlPlaneStore


def _load_bundle(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def main():
    parser = argparse.ArgumentParser(
        description="Import a control-plane bundle into local YAML storage.",
    )
    parser.add_argument("bundle", help="Path to a JSON or YAML bundle file")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Target control-plane data directory (defaults to data/control_plane)",
    )
    args = parser.parse_args()

    bundle_path = Path(args.bundle).resolve()
    output_dir = Path(args.output_dir).resolve() if args.output_dir else None
    store = LocalControlPlaneStore(output_dir or PROJECT_ROOT / "data" / "control_plane")
    summary = import_control_plane_bundle(store, _load_bundle(bundle_path))
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
