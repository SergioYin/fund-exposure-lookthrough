"""Tiny offline PEP 517 backend for this zero-dependency project."""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import tarfile
import time
import zipfile
from pathlib import Path


NAME = "fund-exposure-lookthrough"
MODULE = "fund_exposure_lookthrough"
VERSION = "0.1.0"
DIST = f"{NAME}-{VERSION}"
DIST_INFO = f"{NAME.replace('-', '_')}-{VERSION}.dist-info"
ROOT = Path(__file__).resolve().parent


def get_requires_for_build_wheel(config_settings=None):  # noqa: ANN001
    return []


def get_requires_for_build_sdist(config_settings=None):  # noqa: ANN001
    return []


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):  # noqa: ANN001
    dist_info = Path(metadata_directory) / DIST_INFO
    dist_info.mkdir(parents=True, exist_ok=True)
    (dist_info / "METADATA").write_text(_metadata(), encoding="utf-8")
    (dist_info / "WHEEL").write_text(_wheel_metadata(), encoding="utf-8")
    (dist_info / "entry_points.txt").write_text(_entry_points(), encoding="utf-8")
    return DIST_INFO


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):  # noqa: ANN001
    wheel_name = f"{NAME.replace('-', '_')}-{VERSION}-py3-none-any.whl"
    wheel_path = Path(wheel_directory) / wheel_name
    records: list[tuple[str, bytes]] = []

    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((ROOT / "src" / MODULE).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                rel = str(path.relative_to(ROOT / "src")).replace("\\", "/")
                data = path.read_bytes()
                _write_zip(archive, rel, data)
                records.append((rel, data))

        dist_files = {
            f"{DIST_INFO}/METADATA": _metadata().encode("utf-8"),
            f"{DIST_INFO}/WHEEL": _wheel_metadata().encode("utf-8"),
            f"{DIST_INFO}/entry_points.txt": _entry_points().encode("utf-8"),
        }
        for rel, data in dist_files.items():
            _write_zip(archive, rel, data)
            records.append((rel, data))

        record_rel = f"{DIST_INFO}/RECORD"
        record_data = _record(records, record_rel).encode("utf-8")
        _write_zip(archive, record_rel, record_data)

    return wheel_name


def build_sdist(sdist_directory, config_settings=None):  # noqa: ANN001
    sdist_name = f"{DIST}.tar.gz"
    sdist_path = Path(sdist_directory) / sdist_name
    include_roots = ["src", "tests", "examples", "demo", "skills"]
    include_files = ["README.md", "LICENSE", "CHANGELOG.md", "RELEASE_NOTES.md", "pyproject.toml", "build_backend.py", ".gitignore"]
    with tarfile.open(sdist_path, "w:gz") as archive:
        for root_name in include_roots:
            for path in sorted((ROOT / root_name).rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts:
                    archive.add(path, arcname=f"{DIST}/{path.relative_to(ROOT)}")
        for rel in include_files:
            archive.add(ROOT / rel, arcname=f"{DIST}/{rel}")
        info = tarfile.TarInfo(f"{DIST}/PKG-INFO")
        data = _metadata().encode("utf-8")
        info.size = len(data)
        info.mtime = 0
        archive.addfile(info, io.BytesIO(data))
    return sdist_name


def _metadata() -> str:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    return (
        "Metadata-Version: 2.3\n"
        f"Name: {NAME}\n"
        f"Version: {VERSION}\n"
        "Summary: Zero-dependency static fund look-through exposure analysis CLI.\n"
        "License-Expression: MIT\n"
        "Requires-Python: >=3.10\n"
        "Classifier: Development Status :: 3 - Alpha\n"
        "Classifier: Environment :: Console\n"
        "Classifier: License :: OSI Approved :: MIT License\n"
        "Classifier: Programming Language :: Python :: 3\n"
        "Classifier: Programming Language :: Python :: 3 :: Only\n"
        "Description-Content-Type: text/markdown\n"
        "\n"
        f"{readme}\n"
    )


def _wheel_metadata() -> str:
    return "Wheel-Version: 1.0\nGenerator: fund-exposure-lookthrough-build-backend\nRoot-Is-Purelib: true\nTag: py3-none-any\n"


def _entry_points() -> str:
    return "[console_scripts]\nfund-exposure-lookthrough = fund_exposure_lookthrough.cli:main\n"


def _write_zip(archive: zipfile.ZipFile, rel: str, data: bytes) -> None:
    info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def _record(records: list[tuple[str, bytes]], record_rel: str) -> str:
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    for rel, data in records:
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode("ascii")
        writer.writerow([rel, f"sha256={digest}", str(len(data))])
    writer.writerow([record_rel, "", ""])
    return output.getvalue()
