# Parse Apache Access Log

You are given an access log file in Apache Combined Log Format at `/app/access.log`. 
Analyze the traffic and compute summary statistics.

## Requirements

Analyze the log file and produce a JSON report file saved to `/app/report.json` containing:

- **total_requests**: The total number of valid log lines (requests)
- **unique_ips**: The count of distinct client IP addresses
- **top_path**: The most frequently requested path (by count), as a string

## Input

The log file is located at `/app/access.log` and uses standard Apache Combined Log Format.

## Output Format

Write your report as a JSON object to `/app/report.json`:

```json
{
  "total_requests": <integer>,
  "unique_ips": <integer>,
  "top_path": "<string: most common request path>"
}
```

All three fields are required. The report will be verified for correctness.
