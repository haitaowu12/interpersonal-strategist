#!/usr/bin/env python3
"""Verify promoted evidence identities without redistributing source text.

Offline mode validates registry structure and stable-identity syntax. Online mode
uses NCBI PubMed, Crossref, DOI resolution, and official-document URLs to compare
source identity metadata. Network verification is a release gate, not a runtime
dependency.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "provenance" / "evidence-sources.json"
USER_AGENT = "interpersonal-strategist-evidence-check/0.10.0-rc.1"
PMID_PATTERN = re.compile(r"PMID (\d+)")
DOI_PATTERN = re.compile(r"DOI ([^;]+)")
OFFICIAL_URLS = {
    "PRACTICE-01": "https://www.acas.org.uk/acas-guide-to-challenging-conversations-and-how-to-manage-them",
}


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", ascii_text.casefold()))


def title_similarity(expected: str, actual: str) -> float:
    left = normalize(expected)
    right = normalize(actual)
    if not left or not right:
        return 0.0
    if left in right or right in left:
        return 1.0
    sequence = difflib.SequenceMatcher(None, left, right).ratio()
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    overlap = len(left_tokens & right_tokens) / max(1, len(left_tokens | right_tokens))
    return max(sequence, overlap)


def request_json(url: str, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("response was not a JSON object")
    return payload


def request_status(url: str, timeout: float) -> tuple[int, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        body = response.read(50_000) if "text" in content_type or "html" in content_type else b""
        return response.status, body.decode("utf-8", errors="ignore")


def extract_year(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r"(?:19|20)\d{2}", value)
        return int(match.group(0)) if match else None
    return None


def verify_pubmed(pmid: str, timeout: float) -> dict[str, Any]:
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        f"?db=pubmed&id={urllib.parse.quote(pmid)}&retmode=json"
    )
    payload = request_json(url, timeout)
    result = payload.get("result", {}).get(pmid, {})
    if not isinstance(result, dict) or not result:
        raise ValueError("PubMed record not found")
    authors = result.get("authors", [])
    first_author = ""
    if authors and isinstance(authors[0], dict):
        first_author = str(authors[0].get("name", "")).split()[0]
    return {
        "source": "NCBI PubMed",
        "url": url,
        "title": result.get("title", ""),
        "first_author": first_author,
        "year": extract_year(result.get("pubdate")),
        "doi": next(
            (
                item.get("value")
                for item in result.get("articleids", [])
                if isinstance(item, dict) and item.get("idtype") == "doi"
            ),
            None,
        ),
    }


def verify_crossref(doi: str, timeout: float) -> dict[str, Any]:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    payload = request_json(url, timeout)
    message = payload.get("message", {})
    if not isinstance(message, dict):
        raise ValueError("Crossref record not found")
    titles = message.get("title", [])
    title = titles[0] if isinstance(titles, list) and titles else ""
    authors = message.get("author", [])
    first_author = ""
    if isinstance(authors, list) and authors and isinstance(authors[0], dict):
        first_author = authors[0].get("family") or authors[0].get("name") or ""
    year: int | None = None
    for key in ("published-print", "published", "published-online", "issued", "created"):
        value = message.get(key)
        if isinstance(value, dict):
            parts = value.get("date-parts")
            if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
                year = extract_year(parts[0][0])
                if year:
                    break
    return {
        "source": "Crossref",
        "url": url,
        "title": title,
        "first_author": str(first_author),
        "year": year,
        "doi": message.get("DOI"),
    }


def compare_metadata(source: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    expected_author = normalize(str(source["first_author"]))
    actual_author = normalize(str(actual.get("first_author", "")))
    author_match = bool(
        expected_author
        and actual_author
        and (
            expected_author in actual_author
            or actual_author in expected_author
            or expected_author == "nist" and "national institute" in actual_author
        )
    )
    similarity = title_similarity(str(source["title"]), str(actual.get("title", "")))
    expected_year = int(source["year"])
    actual_year = actual.get("year")
    year_match = isinstance(actual_year, int) and abs(expected_year - actual_year) <= 1
    return {
        "author_match": author_match,
        "title_similarity": round(similarity, 4),
        "title_match": similarity >= 0.62,
        "year_match": year_match,
        "actual": actual,
    }


def validate_registry(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        return ["registry sources must be a non-empty list"]
    ids: set[str] = set()
    required = {
        "id",
        "first_author",
        "year",
        "title",
        "stable_identity",
        "evidence_type",
        "permitted_claim",
        "limitation",
        "runtime_rule",
        "last_verified",
        "license_note",
    }
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"source {index} is not an object")
            continue
        missing = required - set(source)
        if missing:
            errors.append(
                f"source {source.get('id', index)!r} missing: {', '.join(sorted(missing))}"
            )
            continue
        source_id = source["id"]
        if source_id in ids:
            errors.append(f"duplicate source id: {source_id}")
        ids.add(source_id)
        identity = str(source["stable_identity"])
        if not (PMID_PATTERN.search(identity) or DOI_PATTERN.search(identity) or source_id in OFFICIAL_URLS):
            errors.append(f"{source_id}: no resolvable PMID, DOI, or official URL")
    return errors


def verify_source(source: dict[str, Any], timeout: float) -> dict[str, Any]:
    source_id = source["id"]
    identity = str(source["stable_identity"])
    pmid_match = PMID_PATTERN.search(identity)
    doi_match = DOI_PATTERN.search(identity)
    attempts: list[dict[str, Any]] = []

    if pmid_match:
        try:
            actual = verify_pubmed(pmid_match.group(1), timeout)
            comparison = compare_metadata(source, actual)
            attempts.append({"method": "pubmed", "status": "resolved", **comparison})
            if comparison["author_match"] and comparison["title_match"] and comparison["year_match"]:
                return {"id": source_id, "status": "pass", "attempts": attempts}
        except (OSError, ValueError, KeyError, urllib.error.URLError) as exc:
            attempts.append({"method": "pubmed", "status": "error", "error": str(exc)})

    if doi_match:
        doi = doi_match.group(1).strip()
        try:
            actual = verify_crossref(doi, timeout)
            comparison = compare_metadata(source, actual)
            attempts.append({"method": "crossref", "status": "resolved", **comparison})
            if comparison["author_match"] and comparison["title_match"] and comparison["year_match"]:
                return {"id": source_id, "status": "pass", "attempts": attempts}
        except (OSError, ValueError, KeyError, urllib.error.URLError) as exc:
            attempts.append({"method": "crossref", "status": "error", "error": str(exc)})

        try:
            status, _ = request_status("https://doi.org/" + urllib.parse.quote(doi), timeout)
            attempts.append(
                {
                    "method": "doi-resolution",
                    "status": "resolved" if 200 <= status < 400 else "error",
                    "http_status": status,
                }
            )
        except (OSError, urllib.error.URLError) as exc:
            attempts.append({"method": "doi-resolution", "status": "error", "error": str(exc)})

    official_url = OFFICIAL_URLS.get(source_id)
    if official_url:
        try:
            status, body = request_status(official_url, timeout)
            title_tokens = [
                token for token in normalize(str(source["title"])).split() if len(token) > 4
            ]
            page = normalize(body)
            matched = sum(token in page for token in title_tokens)
            title_match = bool(title_tokens) and matched / len(title_tokens) >= 0.5
            attempts.append(
                {
                    "method": "official-url",
                    "status": "resolved",
                    "url": official_url,
                    "http_status": status,
                    "title_match": title_match,
                }
            )
            if 200 <= status < 400 and title_match:
                return {"id": source_id, "status": "pass", "attempts": attempts}
        except (OSError, urllib.error.URLError) as exc:
            attempts.append({"method": "official-url", "status": "error", "error": str(exc)})

    return {"id": source_id, "status": "fail", "attempts": attempts}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--allow-unresolved", action="store_true")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--delay", type=float, default=0.1)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        payload = json.loads(args.registry.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1

    registry_errors = validate_registry(payload)
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "registry": str(args.registry),
        "mode": "offline" if args.offline else "online",
        "registry_errors": registry_errors,
        "sources": [],
    }

    if not registry_errors and not args.offline:
        for source in payload["sources"]:
            report["sources"].append(verify_source(source, args.timeout))
            if args.delay:
                time.sleep(args.delay)

    failed = registry_errors or any(
        item.get("status") != "pass" for item in report["sources"]
    )
    report["status"] = "fail" if failed else "pass"
    report["source_count"] = len(payload.get("sources", []))
    report["pass_count"] = sum(
        item.get("status") == "pass" for item in report["sources"]
    )
    report["fail_count"] = sum(
        item.get("status") != "pass" for item in report["sources"]
    )

    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not failed or args.allow_unresolved else 1


if __name__ == "__main__":
    sys.exit(main())
