from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from core.store.sqlalchemy_store import SQLAlchemyControlPlaneStore


def import_yaml_control_plane(source_root: str | Path, target_store: SQLAlchemyControlPlaneStore) -> None:
    source_root = Path(source_root)
    for yaml_path in sorted(source_root.rglob("*.yaml")):
        relative = yaml_path.relative_to(source_root)
        payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            continue
        target_store._write_yaml(target_store.root_dir / relative, payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Import YAML control plane data into PostgreSQL store.")
    parser.add_argument("source_root", help="Path to the existing YAML control plane directory")
    parser.add_argument("--pg-url", required=True, help="SQLAlchemy database URL")
    parser.add_argument("--schema", default="xw_mgmt", help="Target PostgreSQL schema name")
    args = parser.parse_args()

    store = SQLAlchemyControlPlaneStore.from_config(
        {
            "control-plane": {
                "backend": "postgres",
                "postgres": {"url": args.pg_url, "schema": args.schema},
            }
        }
    )
    try:
        import_yaml_control_plane(args.source_root, store)
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
