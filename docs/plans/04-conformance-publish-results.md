# Conformance Results Publishing
Status: planned (2026-01-08)
Owner: TBD

## 1) Summary
Add a reproducible, machine-readable conformance report artifact and a clear
publishing path for forks/plugins, without requiring any network services.

## 2) Goals
- Produce a stable JSON report with environment metadata.
- Support a CLI flag or command to write results to disk.
- Document how forks should publish results (e.g., in their repos/CI artifacts).

## 3) Non-goals
- Central hosting service or registry.
- Network uploads from the CLI.
- Changing conformance comparison logic.

## 4) Proposed report metadata
Include fields such as:
- git SHA (if available), repo dirty flag
- `calc_version`, `schema_version`, `rounding_policy_id`
- Python version, OS, timestamp (ISO 8601)

## 5) Diff-by-diff plan
1) Extend conformance reporting to include metadata:
   - Add a small helper in `opie/conformance/runner.py` or a new module
     (e.g., `opie/conformance/reporting.py`) to gather metadata.
   - Ensure JSON is emitted via `dumps_json` for determinism.
2) Add CLI support:
   - `opie conformance run --out <path>` (or `opie conformance publish`)
     that writes the full report JSON.
3) Documentation:
   - Add a short doc (e.g., `docs/conformance_publishing.md`) describing
     how forks/plugins should generate and publish results.
   - Add a README snippet with the command.
4) Tests:
   - Add tests verifying report JSON structure and determinism for the same run.

## 6) Acceptance criteria
- `opie conformance run --out results.json` writes a stable report with metadata.
- Report includes versions and environment context for traceability.
- Documentation shows how to publish results in CI artifacts.
