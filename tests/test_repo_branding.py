from pathlib import Path


TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".txt",
    ".sh",
    ".ps1",
    ".toml",
    ".java",
    ".vue",
    ".js",
    ".ts",
    ".html",
    ".css",
    ".conf",
    ".properties",
    ".env",
    ".sql",
    ".xml",
    ".gradle",
    ".kts",
}

SKIP_DIRS = {
    ".git",
    ".worktrees",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    "target",
}


def _iter_repo_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in relative_parts):
            continue
        if path.name == "Dockerfile" or path.suffix in TEXT_SUFFIXES:
            yield path


def test_runtime_branding_uses_xuanwu_ai():
    root = Path(__file__).resolve().parents[1] / "main" / "xuanwu-device-server"
    config_text = (root / "config.yaml").read_text(encoding="utf-8")
    util_text = (root / "core" / "utils" / "util.py").read_text(encoding="utf-8")

    assert "玄武AI" in config_text
    assert "玄武AI" in util_text


def test_repo_text_files_do_not_contain_legacy_brand():
    root = Path(__file__).resolve().parents[1]
    offenders = []
    legacy_brand = "".join(["xiao", "zhi"])

    for path in _iter_repo_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if legacy_brand in text.lower():
            offenders.append(path.relative_to(root).as_posix())

    assert offenders == []
