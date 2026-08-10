#!/usr/bin/env python3
"""Build a deterministic, directly installable skill archive."""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = PROJECT_ROOT / "skill" / "interpersonal-strategist"
DIST_DIR = PROJECT_ROOT / "dist"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import is_generated_python_cache, validate_repository  # noqa: E402


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def distributable_files(skill_dir: Path = SKILL_DIR) -> list[Path]:
    return sorted(
        path
        for path in skill_dir.rglob("*")
        if path.is_file()
        and not is_generated_python_cache(path.relative_to(skill_dir))
    )


def build_archive() -> tuple[Path, Path, Path]:
    errors = validate_repository(PROJECT_ROOT)
    if errors:
        raise RuntimeError("validation failed before packaging:\n- " + "\n- ".join(errors))

    version = (PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip()
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    archive = DIST_DIR / f"interpersonal-strategist-{version}.zip"
    checksum = archive.with_suffix(archive.suffix + ".sha256")
    manifest_path = DIST_DIR / f"interpersonal-strategist-{version}.manifest.json"

    files = distributable_files()
    manifest_files: list[dict[str, object]] = []

    entries: list[tuple[str, bytes]] = []
    for path in files:
        relative = path.relative_to(SKILL_DIR)
        archive_name = Path("interpersonal-strategist") / relative
        data = path.read_bytes()
        entries.append((str(archive_name), data))
        manifest_files.append(
            {
                "path": str(archive_name),
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )

    internal_manifest = {
        "schema_version": "1.0",
        "name": "interpersonal-strategist",
        "version": version,
        "files": manifest_files,
    }
    internal_manifest_data = (
        json.dumps(internal_manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    entries.append(
        (
            "interpersonal-strategist/PACKAGE_MANIFEST.json",
            internal_manifest_data,
        )
    )

    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as zf:
        for archive_name, data in sorted(entries):
            info = zipfile.ZipInfo(str(archive_name), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            zf.writestr(info, data)

    archive_sha = sha256_bytes(archive.read_bytes())
    checksum.write_text(f"{archive_sha}  {archive.name}\n", encoding="utf-8")
    manifest = dict(internal_manifest)
    manifest.update({"archive": archive.name, "archive_sha256": archive_sha})
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return archive, checksum, manifest_path


def main() -> int:
    try:
        archive, checksum, manifest = build_archive()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "pass",
                "archive": str(archive),
                "checksum": str(checksum),
                "manifest": str(manifest),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
