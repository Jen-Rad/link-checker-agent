#!/usr/bin/env python3
"""
Web Scraping Agent for Link Validation
Crawls a website and generates a report on broken/inactive links
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import defaultdict
import json
from pathlib import Path
from bs4 import BeautifulSoup
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinkCheckerAgent:
    def __init__(self, base_url, max_retries=3, timeout=10, max_concurrent=5):
        """
        Initialize the link checker agent
        
        Args:
            base_url: The starting URL to crawl
            max_retries: Number of retries for failed requests
            timeout: Request timeout in seconds
            max_concurrent: Maximum concurrent requests
        """
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_retries = max_retries
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        
        # Track visited pages and links
        self.visited_pages = set()
        self.to_visit = {base_url}
        self.all_links = defaultdict(lambda: {"status": None, "pages": [], "error": None})
        self.pages_scanned = 0
        self.session = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def fetch_page(self, url):
        """Fetch a page with retry logic"""
        async with self.semaphore:
            for attempt in range(self.max_retries):
                try:
                    async with self.session.get(url, timeout=self.timeout, allow_redirects=True) as response:
                        if response.status == 200:
                            return await response.text()
                        else:
                            return None
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout on {url} (attempt {attempt + 1}/{self.max_retries})")
                    if attempt == self.max_retries - 1:
                        return None
                except Exception as e:
                    logger.warning(f"Error fetching {url}: {e}")
                    if attempt == self.max_retries - 1:
                        return None
                await asyncio.sleep(0.5)
        return None

    async def check_link_status(self, url):
        """Check if a link is active"""
        async with self.semaphore:
            for attempt in range(self.max_retries):
                try:
                    async with self.session.head(url, timeout=self.timeout, allow_redirects=True) as response:
                        return response.status
                except asyncio.TimeoutError:
                    if attempt == self.max_retries - 1:
                        return 408  # Request timeout status
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        return None
                await asyncio.sleep(0.5)
        return None

    def extract_links(self, page_url, html_content):
        """Extract all links from a page"""
        links = {"internal": [], "external": []}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for tag in soup.find_all(['a', 'link', 'script', 'img']):
                href = tag.get('href') or tag.get('src')
                if not href:
                    continue
                
                # Skip certain links
                if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                    continue
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(page_url, href)
                
                # Categorize links
                if urlparse(absolute_url).netloc == self.domain:
                    links["internal"].append(absolute_url)
                else:
                    links["external"].append(absolute_url)
        
        except Exception as e:
            logger.error(f"Error parsing {page_url}: {e}")
        
        return links

    async def crawl_page(self, url):
        """Crawl a single page"""
        if url in self.visited_pages:
            return
        
        logger.info(f"Crawling: {url}")
        self.visited_pages.add(url)
        self.pages_scanned += 1
        
        # Fetch the page
        html = await self.fetch_page(url)
        if not html:
            logger.warning(f"Could not fetch {url}")
            return
        
        # Extract links
        links = self.extract_links(url, html)
        
        # Track all links found on this page
        for link in links["internal"] + links["external"]:
            self.all_links[link]["pages"].append(url)
        
        # Add internal links to crawl queue
        for internal_link in links["internal"]:
            if internal_link not in self.visited_pages and len(self.visited_pages) < 1000:  # Limit crawl
                self.to_visit.add(internal_link)

    async def crawl_site(self):
        """Crawl the entire site"""
        logger.info(f"Starting crawl of {self.base_url}")
        
        connector = aiohttp.TCPConnector(limit_per_host=self.max_concurrent)
        async with aiohttp.ClientSession(connector=connector) as session:
            self.session = session
            
            while self.to_visit:
                url = self.to_visit.pop()
                if url not in self.visited_pages:
                    await self.crawl_page(url)
                
                # Progress update
                if self.pages_scanned % 10 == 0:
                    logger.info(f"Progress: {self.pages_scanned} pages scanned, {len(self.all_links)} unique links found")
        
        logger.info(f"Crawl complete: {self.pages_scanned} pages, {len(self.all_links)} unique links")

    async def check_all_links(self):
        """Check the status of all discovered links"""
        logger.info(f"Checking status of {len(self.all_links)} links...")
        
        connector = aiohttp.TCPConnector(limit_per_host=self.max_concurrent)
        async with aiohttp.ClientSession(connector=connector) as session:
            self.session = session
            
            tasks = []
            for link in self.all_links.keys():
                tasks.append(self._check_link_with_tracking(link))
            
            # Process in batches
            for i in range(0, len(tasks), self.max_concurrent):
                batch = tasks[i:i + self.max_concurrent]
                await asyncio.gather(*batch)
                
                if i % (self.max_concurrent * 5) == 0:
                    logger.info(f"Status check progress: {i}/{len(tasks)} links checked")
        
        logger.info("Link status check complete")

    async def _check_link_with_tracking(self, link):
        """Check link status and track result"""
        try:
            status = await self.check_link_status(link)
            self.all_links[link]["status"] = status
        except Exception as e:
            self.all_links[link]["error"] = str(e)

    def generate_report(self, output_file="link_report.json"):
        """Generate a comprehensive report of broken links"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "site_url": self.base_url,
            "domain": self.domain,
            "summary": {
                "total_pages_scanned": self.pages_scanned,
                "total_unique_links": len(self.all_links),
                "broken_links": 0,
                "inactive_links": 0,
                "active_links": 0,
                "error_links": 0,
                "unchecked_links": 0,
            },
            "broken_links": [],
            "inactive_links": [],
            "error_links": [],
            "active_links_sample": [],  # Sample of working links
        }
        
        for link, data in self.all_links.items():
            status = data["status"]
            pages = data["pages"]
            
            link_info = {
                "url": link,
                "status": status,
                "found_on_pages": pages[:5],  # Limit to first 5 pages
                "total_occurrences": len(pages),
            }
            
            if status is None:
                report["summary"]["error_links"] += 1
                link_info["error"] = data.get("error", "Unknown error")
                report["error_links"].append(link_info)
            elif status == 404:
                report["summary"]["broken_links"] += 1
                report["broken_links"].append(link_info)
            elif status >= 400:
                report["summary"]["inactive_links"] += 1
                report["inactive_links"].append(link_info)
            elif status == 200:
                report["summary"]["active_links"] += 1
                if len(report["active_links_sample"]) < 20:
                    report["active_links_sample"].append(link_info)
            else:
                report["summary"]["unchecked_links"] += 1
        
        # Sort by occurrences
        report["broken_links"].sort(key=lambda x: x["total_occurrences"], reverse=True)
        report["inactive_links"].sort(key=lambda x: x["total_occurrences"], reverse=True)
        report["error_links"].sort(key=lambda x: x["total_occurrences"], reverse=True)
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {output_file}")
        return report

    def print_report_summary(self, report):
        """Print a summary of the report"""
        summary = report["summary"]
        
        print("\n" + "="*60)
        print("LINK CHECK REPORT SUMMARY")
        print("="*60)
        print(f"Site: {report['site_url']}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"\nPages Scanned: {summary['total_pages_scanned']}")
        print(f"Total Unique Links: {summary['total_unique_links']}")
        print(f"\nResults:")
        print(f"  ✓ Active Links: {summary['active_links']}")
        print(f"  ✗ Broken Links (404): {summary['broken_links']}")
        print(f"  ⚠ Inactive Links (4xx/5xx): {summary['inactive_links']}")
        print(f"  ⚠ Error/Unchecked: {summary['error_links'] + summary['unchecked_links']}")
        
        if report["broken_links"]:
            print(f"\nTop Broken Links:")
            for link in report["broken_links"][:5]:
                print(f"  - {link['url']}")
                print(f"    Status: {link['status']}, Found on {link['total_occurrences']} pages")
        
        if report["inactive_links"]:
            print(f"\nTop Inactive Links:")
            for link in report["inactive_links"][:5]:
                print(f"  - {link['url']}")
                print(f"    Status: {link['status']}, Found on {link['total_occurrences']} pages")
        
        print("\n" + "="*60 + "\n")


async def main():
    """Main execution"""
    # Example usage - change this to your target site
    target_url = input("Enter the website URL to scan (e.g., https://example.com): ").strip()
    
    if not target_url.startswith('http'):
        target_url = 'https://' + target_url
    
    agent = LinkCheckerAgent(target_url)
    
    # Step 1: Crawl the site
    print(f"\nStarting link checker for: {target_url}")
    await agent.crawl_site()
    
    # Step 2: Check all links
    await agent.check_all_links()
    
    # Step 3: Generate report
    report = agent.generate_report()
    agent.print_report_summary(report)


if __name__ == "__main__":
    asyncio.run(main()) EOF
cat > requirements.txt << 'EOF'
aiohttp==3.9.1
beautifulsoup4==4.12.2
python-dotenv==1.0.0
