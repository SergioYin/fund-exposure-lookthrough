from pathlib import Path

from fund_exposure_lookthrough.cli import public_hygiene_findings
from fund_exposure_lookthrough.render import DISCLAIMER


ROOT = Path(__file__).resolve().parents[1]


def test_disclaimer_excludes_advice_and_trading_surface():
    lower = DISCLAIMER.lower()

    assert "not investment advice" in lower
    assert "target allocations" in lower
    assert "trades" in lower
    assert "user-supplied fixture data" in lower


def test_no_github_workflows_created():
    assert not (ROOT / ".github" / "workflows").exists()


def test_readme_states_static_boundaries():
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()

    assert "does not fetch live data" in readme
    assert "connect to brokers" in readme
    assert "recommend buys" in readme
    assert "predict returns" in readme


def test_release_metadata_includes_bundled_csv_package_data():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert "[tool.setuptools.package-data]" in pyproject
    assert 'fund_exposure_lookthrough = ["data/*.csv"]' in pyproject


def test_build_backend_version_matches_package_version():
    init_text = (ROOT / "src" / "fund_exposure_lookthrough" / "__init__.py").read_text(encoding="utf-8")
    backend_text = (ROOT / "build_backend.py").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert '__version__ = "0.4.0"' in init_text
    assert 'VERSION = "0.4.0"' in backend_text
    assert 'version = "0.4.0"' in pyproject


def test_public_hygiene_scan_detects_private_terms(tmp_path):
    private_term = "api" + "_key"
    (tmp_path / "README.md").write_text(f"contains {private_term} by mistake\n", encoding="utf-8")

    findings = public_hygiene_findings(tmp_path)

    assert findings == [f"README.md contains {private_term}"]
