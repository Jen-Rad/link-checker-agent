# Web Scraping Agent - Link Checker

A comprehensive web scraping agent that crawls entire websites and generates detailed reports on broken and inactive links.

## Features

✅ **Site Crawling** - Automatically discovers all pages on a domain
✅ **Link Checking** - Tests every discovered link for availability
✅ **Detailed Reports** - JSON reports with actionable insights
✅ **Concurrent Requests** - Fast scanning with configurable parallelization
✅ **Error Handling** - Robust retry logic for failed requests
✅ **Web Interface** - Beautiful React UI for easy scanning
✅ **REST API** - Integrate with other tools and workflows

## Installation

### Prerequisites

- Python 3.8+
- pip or conda

### Setup

1. **Clone or download the files**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

For the web interface, you'll also need:
```bash
pip install flask flask-cors
```

## Usage

### Option 1: Command Line (Fastest)
```bash
python link_checker_agent.py
```

Follow the prompts to enter your website URL. The agent will:
1. Crawl the entire site
2. Check all discovered links
3. Generate a detailed JSON report
4. Print a summary to the console

**Example:**
```
Enter the website URL to scan: https://example.com
Starting link checker for: https://example.com

Crawling: https://example.com
Crawling: https://example.com/about
Crawling: https://example.com/services
...
Crawl complete: 45 pages, 320 unique links

Checking status of 320 links...

============================================================
LINK CHECK REPORT SUMMARY
============================================================
Site: https://example.com
Pages Scanned: 45
Total Unique Links: 320

Results:
  ✓ Active Links: 305
  ✗ Broken Links (404): 8
  ⚠ Inactive Links (4xx/5xx): 7
  ⚠ Error/Unchecked: 0

Top Broken Links:
  - https://example.com/old-page
    Status: 404, Found on 2 pages
```

### Option 2: REST API + Web Interface

**Start the API server:**
```bash
python api_server.py
```

The server will run on `http://localhost:5000`

**API Endpoints:**

- `POST /api/scan` - Start a new scan
```json
  {
    "url": "https://example.com"
  }
```

- `GET /api/scan/{scan_id}/status` - Check scan progress
  
- `GET /api/scan/{scan_id}/report` - Get the full report (once complete)

- `GET /api/scans` - List all scans

- `GET /api/health` - Health check

**Example API usage with curl:**
```bash
# Start a scan
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Response: {"scan_id": "scan_1234567890", "status": "started"}

# Check status
curl http://localhost:5000/api/scan/scan_1234567890/status

# Get report (when complete)
curl http://localhost:5000/api/scan/scan_1234567890/report
```

### Option 3: Python Module

Use the agent as a library in your own Python code:
```python
import asyncio
from link_checker_agent import LinkCheckerAgent

async def main():
    agent = LinkCheckerAgent("https://example.com")
    
    # Crawl the site
    await agent.crawl_site()
    
    # Check all links
    await agent.check_all_links()
    
    # Generate report
    report = agent.generate_report()
    agent.print_report_summary(report)

asyncio.run(main())
```

## Configuration

### Customize Agent Behavior
```python
agent = LinkCheckerAgent(
    base_url="https://example.com",
    max_retries=3,           # Retry failed requests up to 3 times
    timeout=10,              # 10 second timeout per request
    max_concurrent=5         # 5 concurrent requests at a time
)
```

**Important Parameters:**
- `max_concurrent`: Higher = faster but more resource usage. Start with 5-10
- `timeout`: Increase if scanning slow sites
- `max_retries`: More retries = slower but more reliable

## Report Structure

The generated `link_report.json` contains:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "site_url": "https://example.com",
  "domain": "example.com",
  "summary": {
    "total_pages_scanned": 45,
    "total_unique_links": 320,
    "broken_links": 8,
    "inactive_links": 7,
    "active_links": 305,
    "error_links": 0,
    "unchecked_links": 0
  },
  "broken_links": [
    {
      "url": "https://example.com/old-page",
      "status": 404,
      "found_on_pages": ["https://example.com/index"],
      "total_occurrences": 2
    }
  ],
  "inactive_links": [
    {
      "url": "https://example.com/maintenance",
      "status": 503,
      "found_on_pages": ["https://example.com/services"],
      "total_occurrences": 1
    }
  ],
  "error_links": [],
  "active_links_sample": [
    {
      "url": "https://example.com/about",
      "status": 200,
      "total_occurrences": 1
    }
  ]
}
```

## Interpreting Results

### Link Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| 200 | ✅ Link is active | No action needed |
| 301/302 | Redirect | May need updating |
| 404 | ❌ Page not found | Should be fixed |
| 403 | Forbidden | May require authentication |
| 500-599 | Server error | Check with site owner |
| None/Timeout | Error checking | Network/timeout issue |

### What to Fix First

1. **Broken Links (404)** - Links to deleted pages. Update or remove.
2. **Server Errors (5xx)** - Contact site owner or check server status.
3. **Timeouts** - May indicate slow/offline resources.

## Performance Tips

1. **For large sites (1000+ pages):**
   - Increase `max_concurrent` to 10-20
   - May take 10-30 minutes depending on site size

2. **For small sites (< 100 pages):**
   - Keep `max_concurrent` at 5-10
   - Should complete in 1-5 minutes

3. **Reduce memory usage:**
   - Lower `max_concurrent`
   - Run on a machine with at least 2GB RAM

4. **Respect server load:**
   - Don't set `max_concurrent` above 20
   - Consider adding delays between requests for very large scans

## Troubleshooting

### "Connection refused" or "Unable to connect"
- Verify the URL is correct and the site is online
- Check your internet connection

### Timeout errors
- Increase the `timeout` parameter
- Reduce `max_concurrent` (less parallel requests = less strain)

### Memory issues
- Reduce `max_concurrent` to 3-5
- Large sites may require multiple scans

### Missing links in report
- Some links may be loaded via JavaScript (not captured by BeautifulSoup)
- Consider using Selenium for JavaScript-heavy sites

## License

MIT License - Feel free to use and modify for your needs.

## Support

For issues or feature requests, please provide:
1. The URL you're scanning
2. Error messages or unexpected behavior
3. Your Python and package versions
