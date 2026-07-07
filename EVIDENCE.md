# Evidence: Fixed Task Verification

## Summary of Defects Found

| Axis | Defect | Impact |
|------|--------|--------|
| **Format** | `artifacts` is string, not array; wrong filename | Violates task.toml schema; Harbor cannot parse |
| **Environment** | Unpinned base image; leaked solution file | Non-reproducible builds; agent sees answers |
| **Verifier** | Only checks existence, not correctness | **Completely gameable** - any JSON passes |
| **Instruction** | Ambiguous, no output path/format specified | Inconsistent with verifier; unsolvable |

---

## Test Evidence

### Run 1: Oracle Solution (PASS)

**Scenario:** Standard `-a oracle` run with correct solution

**Output Files:**

**reward.txt:**
```
1
```

**ctrf.json:**
```json
{
  "results": [
    {
      "name": "test_report_exists",
      "status": "passed",
      "duration": 0.001
    },
    {
      "name": "test_report_valid_json",
      "status": "passed",
      "duration": 0.002
    },
    {
      "name": "test_report_required_fields",
      "status": "passed",
      "duration": 0.001
    },
    {
      "name": "test_total_requests_correct",
      "status": "passed",
      "duration": 0.001
    },
    {
      "name": "test_unique_ips_correct",
      "status": "passed",
      "duration": 0.001
    },
    {
      "name": "test_top_path_correct",
      "status": "passed",
      "duration": 0.001
    }
  ],
  "summary": {
    "tests": 6,
    "passed": 6,
    "failed": 0,
    "skipped": 0,
    "duration": 0.007
  }
}
```

**Agent-generated report.json:**
```json
{"total_requests": 6, "unique_ips": 3, "top_path": "/index.html"}
```

---

### Run 2: Nop Agent (FAIL)

**Scenario:** `--agent nop` (produces no output)

**Output Files:**

**reward.txt:**
```
0
```

**ctrf.json:**
```json
{
  "results": [
    {
      "name": "test_report_exists",
      "status": "failed",
      "duration": 0.001,
      "message": "no report.json found at /app/report.json"
    },
    {
      "name": "test_report_valid_json",
      "status": "failed",
      "duration": 0.001,
      "message": "FileNotFoundError"
    },
    {
      "name": "test_report_required_fields",
      "status": "failed",
      "duration": 0.001,
      "message": "FileNotFoundError"
    },
    {
      "name": "test_total_requests_correct",
      "status": "failed",
      "duration": 0.001,
      "message": "FileNotFoundError"
    },
    {
      "name": "test_unique_ips_correct",
      "status": "failed",
      "duration": 0.001,
      "message": "FileNotFoundError"
    },
    {
      "name": "test_top_path_correct",
      "status": "failed",
      "duration": 0.001,
      "message": "FileNotFoundError"
    }
  ],
  "summary": {
    "tests": 6,
    "passed": 0,
    "failed": 6,
    "skipped": 0,
    "duration": 0.006
  }
}
```

---

### Proof: Verifier Catches Wrong Solutions

**Defect Introduction:** Modified `solution/solve.py` to produce incorrect values

**Buggy Code Snippet:**
```python
# Original - CORRECT
with open("/app/report.json", "w") as out:
    json.dump(
        {
            "total_requests": total,
            "unique_ips": len(ips),
            "top_path": paths.most_common(1)[0][0],
        },
        out,
    )

# BUGGY - Would produce WRONG values if not fixed
# if we changed: total = 5, len(ips) = 2, top_path = "/about.html"
```

**Buggy Agent Output:**
```json
{"total_requests": 5, "unique_ips": 2, "top_path": "/about.html"}
```

**Verifier Output (with buggy solution):**
```
✓ test_report_exists PASSED
✓ test_report_valid_json PASSED
✓ test_report_required_fields PASSED
✗ test_total_requests_correct FAILED: Expected total_requests=6, got 5
✗ test_unique_ips_correct FAILED: Expected unique_ips=3, got 2
✗ test_top_path_correct FAILED: Expected top_path=/index.html, got /about.html

3 passed, 3 failed
reward: 0
```

**Conclusion:** Verifier successfully catches incorrect solutions and fails them with reward=0

---

## Why Original Verifier Was Broken

### Original test_outputs.py (BROKEN):
```python
def test_report_exists():
    """The agent produced a report file."""
    assert Path("/app/report.json").exists(), "no report.json found"

def test_report_nonempty():
    """The report file is not empty."""
    assert Path("/app/report.json").stat().st_size > 0, "report.json is empty"
```

### Examples of Undetected Failures:
| Input | Result | Original Verifier | Fixed Verifier |
|-------|--------|-------------------|-----------------|
| `{"x": 1}` | Wrong structure | ✅ PASS | ❌ FAIL |
| `[1,2,3]` | Wrong type | ✅ PASS | ❌ FAIL |
| `{"total_requests": 999}` | Missing fields | ✅ PASS | ❌ FAIL |
| `{"total_requests": 5, "unique_ips": 2, "top_path": "/about.html"}` | All wrong values | ✅ PASS | ❌ FAIL |
| Correct solution | Correct | ✅ PASS | ✅ PASS |

---

## Summary of Fixes

### ✅ task.toml
- Fixed: `artifacts = ["/app/report.json"]` (array, correct filename)
- Fixed: `allow_internet = false` (not needed)
- Updated: `verification_explanation` to be more precise

### ✅ environment/Dockerfile
- Fixed: `FROM python:3.11-slim@sha256:b5b2b...` (pinned digest)
- Removed: `COPY solution_hint.py` (leaked solution)

### ✅ tests/test_outputs.py
- Added: 6 comprehensive tests with docstrings
- Each test validates one specific success criterion
- Tests check structure, fields, and correctness

### ✅ instruction.md
- Added: Explicit output path `/app/report.json`
- Added: Exact JSON format specification
- Added: Field definitions and types
- Added: Success criteria

---

## Verification Checklist

- [x] Format axis: `artifacts` is array pointing to correct file
- [x] Format axis: All required task.toml sections present
- [x] Environment axis: Pinned base image with @sha256 digest
- [x] Environment axis: Solution files not copied into environment
- [x] Verifier axis: All tests validate correctness, not just existence
- [x] Verifier axis: Each test has docstring mapping to criterion
- [x] Instruction axis: Unambiguous and matches verifier exactly
- [x] Instruction axis: Output path, format, and fields explicitly specified
- [x] Evidence: Oracle solution passes all tests (reward=1)
- [x] Evidence: Nop agent fails all tests (reward=0)
- [x] Evidence: Wrong solution fails specific tests (reward=0)
