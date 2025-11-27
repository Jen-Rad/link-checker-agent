import json
from datetime import datetime

def generate_html_report(json_file='link_report.json', html_file='link_report.html'):
    try:
        with open(json_file, 'r') as f:
            report = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_file} not found!")
        return
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Link Report - {report['domain']}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 40px 20px; }}
.container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }}
header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
header p {{ font-size: 1.1em; opacity: 0.9; }}
.content {{ padding: 40px; }}
.meta {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 30px; }}
.meta p {{ margin: 5px 0; color: #333; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 30px 0; }}
.stat {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
.stat-num {{ font-size: 2.5em; font-weight: bold; }}
.stat-label {{ font-size: 0.9em; opacity: 0.9; margin-top: 5px; }}
h2 {{ color: #333; margin-top: 40px; margin-bottom: 15px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
th {{ background: #f0f0f0; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #667eea; }}
td {{ padding: 10px 12px; border-bottom: 1px solid #ddd; }}
tr:hover {{ background: #f9f9f9; }}
code {{ background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
.empty {{ text-align: center; color: #999; padding: 30px; font-style: italic; }}
.badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; }}
.badge-404 {{ background: #f8d7da; color: #721c24; }}
.badge-5xx {{ background: #fff3cd; color: #856404; }}
footer {{ background: #f0f0f0; padding: 20px; text-align: center; color: #666; border-top: 1px solid #ddd; }}
</style>
</head>
<body>
<div class="container">
<header>
<h1>🔗 Link Checker Report</h1>
<p>{report['site_url']}</p>
</header>

<div class="content">
<div class="meta">
<p><strong>Domain:</strong> {report['domain']}</p>
<p><strong>Scanned:</strong> {report['timestamp']}</p>
</div>

<div class="stats">
<div class="stat">
<div class="stat-num">{report['summary']['total_pages_scanned']}</div>
<div class="stat-label">Pages Scanned</div>
</div>
<div class="stat">
<div class="stat-num">{report['summary']['total_unique_links']}</div>
<div class="stat-label">Total Links</div>
</div>
<div class="stat">
<div class="stat-num">{report['summary']['active_links']}</div>
<div class="stat-label">Active Links</div>
</div>
<div class="stat">
<div class="stat-num">{report['summary']['broken_links']}</div>
<div class="stat-label">Broken (404)</div>
</div>
<div class="stat">
<div class="stat-num">{report['summary']['inactive_links']}</div>
<div class="stat-label">Inactive</div>
</div>
<div class="stat">
<div class="stat-num">{report['summary']['error_links']}</div>
<div class="stat-label">Errors</div>
</div>
</div>

<h2>❌ Broken Links (404)</h2>
{('<table><tr><th>URL</th><th>Status</th><th>Found On</th><th>Count</th></tr>' + ''.join([f'<tr><td><code>{link["url"]}</code></td><td><span class="badge badge-404">{link["status"]}</span></td><td>{link["found_on_pages"][0] if link["found_on_pages"] else "N/A"}</td><td>{link["total_occurrences"]}</td></tr>' for link in report['broken_links']]) + '</table>') if report['broken_links'] else '<p class="empty">✓ No broken links found!</p>'}

<h2>⚠️ Inactive Links (4xx/5xx)</h2>
{('<table><tr><th>URL</th><th>Status</th><th>Found On</th><th>Count</th></tr>' + ''.join([f'<tr><td><code>{link["url"]}</code></td><td><span class="badge badge-5xx">{link["status"]}</span></td><td>{link["found_on_pages"][0] if link["found_on_pages"] else "N/A"}</td><td>{link["total_occurrences"]}</td></tr>' for link in report['inactive_links']]) + '</table>') if report['inactive_links'] else '<p class="empty">✓ No inactive links found!</p>'}

<h2>🔴 Error Links</h2>
{('<table><tr><th>URL</th><th>Error</th></tr>' + ''.join([f'<tr><td><code>{link["url"]}</code></td><td>{link.get("error", "Unknown")}</td></tr>' for link in report['error_links']]) + '</table>') if report['error_links'] else '<p class="empty">✓ No errors found!</p>'}

<h2>✅ Sample Active Links</h2>
{('<table><tr><th>URL</th><th>Count</th></tr>' + ''.join([f'<tr><td><code>{link["url"]}</code></td><td>{link["total_occurrences"]}</td></tr>' for link in report['active_links_sample']]) + '</table>') if report['active_links_sample'] else '<p class="empty">No active links in this report.</p>'}
</div>

<footer>
<p>Generated by Link Checker Agent | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</footer>
</div>
</body>
</html>
"""
    
    with open(html_file, 'w') as f:
        f.write(html)
    
    print(f"✅ HTML report generated: {html_file}")
    print(f"   Open in browser: open {html_file}")

if __name__ == "__main__":
    generate_html_report()
