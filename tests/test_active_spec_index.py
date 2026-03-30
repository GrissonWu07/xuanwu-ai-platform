from pathlib import Path


def test_active_spec_index_points_to_xuanwu_platform_blueprint():
    readme_path = Path(__file__).resolve().parents[1] / "docs" / "superpowers" / "specs" / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    assert "XuanWu Platform Blueprint" in content
    assert "2026-03-30-xuanwu-platform-blueprint.md" in content


def test_python_first_readme_marks_legacy_docs_as_archived():
    readme_path = Path(__file__).resolve().parents[1] / "docs" / "python-first-refactor" / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    assert "归档" in content or "archived" in content.lower()
    assert "docs/superpowers/specs/2026-03-30-xuanwu-platform-blueprint.md" in content
