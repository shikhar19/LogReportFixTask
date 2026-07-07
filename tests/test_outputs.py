import json
from pathlib import Path


def test_report_exists():
    """Criterion: Agent produces output file at /app/report.json"""
    assert Path("/app/report.json").exists(), "no report.json found at /app/report.json"


def test_report_valid_json():
    """Criterion: Output is valid JSON format"""
    try:
        with open("/app/report.json") as f:
            json.load(f)
    except json.JSONDecodeError as e:
        raise AssertionError(f"report.json is not valid JSON: {e}")


def test_report_required_fields():
    """Criterion: Report contains all required fields (total_requests, unique_ips, top_path)"""
    with open("/app/report.json") as f:
        report = json.load(f)
    
    required_fields = {"total_requests", "unique_ips", "top_path"}
    missing = required_fields - set(report.keys())
    assert not missing, f"Missing required fields: {missing}"


def test_total_requests_correct():
    """Criterion: total_requests equals correct count (6 lines in access.log)"""
    with open("/app/report.json") as f:
        report = json.load(f)
    
    assert report["total_requests"] == 6, f"Expected total_requests=6, got {report['total_requests']}"


def test_unique_ips_correct():
    """Criterion: unique_ips equals correct count (3 distinct IPs: 192.168.0.1, 192.168.0.2, 10.0.0.5)"""
    with open("/app/report.json") as f:
        report = json.load(f)
    
    assert report["unique_ips"] == 3, f"Expected unique_ips=3, got {report['unique_ips']}"


def test_top_path_correct():
    """Criterion: top_path is the most frequently requested path (/index.html appears 3 times)"""
    with open("/app/report.json") as f:
        report = json.load(f)
    
    assert report["top_path"] == "/index.html", f"Expected top_path=/index.html, got {report['top_path']}"
