import pathlib
import sys


def main() -> None:
    try:
        import win32serviceutil  # noqa: F401
    except ImportError as exc:  # pragma: no cover - packaging helper
        raise SystemExit("pywin32 is required to host XuanWuNearLinkBridge as a Windows service") from exc

    service_root = pathlib.Path(__file__).resolve().parents[2]
    if str(service_root) not in sys.path:
        sys.path.insert(0, str(service_root))
    from app import main as run_main

    run_main()


if __name__ == "__main__":
    main()
