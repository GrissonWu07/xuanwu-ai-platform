from pathlib import Path


def test_manager_mobile_removed():
    root = Path(__file__).resolve().parents[1]
    assert not (root / "main" / "manager-mobile").exists()
    assert not (root / "docs" / "images" / "manager-mobile").exists()
    tracked_docs = [
        root / ".gitignore",
        root / "main" / "README.md",
        root / "main" / "README_en.md",
        root / "docs" / "python-first-refactor" / "README.md",
        root / "docs" / "python-first-refactor" / "fallback-config-center-and-java-sunset.md",
        root / "docs" / "python-first-refactor" / "java-sunset-checklist.md",
        root / "docs" / "python-first-refactor" / "protocol-and-interface-freeze.md",
    ]
    for doc in tracked_docs:
        content = doc.read_text(encoding="utf-8")
        assert "manager-mobile" not in content, doc
