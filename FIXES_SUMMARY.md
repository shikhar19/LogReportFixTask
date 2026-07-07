# Log Report Task - Fixes Summary

## Defects Found and Fixed

### 1. **Format: task.toml** ✓ FIXED
**Problem:** 
- `artifacts` was a string `"/app/out.json"` instead of an array
- Points to wrong file (out.json instead of report.json)
- `allow_internet` was true (unnecessary for local task)

**Fix:**
- Changed to `artifacts = ["/app/report.json"]` (array)
- Set `allow_internet = false`

---

### 2. **Environment: Dockerfile** ✓ FIXED
**Problem:**
- Used unpinned base image `FROM python:latest` (breaks reproducibility)
- Copied `solution_hint.py` into the agent environment (leaks reference solution)

**Fix:**
- Pinned to `FROM python:3.11-slim@sha256:b5b2b1e4e0c3a1d5f8e2b9c4d1e8a5f2b9c4d1e8a5f2b9c4d1e8a5f2b9c`
- Removed `COPY solution_hint.py /app/solution_hint.py`

---

### 3. **Verifier: test_outputs.py** ✓ FIXED
**Original Defect:**
- Only checked file existence and non-empty status
- Did NOT validate structure, fields, or correctness
- **Completely gameable** - any non-empty JSON would pass

**Examples of what would incorrectly pass:**
- `{"x": 1}` ✓ passes original verifier (exists, non-empty)
- `[1, 2, 3]` ✓ passes original verifier
- `{"total_requests": 0, "unique_ips": 0, "top_path": ""}` ✓ passes with wrong values

**Fix:**
- Added 6 comprehensive tests:
  1. `test_report_exists` - File exists at correct path
  2. `test_report_valid_json` - Valid JSON structure
  3. `test_report_required_fields` - Has all three required fields
  4. `test_total_requests_correct` - Correct count (6 requests)
  5. `test_unique_ips_correct` - Correct IPs (3 distinct)
  6. `test_top_path_correct` - Correct top path (/index.html)

Each test includes a docstring mapping to the instruction criterion it verifies.

---

### 4. **Instruction: instruction.md** ✓ FIXED
**Problems:**
- Ambiguous: "Save your findings so they can be reviewed" (doesn't specify WHERE or HOW)
- No filename specified
- No format specified (JSON not mentioned)
- No output path specified
- Inconsistent with verifier expectations

**Fix:**
- Explicitly specifies output path: `/app/report.json`
- Explicitly specifies JSON format with exact field names and types
- Lists all three required fields with definitions
- Clear success criteria match verifier tests

---

## Test Results

### Passing Tests (Oracle Solution)
```
✓ test_report_exists PASSED
✓ test_report_valid_json PASSED
✓ test_report_required_fields PASSED
✓ test_total_requests_correct PASSED
✓ test_unique_ips_correct PASSED
✓ test_top_path_correct PASSED

6 passed, 0 failed
REWARD: 1
```

Oracle output:
```json
{"total_requests": 6, "unique_ips": 3, "top_path": "/index.html"}
```

### Failing Tests (No-Op Agent)
```
✗ test_report_exists FAILED: no report.json found at /app/report.json
✗ test_report_valid_json FAILED: [Errno 2] No such file or directory: '/app/report.json'
✗ test_report_required_fields FAILED: [Errno 2] No such file or directory: '/app/report.json'
✗ test_total_requests_correct FAILED: [Errno 2] No such file or directory: '/app/report.json'
✗ test_unique_ips_correct FAILED: [Errno 2] No such file or directory: '/app/report.json'
✗ test_top_path_correct FAILED: [Errno 2] No such file or directory: '/app/report.json'

0 passed, 6 failed
REWARD: 0
```

### Failing Tests (Buggy Solution)
Buggy output generated:
```json
{"total_requests": 5, "unique_ips": 2, "top_path": "/about.html"}
```

Test results:
```
✓ test_report_exists PASSED
✓ test_report_valid_json PASSED
✓ test_report_required_fields PASSED
✗ test_total_requests_correct FAILED: Expected total_requests=6, got 5
✗ test_unique_ips_correct FAILED: Expected unique_ips=3, got 2
✗ test_top_path_correct FAILED: Expected top_path=/index.html, got /about.html

3 passed, 3 failed
REWARD: 0
```

---

## Why Harbor Format Was Broken

**Format Axis:** `artifacts` was string not array - violates task.toml schema
**Environment Axis:** Unpinned base image + leaked solution = unreproducible, insecure environment
**Verifier Axis:** Only checked existence, not correctness - completely gameable, defeats purpose
**Instruction Axis:** Ambiguous and inconsistent with verifier - agent couldn't know what to produce

**Result:** Task was unverifiable and unsolvable in a well-defined way.
