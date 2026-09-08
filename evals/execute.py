#!/usr/bin/env python3
"""Bounded runner for a user-supplied JSON adapter. Dry-run is the default.

Adapter input is one JSON object on stdin: run_id, condition, prompt, subject.
Output is {"response": "...", "receipt": {...}}. Receipt claims need host review.
No shell, network client, keys, automatic retries, or model choice is bundled.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import selectors
import subprocess
import sys
import time
from pathlib import Path

from eval_integrity import digest, jsonl, validate_plan


def invoke(argv: list[str], request: dict, *, timeout: float, limit: int) -> dict:
    if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or not a for a in argv):
        raise ValueError("adapter command must be a non-empty JSON string array")
    import os
    if os.name != "posix":
        raise ValueError("the bounded adapter runner currently supports POSIX hosts only")
    if timeout <= 0 or limit < 1:
        raise ValueError("adapter limits must be positive")
    started = time.monotonic()
    # Use a temporary input file to avoid blocking on a large prompt before output is read.
    import tempfile
    with tempfile.TemporaryFile() as source:
        source.write((json.dumps(request, ensure_ascii=False) + "\n").encode()); source.seek(0)
        process = subprocess.Popen(argv, stdin=source, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=False, start_new_session=True)
        buffers = {"stdout": bytearray(), "stderr": bytearray()}
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ, "stdout")
                selector.register(process.stderr, selectors.EVENT_READ, "stderr")
                while selector.get_map():
                    remaining = timeout - (time.monotonic() - started)
                    if remaining <= 0:
                        raise ValueError("adapter timeout")
                    for key, _ in selector.select(min(remaining, 0.2)):
                        chunk = key.fileobj.read1(8192)
                        if not chunk:
                            selector.unregister(key.fileobj)
                        else:
                            buffers[key.data].extend(chunk)
                            if sum(map(len, buffers.values())) > limit:
                                raise ValueError("adapter output limit exceeded")
                status = process.wait(timeout=max(0.01, timeout - (time.monotonic() - started)))
                if status != 0:
                    # Do not print adapter stderr: it can contain credentials or private prompts.
                    raise ValueError(f"adapter exited with status {status}")
                result = json.loads(buffers["stdout"].decode("utf-8"))
                if not isinstance(result, dict) or not isinstance(result.get("response"), str) or not result["response"].strip():
                    raise ValueError("adapter must return non-empty response text")
                receipt = result.get("receipt")
                if not isinstance(receipt, dict):
                    raise ValueError("adapter must return a receipt object (unverified unless attested)")
                return {"response": result["response"], "receipt": receipt,
                        "elapsed_seconds": round(time.monotonic() - started, 3)}
        finally:
            # Kill descendants even if the parent already exited but left pipes open.
            import signal
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
            if process.stdout: process.stdout.close()
            if process.stderr: process.stderr.close()


def execute(plan_path: Path, manifests: list[Path], output: Path, command: list[str],
            *, allow_execution: bool = False, max_runs: int = 20, timeout: float = 120,
            output_limit: int = 1_000_000) -> dict:
    if max_runs < 1 or timeout <= 0 or output_limit < 1:
        raise ValueError("run, timeout, and output limits must be positive")
    plan = json.loads(plan_path.read_text()); validate_plan(plan)
    expected_hashes = sorted(m["sha256"] for m in plan["manifests"])
    if sorted(digest(p) for p in manifests) != expected_hashes:
        raise ValueError("prompt manifests do not match frozen plan")
    inputs = {}
    for path in manifests:
        for row in jsonl(path):
            if row["run_id"] in inputs:
                raise ValueError("duplicate input run")
            inputs[row["run_id"]] = row
    if set(inputs) != {r["run_id"] for r in plan["planned_runs"]}:
        raise ValueError("input manifests differ from planned runs")
    existing = jsonl(output) if output.exists() else []
    seen = {r["run_id"] for r in existing}
    if len(seen) != len(existing) or not seen <= set(inputs):
        raise ValueError("output contains duplicate or unplanned runs")
    if any(r.get("plan_sha256") != digest(plan_path) for r in existing):
        raise ValueError("existing output belongs to a different run plan")
    pending = [r for r in plan["planned_runs"] if r["run_id"] not in seen]
    chosen = pending[:max_runs]
    report = {"status": "dry_run", "planned": len(plan["planned_runs"]), "already_recorded": len(seen),
              "selected": len(chosen), "remaining_after_selection": len(pending) - len(chosen),
              "automatic_retries": 0, "plan_sha256": digest(plan_path)}
    if not allow_execution:
        return report
    output.parent.mkdir(parents=True, exist_ok=True)
    completed, failed = 0, 0
    with output.open("a", encoding="utf-8") as stream:
        for row in chosen:
            source = inputs[row["run_id"]]
            if hashlib.sha256(source["prompt"].encode()).hexdigest() != row["prompt_sha256"]:
                raise ValueError("prompt bytes do not match planned hash")
            record = {**row, "plan_sha256": digest(plan_path),
                      "blind_id": hashlib.sha256(row["run_id"].encode()).hexdigest()[:20]}
            try:
                result = invoke(command, {"run_id": row["run_id"], "condition": row["condition"],
                    "prompt": source["prompt"], "subject": plan["subject"]}, timeout=timeout, limit=output_limit)
                record.update(result, status="completed"); completed += 1
            except (OSError, ValueError, subprocess.SubprocessError, UnicodeError):
                # Keep an operational failure, not an exception potentially containing source data.
                record.update(status="failed", reason="Adapter execution or response contract failed; inspect privately.")
                failed += 1
            stream.write(json.dumps(record, ensure_ascii=False) + "\n"); stream.flush()
            if failed:
                break  # No automatic repair/retry loop; preserve remaining runs as unobserved.
    report.update(status="recorded", completed=completed, failed=failed,
                  remaining=len(pending) - completed - failed,
                  host_attestation="not_established_by_this_runner")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--command-json", default="[]", help="Trusted adapter argv; never shell text")
    parser.add_argument("--allow-execution", action="store_true")
    parser.add_argument("--max-runs", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--output-limit", type=int, default=1_000_000)
    args = parser.parse_args()
    try:
        report = execute(args.plan, args.manifest, args.output, json.loads(args.command_json),
            allow_execution=args.allow_execution, max_runs=args.max_runs, timeout=args.timeout, output_limit=args.output_limit)
        print(json.dumps(report, indent=2)); return int(bool(report.get("failed")))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)})); return 1


if __name__ == "__main__":
    sys.exit(main())
